from pyuvm import uvm_sequence
from .cl_mem_seq_item import cl_mem_seq_item
from .cl_mem_types import MemOp


class cl_mem_base_seq(uvm_sequence):

    def __init__(self, name: str = "cl_mem_base_seq"):
        super().__init__(name)
        self.seq_item: cl_mem_seq_item | None = None

    async def body(self):
        await super().body()
        if self.seq_item is None:
            self.seq_item = cl_mem_seq_item("seq_item")
            self.seq_item.randomize()
        await self.start_item(self.seq_item)
        await self.finish_item(self.seq_item)
