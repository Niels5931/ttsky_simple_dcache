import cocotb

from ....uvc.cpu import cl_cpu_seq_item, cl_cpu_base_seq, CpuOp
from ....uvc.mem import cl_mem_seq_item, cl_mem_base_seq, MemOp
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..cl_tt_um_dcache_vseqr import cl_tt_um_dcache_vseqr


class cl_tt_um_dcache_random_vseq(cl_tt_um_dcache_base_vseq):
    """Random test sequence.

    Uses constrained-random CPU and memory sequence items.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_random_vseq"):
        super().__init__(name)
        self.num_iterations = 4

    async def body(self):
        await super().body()
        vseqr: cl_tt_um_dcache_vseqr = self.sequencer

        for _ in range(self.num_iterations):
            cpu_item = cl_cpu_seq_item("cpu_item")
            with cpu_item.randomize_with():
                cpu_item.op == CpuOp.READ
            
            mem_item = cl_mem_seq_item("mem_item")
            with mem_item.randomize_with():
                mem_item.op == MemOp.READ

            cpu_task = cocotb.start_soon(self.cpu_fork(vseqr, cpu_item))
            mem_task = cocotb.start_soon(self.mem_fork(vseqr, mem_item))
            await cpu_task

    async def cpu_fork(self, vseqr, cpu_item):
        cpu_seq = cl_cpu_base_seq("cpu_seq")
        cpu_seq.seq_item = cpu_item
        await cpu_seq.start(vseqr.cpu_vseqr)

    async def mem_fork(self, vseqr, mem_item):
        mem_seq = cl_mem_base_seq("mem_seq")
        mem_seq.seq_item = mem_item
        await mem_seq.start(vseqr.mem_vseqr)
