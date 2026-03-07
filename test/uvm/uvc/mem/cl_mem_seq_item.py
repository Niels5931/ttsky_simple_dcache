import vsc
from pyuvm import uvm_sequence_item
from .cl_mem_types import MemOp


@vsc.randobj
class cl_mem_seq_item(uvm_sequence_item):

    def __init__(self, name: str = "cl_mem_seq_item"):
        super().__init__(name)
        self.addr = vsc.rand_bit_t(8)
        self.op = vsc.rand_enum_t(MemOp)
        self.data = vsc.rand_bit_t(8)

    @vsc.constraint
    def addr_c(self):
        self.addr >= 0
        self.addr <= 255

    @vsc.constraint
    def data_c(self):
        self.data >= 0
        self.data <= 255

    def copy(self) -> "cl_mem_seq_item":
        """Create a copy of this sequence item."""
        item = cl_mem_seq_item(self.get_name())
        item.addr = self.addr
        item.op = self.op
        item.data = self.data
        return item

    def __str__(self) -> str:
        return (f"addr=0x{self.addr:02x} op={self.op.name} "
                f"data=0x{self.data:02x}")
