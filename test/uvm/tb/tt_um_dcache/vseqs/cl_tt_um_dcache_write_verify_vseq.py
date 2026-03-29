import cocotb

from ....uvc.cpu import cl_cpu_seq_item, cl_cpu_base_seq, CpuOp
from ....uvc.mem import cl_mem_seq_item, cl_mem_base_seq, MemOp
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..cl_tt_um_dcache_vseqr import cl_tt_um_dcache_vseqr


class cl_tt_um_dcache_write_verify_vseq(cl_tt_um_dcache_base_vseq):
    """Write-through verification test virtual sequence.

    Verifies that writes propagate to memory correctly:
    1. WRITE addr 0x00 with data 0xAA
    2. Memory receives the write and stores 0xAA
    3. Subsequent READ from 0x00 returns 0xAA (hit in cache)
    
    This tests the write-through behavior and verifies data consistency.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_write_verify_vseq"):
        super().__init__(name)

    async def body(self):
        await super().body()

        vseqr: cl_tt_um_dcache_vseqr = self.sequencer

        test_addr = 0x10
        test_data = 0xAB

        # Step 1: Write data to address
        cpu_write = cl_cpu_seq_item("cpu_write")
        cpu_write.op = CpuOp.WRITE
        cpu_write.addr = test_addr
        cpu_write.data = test_data
        cpu_write.nibble_sel = 0

        mem_write = cl_mem_seq_item("mem_write")
        mem_write.op = MemOp.WRITE
        mem_write.addr = test_addr
        mem_write.data = test_data

        cpu_seq_write = cl_cpu_base_seq("cpu_seq_write")
        cpu_seq_write.seq_item = cpu_write

        mem_seq_write = cl_mem_base_seq("mem_seq_write")
        mem_seq_write.seq_item = mem_write

        # Execute write transaction
        cpu_task_write = cocotb.start_soon(cpu_seq_write.start(vseqr.cpu_vseqr))
        mem_task_write = cocotb.start_soon(mem_seq_write.start(vseqr.mem_vseqr))
        await cpu_task_write
        await mem_task_write

        # Step 2: Read back the data (should hit in cache)
        cpu_read = cl_cpu_seq_item("cpu_read")
        cpu_read.op = CpuOp.READ
        cpu_read.addr = test_addr
        cpu_read.data = test_data & 0x0F  # Low nibble
        cpu_read.nibble_sel = 0

        cpu_seq_read = cl_cpu_base_seq("cpu_seq_read")
        cpu_seq_read.seq_item = cpu_read

        # Read should hit in cache
        await cpu_seq_read.start(vseqr.cpu_vseqr)

        # Step 3: Read again to confirm it's still cached
        cpu_read2 = cl_cpu_seq_item("cpu_read2")
        cpu_read2.op = CpuOp.READ
        cpu_read2.addr = test_addr
        cpu_read2.data = test_data & 0x0F  # Low nibble
        cpu_read2.nibble_sel = 0

        cpu_seq_read2 = cl_cpu_base_seq("cpu_seq_read2")
        cpu_seq_read2.seq_item = cpu_read2

        await cpu_seq_read2.start(vseqr.cpu_vseqr)
