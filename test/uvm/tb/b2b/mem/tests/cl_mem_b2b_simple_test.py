import pyuvm
from pyuvm import uvm_component, uvm_factory

from ..cl_mem_b2b_base_test import cl_mem_b2b_base_test
from ..cl_mem_b2b_base_seq import cl_mem_b2b_base_vseq
from ..vseqs.cl_mem_b2b_simple_vseq import cl_mem_b2b_simple_vseq


@pyuvm.test()
class cl_mem_b2b_simple_test(cl_mem_b2b_base_test):
    """Simple test for mem b2b testbench.

    Runs a simple virtual sequence that performs a basic memory transaction
    between master and slave agents using factory override to substitute
    the base virtual sequence with the simple variant.
    """

    def __init__(self, name: str = "cl_mem_b2b_simple_test", parent: uvm_component | None = None):
        super().__init__(name, parent)

    def build_phase(self):
        # Set factory override before calling base build_phase
        uvm_factory().set_type_override_by_type(cl_mem_b2b_base_vseq, cl_mem_b2b_simple_vseq)
        super().build_phase()
