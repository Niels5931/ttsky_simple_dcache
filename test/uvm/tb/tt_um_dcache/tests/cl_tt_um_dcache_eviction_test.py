import pyuvm
from pyuvm import uvm_component, uvm_factory

from ..cl_tt_um_dcache_base_test import cl_tt_um_dcache_base_test
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..vseqs.cl_tt_um_dcache_eviction_vseq import cl_tt_um_dcache_eviction_vseq


@pyuvm.test()
class cl_tt_um_dcache_eviction_test(cl_tt_um_dcache_base_test):
    """Cache eviction test for tt_um_dcache.

    Tests direct-mapped cache line eviction with conflicting addresses:
    - Addresses 0x00, 0x08, 0x10, 0x18 all map to cache index 0
    - But have different tags (0, 1, 2, 3 respectively)
    
    Scenario:
    1. READ 0x00 -> MISS (cache empty), loads line with tag 0
    2. READ 0x08 -> MISS (tag mismatch), evicts 0x00, loads tag 1
    3. READ 0x10 -> MISS (tag mismatch), evicts 0x08, loads tag 2
    4. READ 0x18 -> MISS (tag mismatch), evicts 0x10, loads tag 3
    
    All 4 reads require memory access due to tag conflicts on the same index.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_eviction_test", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def build_phase(self):
        uvm_factory().set_type_override_by_type(cl_tt_um_dcache_base_vseq, cl_tt_um_dcache_eviction_vseq)
        super().build_phase()
