import pyuvm
from pyuvm import uvm_component, uvm_factory

from ..cl_tt_um_dcache_base_test import cl_tt_um_dcache_base_test
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..vseqs.cl_tt_um_dcache_random_vseq import cl_tt_um_dcache_random_vseq


@pyuvm.test()
class cl_tt_um_dcache_random_test(cl_tt_um_dcache_base_test):
    """Random test using constrained-random sequence items."""

    def __init__(self, name: str = "cl_tt_um_dcache_random_test", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def build_phase(self):
        uvm_factory().set_type_override_by_type(
            cl_tt_um_dcache_base_vseq, 
            cl_tt_um_dcache_random_vseq
        )
        super().build_phase()
