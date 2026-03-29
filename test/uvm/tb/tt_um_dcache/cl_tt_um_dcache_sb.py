import cocotb
from cocotb.triggers import Timer, RisingEdge

from pyuvm import (
    uvm_scoreboard,
    uvm_tlm_analysis_fifo,
    uvm_component,
    uvm_fatal,
    uvm_object,
    uvm_error,
    ConfigDB,
)


class cl_tt_um_dcache_sb(uvm_scoreboard):
    """Scoreboard for tt_um_dcache testbench.

    Maintains a cache model with tag, data, and valid bits.
    Compares CPU transactions with expected behavior based on
    cache hit/miss detection.
    """

    NUM_CACHE_LINES = 8

    def __init__(self, name: str = "cl_tt_um_dcache_sb", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.cpu_fifo: uvm_tlm_analysis_fifo | None = None
        self.mem_fifo: uvm_tlm_analysis_fifo | None = None
        self.tag_mem: dict[int, int] = {}
        self.data_mem: dict[int, int] = {}
        self.valid_mem: dict[int, bool] = {}
        self.pending_reads: list = []
        self.matches: int = 0
        self.errors: int = 0
        self.cpu_task = None
        self.mem_task = None
        self.stop_event = False

    def build_phase(self):
        super().build_phase()
        self.cpu_fifo = uvm_tlm_analysis_fifo("cpu_fifo", self)
        self.mem_fifo = uvm_tlm_analysis_fifo("mem_fifo", self)
        for i in range(self.NUM_CACHE_LINES):
            self.valid_mem[i] = False

    def check_address(self, addr: int) -> tuple[int, int]:
        """Decode address into tag and index.

        Args:
            addr: 8-bit address

        Returns:
            (tag, index) tuple
        """
        tag = (addr >> 3) & 0x1F
        index = addr & 0x07
        return tag, index

    def handle_cpu_transaction(self, item) -> None:
        """Process CPU transaction and determine expected behavior.

        Args:
            item: CPU sequence item with addr, op, data
        """
        tag, index = self.check_address(item.addr)
        nibble_sel = item.nibble_sel
        self.logger.info(f"SB CPU {item.op.name} addr=0x{item.addr:02x} tag={tag} index={index} nibble_sel={nibble_sel}")

        if item.op.name == "READ":
            if self.valid_mem[index] and self.tag_mem[index] == tag:
                full_data = self.data_mem[index]
                if nibble_sel == 0:
                    expected = full_data & 0xF
                else:
                    expected = (full_data >> 4) & 0xF
                self.logger.info(f"  -> CACHE HIT: expected=0x{expected:02x}, actual=0x{item.data:02x} (full_data=0x{full_data:02x})")
                if expected == item.data:
                    self.matches += 1
                    self.logger.info(f"  -> MATCH!")
                else:
                    self.errors += 1
                    self.logger.error(f"  -> MISMATCH! expected=0x{expected:02x}, actual=0x{item.data:02x}")
                self.pending_reads.append({
                    "addr": item.addr,
                    "expected": expected,
                    "from_cpu": True
                })
            else:
                self.logger.info(f"  -> CACHE MISS: expecting memory response")
                self.pending_reads.append({
                    "addr": item.addr,
                    "nibble_sel": nibble_sel,
                    "expected": None,
                    "from_cpu": True
                })
        elif item.op.name == "WRITE":
            self.data_mem[index] = item.data
            self.tag_mem[index] = tag
            self.valid_mem[index] = True
            self.logger.info(f"  -> WRITE: stored data=0x{item.data:02x}")

    def handle_mem_transaction(self, item) -> None:
        """Process memory response and check against expected.

        Args:
            item: Memory sequence item with addr, data
        """
        self.logger.info(f"SB MEM RESP addr=0x{item.addr:02x} data=0x{item.data:02x}")
        tag, index = self.check_address(item.addr)
        self.data_mem[index] = item.data
        self.tag_mem[index] = tag
        self.valid_mem[index] = True
        self.logger.info(f"  -> REFILL: updated cache[{index}] with mem data=0x{item.data:02x}")
        for pending in self.pending_reads:
            if pending["addr"] == item.addr and pending["expected"] is None:
                nibble_sel = pending.get("nibble_sel", 0)
                if nibble_sel == 0:
                    expected = item.data & 0xF
                else:
                    expected = (item.data >> 4) & 0xF
                pending["expected"] = expected
                self.logger.info(f"  -> Updated pending READ with expected=0x{expected:02x}")
                break

    async def cpu_monitor_loop(self) -> None:
        """Monitor CPU fifo for transactions."""
        self.logger.info("CPU monitor loop started")
        while not self.stop_event:
            try:
                item = await self.cpu_fifo.get()
                self.handle_cpu_transaction(item)
            except Exception as e:
                if not self.stop_event:
                    self.logger.error(f"CPU monitor error: {e}")
        self.logger.info("CPU monitor loop stopped")

    async def mem_monitor_loop(self) -> None:
        """Monitor memory fifo for responses."""
        self.logger.info("MEM monitor loop started")
        while not self.stop_event:
            try:
                item = await self.mem_fifo.get()
                self.handle_mem_transaction(item)
            except Exception as e:
                if not self.stop_event:
                    self.logger.error(f"MEM monitor error: {e}")
        self.logger.info("MEM monitor loop stopped")

    async def run_phase(self) -> None:
        await super().run_phase()
        self.logger.info("Scoreboard run_phase started")
        self.cpu_task = cocotb.start_soon(self.cpu_monitor_loop())
        self.mem_task = cocotb.start_soon(self.mem_monitor_loop())
        self.logger.info(f"Scoreboard complete: {self.errors} errors, {self.matches} matches")

    def report_phase(self) -> None:
        """Called at end of test to report results."""
        self.stop_event = True
        if self.cpu_task:
            self.cpu_task.cancel()
        if self.mem_task:
            self.mem_task.cancel()
        self.logger.info(f"Scoreboard Results: {self.errors} errors, {self.matches} matches")

    def check_phase(self) -> None:
        """Called by UVM to check results at end of test."""
        if self.errors > 0:
            uvm_error("SCOREBOARD", f"Found {self.errors} mismatches during test")
            self.logger.error(f"Check phase failed: {self.errors} errors detected")
        else:
            self.logger.info(f"Check phase passed: {self.matches} matches")
