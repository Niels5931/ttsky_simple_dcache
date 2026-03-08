from pyuvm import uvm_sequencer, uvm_component


class cl_tt_um_dcache_vseqr(uvm_sequencer):
    """Virtual sequencer for tt_um_dcache testbench.

    Holds references to CPU master and memory slave agent sequencers.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_vseqr", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.cpu_vseqr: uvm_sequencer | None = None
        self.mem_vseqr: uvm_sequencer | None = None
