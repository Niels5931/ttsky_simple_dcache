from pyuvm import uvm_sequence
from logging import Logger
import cocotb

from ..cl_mem_b2b_base_seq import cl_mem_b2b_base_vseq
from ..cl_mem_b2b_vseqr import cl_mem_b2b_vseqr
from uvm.uvc.mem import cl_mem_seq_item, cl_mem_base_seq


class cl_mem_b2b_simple_vseq(cl_mem_b2b_base_vseq):
    """Simple virtual sequence for mem b2b testbench.

    Creates and runs parallel master and slave sequences with the same
    randomized sequence item to test basic memory transactions.
    """

    def __init__(self, name: str = "cl_mem_b2b_simple_vseq"):
        super().__init__(name)

    async def body(self):
        await super().body()

        vseqr = self.sequencer

        seq_item = cl_mem_seq_item("seq_item")
        seq_item.randomize()

        master_seq = cl_mem_base_seq("master_seq")
        master_seq.seq_item = seq_item.copy()

        slave_seq = cl_mem_base_seq("slave_seq")
        slave_seq.seq_item = seq_item.copy()

        master_task = cocotb.start_soon(master_seq.start(vseqr.m_vseqr))
        slave_task = cocotb.start_soon(slave_seq.start(vseqr.s_vseqr))

        await master_task
        await slave_task
