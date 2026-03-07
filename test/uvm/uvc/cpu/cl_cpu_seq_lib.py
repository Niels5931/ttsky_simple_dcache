import vsc
from pyuvm import uvm_sequence
from .cl_cpu_seq_item import cl_cpu_seq_item
from .cl_cpu_types import CpuOp


class cl_cpu_base_seq(uvm_sequence):

    def __init__(self, name: str = "cl_cpu_base_seq"):
        super().__init__(name)
        self.seq_item: cl_cpu_seq_item | None = None

    async def body(self):
        await super().body()
        if self.seq_item is None:
            self.seq_item = cl_cpu_seq_item("seq_item")
        self.seq_item.randomize()
        await self.start_item(self.seq_item)
        await self.finish_item(self.seq_item)


class cl_cpu_single_read_seq(uvm_sequence):
    """Sequence to perform a single read at a given address."""

    def __init__(self, name: str = "cl_cpu_single_read_seq", addr: int = 0):
        super().__init__(name)
        self.addr = addr
        self.rsp = None

    async def body(self):
        item = cl_cpu_seq_item("read_item")
        with item.randomize_with() as it:
            it.op == CpuOp.READ
            it.addr == self.addr
        await self.start_item(item)
        await self.finish_item(item)
        self.rsp = item


