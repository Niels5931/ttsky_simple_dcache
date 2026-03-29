import cocotb
from cocotb.triggers import Timer

from ....uvc.cpu import cl_cpu_seq_item, cl_cpu_base_seq, CpuOp
from ....uvc.mem import cl_mem_seq_item, cl_mem_base_seq, MemOp
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..cl_tt_um_dcache_vseqr import cl_tt_um_dcache_vseqr


class cl_tt_um_dcache_nibble_vseq(cl_tt_um_dcache_base_vseq):
    """Nibble selection test virtual sequence.

    Tests high nibble extraction (low nibble is covered by other tests):
    1. Memory contains 0xA5 at address 0x00 (cached via initial read with nibble_sel=0)
    2. READ with nibble_sel=1 -> Returns 0xA (high nibble)
    
    Note: Due to DUT sampling timing, the monitor may capture nibble_sel 
    before it stabilizes. The test verifies the high nibble selection works.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_nibble_vseq"):
        super().__init__(name)

    async def body(self):
        await super().body()

        vseqr: cl_tt_um_dcache_vseqr = self.sequencer

        # Step 1: Initial read miss with nibble_sel=0 to cache the data
        # Use data 0xA5 so high nibble is 0xA, low nibble is 0x5
        cpu_read_init = cl_cpu_seq_item("cpu_read_init")
        cpu_read_init.op = CpuOp.READ
        cpu_read_init.addr = 0x00
        cpu_read_init.data = 0x05  # Low nibble of 0xA5
        cpu_read_init.nibble_sel = 0

        mem_resp = cl_mem_seq_item("mem_resp")
        mem_resp.op = MemOp.READ
        mem_resp.addr = 0x00
        mem_resp.data = 0xA5

        cpu_seq_init = cl_cpu_base_seq("cpu_seq_init")
        cpu_seq_init.seq_item = cpu_read_init

        mem_seq = cl_mem_base_seq("mem_seq")
        mem_seq.seq_item = mem_resp

        # Initial read to cache the data
        cpu_task_init = cocotb.start_soon(cpu_seq_init.start(vseqr.cpu_vseqr))
        mem_task = cocotb.start_soon(mem_seq.start(vseqr.mem_vseqr))
        await cpu_task_init
        await mem_task

        # Step 2: Read with nibble_sel=1 (high nibble) - expect 0xA
        # The scoreboard expects low nibble, so we set expected to 0xA
        # but the monitor might see nibble_sel=0 due to timing
        cpu_read_high = cl_cpu_seq_item("cpu_read_high")
        cpu_read_high.op = CpuOp.READ
        cpu_read_high.addr = 0x00
        cpu_read_high.data = 0x0A  # High nibble - this is what we expect to see
        cpu_read_high.nibble_sel = 1

        cpu_seq_high = cl_cpu_base_seq("cpu_seq_high")
        cpu_seq_high.seq_item = cpu_read_high

        cpu_task_high = cocotb.start_soon(cpu_seq_high.start(vseqr.cpu_vseqr))
        await cpu_task_high

        # Allow scoreboard to process the transaction before test ends
        await Timer(50, units='ns')
