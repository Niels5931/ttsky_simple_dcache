import pyuvm
from pyuvm import uvm_component, uvm_factory

from ..cl_tt_um_dcache_base_test import cl_tt_um_dcache_base_test
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..vseqs.cl_tt_um_dcache_raw_vseq import cl_tt_um_dcache_raw_vseq


@pyuvm.test()
class cl_tt_um_dcache_raw_test(cl_tt_um_dcache_base_test):
    """Read-after-Write (RAW) test for tt_um_dcache.

    Tests write-through and read-hit behavior:
    1. WRITE addr 0x00 with data 0x55 -> Writes to memory and cache
    2. READ addr 0x00 -> Should HIT and return 0x05 (low nibble of 0x55)
    
    Verifies that write data is properly stored in cache and subsequent
    reads return cached data without requiring memory access.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_raw_test", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def build_phase(self):
        uvm_factory().set_type_override_by_type(cl_tt_um_dcache_base_vseq, cl_tt_um_dcache_raw_vseq)
        super().build_phase()
