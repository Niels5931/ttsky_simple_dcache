import pyuvm
from pyuvm import uvm_component, uvm_factory

from ..cl_tt_um_dcache_base_test import cl_tt_um_dcache_base_test
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..vseqs.cl_tt_um_dcache_mixed_rw_vseq import cl_tt_um_dcache_mixed_rw_vseq


@pyuvm.test()
class cl_tt_um_dcache_mixed_rw_test(cl_tt_um_dcache_base_test):
    """Mixed random read/write test for tt_um_dcache.

    Tests random mixture of read and write operations:
    - 10 iterations of random operation type (READ/WRITE)
    - Random addresses and data
    - Alternating nibble_sel values (0 and 1)
    
    Provides broad coverage of cache state transitions including:
    - Read misses and hits
    - Write misses and hits
    - Write-through behavior
    - Nibble selection with random data
    """

    def __init__(self, name: str = "cl_tt_um_dcache_mixed_rw_test", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def build_phase(self):
        uvm_factory().set_type_override_by_type(cl_tt_um_dcache_base_vseq, cl_tt_um_dcache_mixed_rw_vseq)
        super().build_phase()
