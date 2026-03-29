import pyuvm
from pyuvm import uvm_component, uvm_factory

from ..cl_tt_um_dcache_base_test import cl_tt_um_dcache_base_test
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..vseqs.cl_tt_um_dcache_back2back_vseq import cl_tt_um_dcache_back2back_vseq


@pyuvm.test()
class cl_tt_um_dcache_back2back_test(cl_tt_um_dcache_base_test):
    """Back-to-back stress test for tt_um_dcache.

    Stress tests the cache with rapid consecutive transactions:
    - 8 consecutive READ operations to addresses 0x00-0x07
    - All addresses map to different cache indices (0-7)
    - Same tag (0) for all addresses
    
    Tests the cache's ability to handle rapid sequential accesses
    and verifies correct data retrieval under stress conditions.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_back2back_test", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def build_phase(self):
        uvm_factory().set_type_override_by_type(cl_tt_um_dcache_base_vseq, cl_tt_um_dcache_back2back_vseq)
        super().build_phase()
