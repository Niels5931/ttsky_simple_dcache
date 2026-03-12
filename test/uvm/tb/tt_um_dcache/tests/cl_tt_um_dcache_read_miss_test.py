import pyuvm
from pyuvm import uvm_component, uvm_factory

from ..cl_tt_um_dcache_base_test import cl_tt_um_dcache_base_test
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..vseqs.cl_tt_um_dcache_read_miss_vseq import cl_tt_um_dcache_read_miss_vseq


@pyuvm.test()
class cl_tt_um_dcache_read_miss_test(cl_tt_um_dcache_base_test):
    """Cache miss test.

    Tests cache miss behavior with read operations:
    1. First read to addr 0x00 -> miss (cache empty)
    2. Second read to addr 0x00 -> hit (cached)
    3. Read to addr 0x10 -> miss (different cache line)
    4. Read to addr 0x00 -> hit (original line still cached)
    """

    def __init__(self, name: str = "cl_tt_um_dcache_miss_test", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def build_phase(self):
        uvm_factory().set_type_override_by_type(cl_tt_um_dcache_base_vseq, cl_tt_um_dcache_read_miss_vseq)
        super().build_phase()
