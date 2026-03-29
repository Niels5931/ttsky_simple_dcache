import cocotb

from ....uvc.cpu import cl_cpu_seq_item, cl_cpu_base_seq, CpuOp
from ....uvc.mem import cl_mem_seq_item, cl_mem_base_seq, MemOp
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..cl_tt_um_dcache_vseqr import cl_tt_um_dcache_vseqr


class cl_tt_um_dcache_raw_vseq(cl_tt_um_dcache_base_vseq):
    """Read-after-Write (RAW) test virtual sequence.

    Tests write-through and read-hit behavior:
    1. WRITE addr 0x00 with data 0x55 -> Writes to memory and cache
    2. READ addr 0x00 -> Should HIT and return 0x55 (no memory access)
    
    This verifies that:
    - Write data is properly stored in cache
    - Subsequent read returns cached data without memory access
    - Write-through behavior works correctly
    """

    def __init__(self, name: str = "cl_tt_um_dcache_raw_vseq"):
        super().__init__(name)

    async def body(self):
        await super().body()

        vseqr: cl_tt_um_dcache_vseqr = self.sequencer

        # Step 1: Write 0x55 to address 0x00
        # Memory needs to be ready to receive the write
        cpu_write = cl_cpu_seq_item("cpu_write")
        cpu_write.op = CpuOp.WRITE
        cpu_write.addr = 0x00
        cpu_write.data = 0x55
        cpu_write.nibble_sel = 0

        mem_write = cl_mem_seq_item("mem_write")
        mem_write.op = MemOp.WRITE
        mem_write.addr = 0x00
        mem_write.data = 0x55

        cpu_seq_write = cl_cpu_base_seq("cpu_seq_write")
        cpu_seq_write.seq_item = cpu_write

        mem_seq_write = cl_mem_base_seq("mem_seq_write")
        mem_seq_write.seq_item = mem_write

        # Run write transaction
        cpu_task_write = cocotb.start_soon(cpu_seq_write.start(vseqr.cpu_vseqr))
        mem_task_write = cocotb.start_soon(mem_seq_write.start(vseqr.mem_vseqr))
        await cpu_task_write
        await mem_task_write

        # Step 2: Read from same address 0x00
        # This should hit in cache and return 0x55
        cpu_read = cl_cpu_seq_item("cpu_read")
        cpu_read.op = CpuOp.READ
        cpu_read.addr = 0x00
        cpu_read.data = 0x05  # Expect low nibble (0x55 & 0x0F = 0x05)
        cpu_read.nibble_sel = 0

        cpu_seq_read = cl_cpu_base_seq("cpu_seq_read")
        cpu_seq_read.seq_item = cpu_read

        # For read hit, no memory transaction needed
        cpu_task_read = cocotb.start_soon(cpu_seq_read.start(vseqr.cpu_vseqr))
        await cpu_task_read
