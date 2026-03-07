import vsc
from pyuvm import uvm_sequence_item
from .cl_cpu_types import CpuOp


@vsc.randobj
class cl_cpu_seq_item(uvm_sequence_item):

    def __init__(self, name: str = "cl_cpu_seq_item"):
        super().__init__(name)
        self.addr = vsc.rand_bit_t(5)
        self.op = vsc.rand_enum_t(CpuOp)
        self.data = vsc.rand_bit_t(8)
        self.resp_valid = 0

    @vsc.constraint
    def addr_c(self):
        self.addr >= 0
        self.addr <= 31

    @vsc.constraint
    def data_c(self):
        self.data >= 0
        self.data <= 255

    def copy(self) -> "cl_cpu_seq_item":
        """Create a copy of this sequence item."""
        item = cl_cpu_seq_item(self.get_name())
        item.addr = self.addr
        item.op = self.op
        item.data = self.data
        item.resp_valid = self.resp_valid
        return item

    def __str__(self) -> str:
        op_str = "READ" if self.op == CpuOp.READ else "WRITE"
        return f"cl_cpu_seq_item({op_str}, addr=0x{self.addr:02x}, data=0x{self.data:02x}, resp_valid={self.resp_valid})"
