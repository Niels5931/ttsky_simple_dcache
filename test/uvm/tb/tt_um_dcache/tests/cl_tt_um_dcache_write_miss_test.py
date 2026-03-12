import pyuvm
from pyuvm import uvm_component, uvm_factory

from ..cl_tt_um_dcache_base_test import cl_tt_um_dcache_base_test
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..vseqs.cl_tt_um_dcache_write_miss_vseq import cl_tt_um_dcache_write_miss_vseq


@pyuvm.test()
class cl_tt_um_dcache_write_miss_test(cl_tt_um_dcache_base_test):
    """Write miss test.

    Tests cache write miss behavior:
    1. WRITE addr 0x00 -> MISS (cache empty, allocate line)
    2. WRITE addr 0x00 -> HIT (write-through)
    3. WRITE addr 0x08 -> MISS (conflict, evicts line 0)
    4. WRITE addr 0x08 -> HIT (cached at line 0)
    """

    def __init__(self, name: str = "cl_tt_um_dcache_write_miss_test", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def build_phase(self):
        uvm_factory().set_type_override_by_type(cl_tt_um_dcache_base_vseq, cl_tt_um_dcache_write_miss_vseq)
        super().build_phase()
