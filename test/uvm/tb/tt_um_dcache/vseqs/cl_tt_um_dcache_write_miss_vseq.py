import cocotb

from pyuvm import uvm_sequence
from ....uvc.cpu import cl_cpu_seq_item, cl_cpu_base_seq, CpuOp
from ....uvc.mem import cl_mem_seq_item, cl_mem_base_seq, MemOp
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..cl_tt_um_dcache_vseqr import cl_tt_um_dcache_vseqr


class cl_tt_um_dcache_write_miss_vseq(cl_tt_um_dcache_base_vseq):
    """Write miss test sequence.

    Tests:
    1. WRITE addr 0x00 -> MISS (cache empty)
    2. WRITE addr 0x00 -> HIT (write-through)
    3. WRITE addr 0x08 -> MISS (conflict)
    4. WRITE addr 0x08 -> HIT
    """

    def __init__(self, name: str = "cl_tt_um_dcache_write_miss_vseq"):
        super().__init__(name)

    async def body(self):
        await super().body()
        vseqr: cl_tt_um_dcache_vseqr = self.sequencer

        cpu_writes = [
            (0x00, 0xA5),
            (0x00, 0xA5),
            (0x08, 0xB5),
            (0x08, 0xB5),
        ]

        mem_writes = [
            (0x00, 0xA5),
            (0x08, 0xB5),
        ]

        mem_tasks = []
        for addr, data in mem_writes:
            mem_item = cl_mem_seq_item("mem_item")
            mem_item.op = MemOp.WRITE
            mem_item.addr = addr
            mem_item.data = data
            mem_seq = cl_mem_base_seq("mem_seq")
            mem_seq.seq_item = mem_item
            mem_tasks.append(cocotb.start_soon(mem_seq.start(vseqr.mem_vseqr)))

        cpu_tasks = []
        for addr, data in cpu_writes:
            cpu_item = cl_cpu_seq_item("cpu_item")
            cpu_item.op = CpuOp.WRITE
            cpu_item.addr = addr
            cpu_item.data = data
            cpu_seq = cl_cpu_base_seq("cpu_seq")
            cpu_seq.seq_item = cpu_item
            cpu_tasks.append(cocotb.start_soon(cpu_seq.start(vseqr.cpu_vseqr)))

        for task in cpu_tasks:
            await task
