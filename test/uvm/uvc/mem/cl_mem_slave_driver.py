import cocotb
from cocotb.triggers import RisingEdge, First

from pyuvm import uvm_component
from .cl_mem_base_driver import cl_mem_base_driver
from .cl_mem_seq_item import cl_mem_seq_item


class cl_mem_slave_driver(cl_mem_base_driver):
    """Slave driver that responds to memory requests from the cache.

    The memory FSM in project.v communicates via uio pins:
    - MEM_IDLE: Waiting for AHB transfer (htrans[1])
    - MEM_DRIVE: Outputs uio_out = 0x69, uio_oe = 0xFF, hready = 0
    - MEM_SAMPLE: Inputs from uio_in as hrdata, hready = 1

    This driver acts as a slave that:
    1. Monitors uio_out and uio_oe for the 0x69 handshake
    2. Drives response data on uio_in when the design releases the bus (uio_oe = 0x00)
    """

    HANDSHAKE_PATTERN = 0x69

    def __init__(self, name: str = "cl_mem_slave_driver", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def drive_reset(self):
        """Drive reset state on uio_in."""
        self.cfg.vif.uio_in.value = 0

    async def drive_item(self, req: cl_mem_seq_item, rsp: cl_mem_seq_item) -> None:
        """Wait for memory handshake and drive response data.

        Args:
            req: Request sequence item with data to respond with
            rsp: Response sequence item to populate with transaction info
        """

        while True:
            await RisingEdge(self.cfg.vif.clk)
            try:
                uio_oe_val = self.cfg.vif.uio_oe.value.to_unsigned()
                uio_out_val = self.cfg.vif.uio_out.value.to_unsigned()
                self.logger.debug(f"Polling handshake: uio_oe=0x{uio_oe_val:02x} uio_out=0x{uio_out_val:02x}")

                if uio_oe_val == 0xFF and uio_out_val == self.HANDSHAKE_PATTERN:
                    break
            except ValueError:
                pass

        self.cfg.vif.uio_in.value = req.data
        self.logger.info(f"Driving response: uio_in=0x{req.data:02x}")
        await RisingEdge(self.cfg.vif.clk)

        self.cfg.vif.uio_in.value = 0

    async def driver_loop(self) -> None:
        """Main driver loop - wait for sequence items and respond to handshakes."""
        while True:
            try:
                if int(self.cfg.vif.rst_n.value) != 0:
                    break
            except ValueError:
                pass
            await RisingEdge(self.cfg.vif.clk)
        self.reset_event.clear()
        self.logger.debug("driver_loop: Reset deasserted, ready for items")

        while True:
            seq_item: cl_mem_seq_item = await self.seq_item_port.get_next_item()
            rsp_item: cl_mem_seq_item = seq_item.copy()
            self.logger.info(f"driver_loop: Got item {seq_item}")

            drive_task = cocotb.start_soon(self.drive_item(seq_item, rsp_item))
            await First(drive_task, self.reset_event.wait())

            if self.reset_event.is_set():
                drive_task.cancel()
                self.logger.warning(f"driver_loop: Item interrupted by reset: {seq_item}")
                self.seq_item_port.item_done()
                return

            self.logger.info(f"Finished response: {rsp_item}")
            self.seq_item_port.item_done()
            self.seq_item_port.put_response(rsp_item)

    async def handle_reset(self) -> None:
        """Handle reset - monitor for reset assertion and reset bus."""
        while True:
            try:
                if int(self.cfg.vif.rst_n.value) == 0:
                    break
            except ValueError:
                pass
            await RisingEdge(self.cfg.vif.clk)

        self.logger.info("Resetting slave bus")
        self.reset_event.set()
        self.drive_reset()

        while True:
            try:
                if int(self.cfg.vif.rst_n.value) != 0:
                    break
            except ValueError:
                pass
            await RisingEdge(self.cfg.vif.clk)
