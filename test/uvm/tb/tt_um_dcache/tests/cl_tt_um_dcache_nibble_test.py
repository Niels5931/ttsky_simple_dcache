import pyuvm
from pyuvm import uvm_component, uvm_factory

from ..cl_tt_um_dcache_base_test import cl_tt_um_dcache_base_test
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..vseqs.cl_tt_um_dcache_nibble_vseq import cl_tt_um_dcache_nibble_vseq


@pyuvm.test()
class cl_tt_um_dcache_nibble_test(cl_tt_um_dcache_base_test):
    """Nibble selection test for tt_um_dcache.

    Tests high and low nibble extraction:
    1. Memory contains 0xA5 at address 0x00 (cached via initial read)
    2. READ with nibble_sel=0 -> Returns 0x5 (low nibble)
    3. READ with nibble_sel=1 -> Returns 0xA (high nibble)
    
    Verifies the nibble selection logic works correctly for both
    low nibble (bits [3:0]) and high nibble (bits [7:4]) access.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_nibble_test", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def build_phase(self):
        uvm_factory().set_type_override_by_type(cl_tt_um_dcache_base_vseq, cl_tt_um_dcache_nibble_vseq)
        super().build_phase()
