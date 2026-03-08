from pyuvm import uvm_sequence


class cl_tt_um_dcache_base_vseq(uvm_sequence):
    """Base virtual sequence for tt_um_dcache testbench.

    Provides empty body() that derived classes can override.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_base_vseq"):
        super().__init__(name)

    async def body(self):
        pass
