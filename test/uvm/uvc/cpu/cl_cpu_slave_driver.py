import cocotb
from cocotb.triggers import RisingEdge, First

from pyuvm import uvm_component
from .cl_cpu_base_driver import cl_cpu_base_driver
from .cl_cpu_seq_item import cl_cpu_seq_item
from .cl_cpu_types import CpuOp


class cl_cpu_slave_driver(cl_cpu_base_driver):
    """Slave driver that responds to CPU requests from the cache."""

    def __init__(self, name: str = "cl_cpu_slave_driver", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def drive_reset(self):
        self.cfg.vif.uo_out.value = 0
        self.logger.info("drive_reset: uo_out=0")

    async def drive_item(self, req: cl_cpu_seq_item, rsp: cl_cpu_seq_item) -> None:
        self.logger.info("drive_item: Starting, driving req_ready=1")

        uo_val = 1 << 4
        self.cfg.vif.uo_out.value = uo_val
        self.logger.info("drive_item: Asserted req_ready=1, waiting for req_valid")

        while True:
            await RisingEdge(self.cfg.vif.clk)
            ui_val = int(self.cfg.vif.ui_in.value)
            if (ui_val >> 5) & 1:
                self.logger.info("drive_item: Saw req_valid=1")
                break

        await RisingEdge(self.cfg.vif.clk)
        
        # No longer ready
        uo_val &= ~(1 << 4)
        
        # Response valid
        uo_val |= 1 << 5
        uo_val |= req.data & 0xF
        self.cfg.vif.uo_out.value = uo_val
        self.logger.info(f"drive_item: Driving response resp_valid=1 resp_rdata=0x{req.data:02x}")

        await RisingEdge(self.cfg.vif.clk)
        # No longer valid response
        uo_val &= ~(1 << 5)
        # No longer ready
        uo_val &= ~(1 << 4)
        
        self.cfg.vif.uo_out.value = uo_val
        self.logger.info("drive_item: Response complete")

    async def driver_loop(self) -> None:
        while self.cfg.vif.rst_n.value == 0:
            await RisingEdge(self.cfg.vif.clk)
        self.reset_event.clear()
        self.logger.info("driver_loop: Reset deasserted, ready for items")

        while True:
            seq_item: cl_cpu_seq_item = await self.seq_item_port.get_next_item()
            self.logger.info(f"driver_loop: Got seq_item with data=0x{seq_item.data:02x}")
            rsp_item: cl_cpu_seq_item = seq_item.copy()

            drive_task = cocotb.start_soon(self.drive_item(seq_item, rsp_item))
            await First(drive_task, self.reset_event.wait())

            if self.reset_event.is_set():
                drive_task.cancel()
                self.logger.warning(f"driver_loop: Item interrupted by reset: {seq_item}")
                self.seq_item_port.item_done()
                return

            self.logger.info(f"driver_loop: Finished response with data=0x{rsp_item.data:02x}")
            self.seq_item_port.item_done()
            self.seq_item_port.put_response(rsp_item)

    async def handle_reset(self) -> None:
        while self.cfg.vif.rst_n.value == 1:
            await RisingEdge(self.cfg.vif.clk)

        self.logger.info("Resetting slave bus")
        self.reset_event.set()
        await RisingEdge(self.cfg.vif.clk)  # Wait for next cycle's drive phase
        self.drive_reset()

        while self.cfg.vif.rst_n.value == 0:
            await RisingEdge(self.cfg.vif.clk)
