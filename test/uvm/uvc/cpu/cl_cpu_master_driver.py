import cocotb
from cocotb.triggers import RisingEdge, First

from pyuvm import uvm_component
from .cl_cpu_base_driver import cl_cpu_base_driver
from .cl_cpu_seq_item import cl_cpu_seq_item
from .cl_cpu_types import CpuOp


class cl_cpu_master_driver(cl_cpu_base_driver):
    """Master driver that initiates CPU requests to the cache."""

    def __init__(self, name: str = "cl_cpu_master_driver", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def drive_reset(self):
        self.cfg.vif.ui_in.value = 0

    async def drive_item(self, req: cl_cpu_seq_item, rsp: cl_cpu_seq_item) -> None:
        self.logger.info(f"drive_item: Starting {req}")

        # Drive ui_in once with request: [addr[4:0], write, valid]
        ui_val = (req.addr & 0x1F) | ((1 if req.op == CpuOp.WRITE else 0) << 6) | (1 << 5)
        self.cfg.vif.ui_in.value = ui_val
        self.logger.info(f"drive_item: Drove request addr=0x{req.addr:02x} op={req.op.name}")

        # Wait for req_ready handshake
        while True:
            await RisingEdge(self.cfg.vif.clk)
            uo_val = int(self.cfg.vif.uo_out.value)
            if (uo_val >> 4) & 1:
                self.logger.info("drive_item: Saw req_ready=1, handshake complete")
                break

        # For READ: sample 4-bit response after handshake
        if req.op == CpuOp.READ:
            while True:
                await RisingEdge(self.cfg.vif.clk)
                uo_val = int(self.cfg.vif.uo_out.value)
                if (uo_val >> 5) & 1:
                    break
            rsp.data = uo_val & 0xF
            self.logger.info(f"drive_item: Sampled resp_rdata=0x{rsp.data:01x}")

        await RisingEdge(self.cfg.vif.clk)  # Wait for next cycle's drive phase
        self.drive_reset()
        self.logger.info(f"drive_item: Complete, rsp={rsp}")

    async def driver_loop(self) -> None:
        while self.cfg.vif.rst_n.value == 0:
            await RisingEdge(self.cfg.vif.clk)
        self.reset_event.clear()
        self.logger.info("driver_loop: Reset deasserted, ready for items")

        while True:
            seq_item: cl_cpu_seq_item = await self.seq_item_port.get_next_item()
            rsp_item: cl_cpu_seq_item = seq_item.copy()
            self.logger.info(f"driver_loop: Got seq_item {seq_item}")

            drive_task = cocotb.start_soon(self.drive_item(seq_item, rsp_item))
            await First(drive_task, self.reset_event.wait())

            if self.reset_event.is_set():
                drive_task.cancel()
                self.logger.warning(f"driver_loop: Item interrupted by reset: {seq_item}")
                self.seq_item_port.item_done()
                return

            self.logger.info(f"driver_loop: Finished item, rsp={rsp_item}")
            self.seq_item_port.item_done()
            self.seq_item_port.put_response(rsp_item)

    async def handle_reset(self) -> None:
        while self.cfg.vif.rst_n.value == 1:
            await RisingEdge(self.cfg.vif.clk)

        self.logger.info("Resetting master bus")
        self.reset_event.set()
        await RisingEdge(self.cfg.vif.clk)  # Wait for next cycle's drive phase
        self.drive_reset()

        while self.cfg.vif.rst_n.value == 0:
            await RisingEdge(self.cfg.vif.clk)
