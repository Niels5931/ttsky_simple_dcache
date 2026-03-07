from pyuvm import uvm_sequence
import cocotb

from ..cl_cpu_b2b_base_seq import cl_cpu_b2b_base_vseq
from ..cl_cpu_b2b_virt_seqr import cl_cpu_b2b_vseqr
from uvm.uvc.cpu import cl_cpu_seq_item, cl_cpu_base_seq


class cl_cpu_b2b_simple_vseq(cl_cpu_b2b_base_vseq):
    """Simple virtual sequence for CPU b2b testbench.

    Creates and runs parallel master and slave sequences with the same
    randomized sequence item to test basic CPU transactions.
    """

    def __init__(self, name: str = "cl_cpu_b2b_simple_vseq"):
        super().__init__(name)

    async def body(self):
        await super().body()

        # Get the virtual sequencer - it has m_vseqr and s_vseqr references
        # self.sequencer is the sequencer this vseq was started on (the virtual sequencer)
        vseqr = self.sequencer

        seq_item = cl_cpu_seq_item("seq_item")
        seq_item.randomize()

        master_seq = cl_cpu_base_seq("master_seq")
        #master_seq.seq_item = seq_item.copy()

        slave_seq = cl_cpu_base_seq("slave_seq")
        #slave_seq.seq_item = seq_item.copy()

        master_task = cocotb.start_soon(master_seq.start(vseqr.m_vseqr))
        slave_task = cocotb.start_soon(slave_seq.start(vseqr.s_vseqr))

        await master_task
        await slave_task
