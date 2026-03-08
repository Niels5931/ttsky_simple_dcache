import cocotb

from pyuvm import uvm_sequence
from ....uvc.cpu import cl_cpu_seq_item, cl_cpu_base_seq, CpuOp
from ....uvc.mem import cl_mem_seq_item, cl_mem_base_seq, MemOp
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..cl_tt_um_dcache_vseqr import cl_tt_um_dcache_vseqr


class cl_tt_um_dcache_simple_vseq(cl_tt_um_dcache_base_vseq):
    """Simple virtual sequence for tt_um_dcache testbench.

    Runs parallel CPU master and memory slave sequences to test basic
    cache read/write transactions.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_simple_vseq"):
        super().__init__(name)

    async def body(self):
        await super().body()

        vseqr: cl_tt_um_dcache_vseqr = self.sequencer

        cpu_item = cl_cpu_seq_item("cpu_item")
        cpu_item.op = CpuOp.READ
        cpu_item.addr = 0x00
        cpu_item.data = 0x5

        mem_item = cl_mem_seq_item("mem_item")
        mem_item.op = MemOp.READ
        mem_item.addr = 0x00
        mem_item.data = 0xA5

        cpu_seq = cl_cpu_base_seq("cpu_seq")
        cpu_seq.seq_item = cpu_item

        mem_seq = cl_mem_base_seq("mem_seq")
        mem_seq.seq_item = mem_item

        cpu_task = cocotb.start_soon(cpu_seq.start(vseqr.cpu_vseqr))
        mem_task = cocotb.start_soon(mem_seq.start(vseqr.mem_vseqr))

        await cpu_task
        await mem_task
