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
    Uses FIFO ordering for memory responses since the memory interface
    doesn't carry address information.
    
    Key insight: Memory requests are processed sequentially by the DUT,
    so memory responses arrive in the same order as CPU requests.
    
    Timing consideration: Memory responses may arrive before CPU reads
    are processed by the monitor. We buffer memory responses until the
    corresponding CPU read arrives.
    """

    NUM_CACHE_LINES = 8

    def __init__(self, name: str = "cl_tt_um_dcache_sb", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.cpu_fifo: uvm_tlm_analysis_fifo | None = None
        self.mem_fifo: uvm_tlm_analysis_fifo | None = None
        self.tag_mem: dict[int, int] = {}
        self.data_mem: dict[int, int] = {}
        self.valid_mem: dict[int, bool] = {}
        self.pending_misses: list = []
        self.buffered_mem_responses: list = []
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

    def process_buffered_responses(self) -> None:
        """Process any buffered memory responses that now have matching pending misses."""
        while self.pending_misses and self.buffered_mem_responses:
            pending = self.pending_misses.pop(0)
            mem_resp = self.buffered_mem_responses.pop(0)
            
            addr = pending["addr"]
            tag = pending["tag"]
            index = pending["index"]
            nibble_sel = pending["nibble_sel"]
            data = mem_resp["data"]
            
            self.data_mem[index] = data
            self.tag_mem[index] = tag
            self.valid_mem[index] = True
            
            self.logger.info(f"  -> REFILL: addr=0x{addr:02x} -> cache[{index}] with data=0x{data:02x}")

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
            else:
                self.logger.info(f"  -> CACHE MISS: addr=0x{item.addr:02x}, expecting memory response")
                self.pending_misses.append({
                    "addr": item.addr,
                    "tag": tag,
                    "index": index,
                    "nibble_sel": nibble_sel,
                })
                self.process_buffered_responses()
        elif item.op.name == "WRITE":
            self.data_mem[index] = item.data
            self.tag_mem[index] = tag
            self.valid_mem[index] = True
            self.logger.info(f"  -> WRITE: stored data=0x{item.data:02x}")

    def handle_mem_transaction(self, item) -> None:
        """Process memory response using FIFO ordering.

        Memory monitor doesn't capture address, so we use FIFO ordering:
        - First pending miss gets first memory response
        - If no pending miss, buffer the response for later processing

        Args:
            item: Memory sequence item with data (addr is ignored)
        """
        data = item.data
        self.logger.info(f"SB MEM RESP data=0x{data:02x}")

        self.buffered_mem_responses.append({"data": data})
        self.process_buffered_responses()

    async def cpu_monitor_loop(self) -> None:
        """Monitor CPU fifo for transactions."""
        self.logger.info("CPU monitor loop started")
        while not self.stop_event:
            try:
                item = await self.cpu_fifo.get()
                self.raise_objection()
                self.handle_cpu_transaction(item)
                self.drop_objection()
            except Exception as e:
                if not self.stop_event:
                    self.logger.error(f"CPU monitor error: {e}")
                try:
                    self.drop_objection()
                except:
                    pass
        self.logger.info("CPU monitor loop stopped")

    async def mem_monitor_loop(self) -> None:
        """Monitor memory fifo for responses."""
        self.logger.info("MEM monitor loop started")
        while not self.stop_event:
            try:
                item = await self.mem_fifo.get()
                self.raise_objection()
                self.handle_mem_transaction(item)
                self.drop_objection()
            except Exception as e:
                if not self.stop_event:
                    self.logger.error(f"MEM monitor error: {e}")
        self.logger.info("MEM monitor loop stopped")

    async def run_phase(self) -> None:
        await super().run_phase()
        self.logger.info("Scoreboard run_phase started")
        self.cpu_task = cocotb.start_soon(self.cpu_monitor_loop())
        self.mem_task = cocotb.start_soon(self.mem_monitor_loop())

    def report_phase(self) -> None:
        """Called at end of test to report results."""
        self.stop_event = True
        if self.cpu_task:
            self.cpu_task.cancel()
        if self.mem_task:
            self.mem_task.cancel()
        self.logger.info(f"Scoreboard Results: {self.errors} errors, {self.matches} matches")
        if self.pending_misses:
            self.logger.warning(f"  -> {len(self.pending_misses)} pending misses still in queue")
        if self.buffered_mem_responses:
            self.logger.warning(f"  -> {len(self.buffered_mem_responses)} buffered memory responses still in queue")

    def check_phase(self) -> None:
        """Called by UVM to check results at end of test."""
        if self.errors > 0:
            uvm_error("SCOREBOARD", f"Found {self.errors} mismatches during test")
            self.logger.error(f"Check phase failed: {self.errors} errors detected")
        else:
            self.logger.info(f"Check phase passed: {self.matches} matches")
