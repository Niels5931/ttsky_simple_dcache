import cocotb
from cocotb.triggers import RisingEdge, First

from pyuvm import uvm_component
from .cl_mem_base_driver import cl_mem_base_driver
from .cl_mem_seq_item import cl_mem_seq_item


class cl_mem_master_driver(cl_mem_base_driver):
    """Master driver that emulates the DUT's memory FSM on the UIO bus.

    Drives the handshake protocol from the DUT side:
    - MEM_IDLE:   uio_oe = 0x00, uio_out = 0x00 (bus released)
    - MEM_DRIVE:  uio_oe = 0xFF, uio_out = 0x69 (handshake signal)
    - MEM_SAMPLE: uio_oe = 0x00 (release bus, sample uio_in as response)
    """

    HANDSHAKE_PATTERN = 0x69

    def __init__(self, name: str = "cl_mem_master_driver", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def drive_reset(self):
        """Drive idle state on uio_out and uio_oe."""
        self.cfg.vif.uio_out.value = 0
        self.cfg.vif.uio_oe.value = 0

    async def drive_item(self, req: cl_mem_seq_item, rsp: cl_mem_seq_item) -> None:
        """Execute the MEM_DRIVE → MEM_SAMPLE handshake sequence.

        Args:
            req: Request sequence item (data field unused for master)
            rsp: Response sequence item populated with sampled data
        """
        # MEM_DRIVE: assert handshake for 2 cycles so slave can detect it
        self.cfg.vif.uio_oe.value = 0xFF
        self.cfg.vif.uio_out.value = self.HANDSHAKE_PATTERN
        self.logger.info(f"Driving handshake: uio_oe=0xFF, uio_out=0x{self.HANDSHAKE_PATTERN:02x}")
        await RisingEdge(self.cfg.vif.clk)

        # MEM_SAMPLE: release bus, let slave drive uio_in
        self.cfg.vif.uio_oe.value = 0x00
        self.cfg.vif.uio_out.value = 0x00
        rsp.data = self.cfg.vif.uio_in.value.to_unsigned()
        self.logger.info(f"Sampled response: uio_in=0x{rsp.data:02x}")

        await RisingEdge(self.cfg.vif.clk)
        # Sample response from uio_in

        self.drive_reset()

    async def driver_loop(self) -> None:
        """Main driver loop - get sequence items and drive handshakes."""
        while self.cfg.vif.rst_n.value == 0:
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

            self.logger.info(f"Finished transaction: {rsp_item}")
            self.seq_item_port.item_done()
            self.seq_item_port.put_response(rsp_item)

    async def handle_reset(self) -> None:
        """Handle reset - monitor for reset assertion and reset bus."""
        while self.cfg.vif.rst_n.value == 1:
            await RisingEdge(self.cfg.vif.clk)

        self.logger.info("Resetting master bus")
        self.reset_event.set()
        self.drive_reset()

        while self.cfg.vif.rst_n.value == 0:
            await RisingEdge(self.cfg.vif.clk)
