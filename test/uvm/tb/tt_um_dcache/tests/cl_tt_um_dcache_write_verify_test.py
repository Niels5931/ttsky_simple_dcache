import pyuvm
from pyuvm import uvm_component, uvm_factory

from ..cl_tt_um_dcache_base_test import cl_tt_um_dcache_base_test
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..vseqs.cl_tt_um_dcache_write_verify_vseq import cl_tt_um_dcache_write_verify_vseq


@pyuvm.test()
class cl_tt_um_dcache_write_verify_test(cl_tt_um_dcache_base_test):
    """Write-through verification test for tt_um_dcache.

    Verifies that writes propagate to memory correctly:
    1. WRITE addr 0x10 with data 0xAB
    2. Memory receives the write and stores 0xAB
    3. READ from 0x10 returns 0x0B (low nibble, cache hit)
    4. Second READ from 0x10 confirms data remains cached
    
    Tests write-through behavior and verifies data consistency
    between cache and memory.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_write_verify_test", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def build_phase(self):
        uvm_factory().set_type_override_by_type(cl_tt_um_dcache_base_vseq, cl_tt_um_dcache_write_verify_vseq)
        super().build_phase()
