from pyuvm import uvm_sequencer, uvm_component


class cl_mem_b2b_vseqr(uvm_sequencer):
    """Virtual sequencer for mem b2b testbench.

    Holds references to master and slave agent sequencers.
    """

    def __init__(self, name: str = "cl_mem_b2b_vseqr", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.m_vseqr: uvm_sequencer | None = None
        self.s_vseqr: uvm_sequencer | None = None


