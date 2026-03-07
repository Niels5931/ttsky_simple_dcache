from pyuvm import uvm_sequence


class cl_cpu_b2b_base_vseq(uvm_sequence):
    """Base virtual sequence for CPU b2b testbench.

    Provides empty body() that derived classes can override.
    Derived classes may call super().body() without side effects.
    """

    def __init__(self, name: str = "cl_cpu_b2b_base_vseq"):
        super().__init__(name)

    async def body(self):
        """Base implementation - does nothing. Override in derived classes."""
        pass
