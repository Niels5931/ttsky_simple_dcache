from enum import Enum, auto
from dataclasses import dataclass

class MemOp(Enum):
    READ = auto()
    WRITE = auto()


class MemAgentMode(Enum):
    MASTER = auto()
    SLAVE = auto()


@dataclass
class MEM_IF_PARAMS:
    """Interface parameters for memory agent."""
    word_size: int = 8
    response_timeout_cycles: int = 1000


class cl_mem_if:
    """Virtual interface for memory signals (uio pins)."""

    def __init__(self):
        # UIO interface signals
        self.uio_out = None     # [7:0] Output from DUT
        self.uio_in = None      # [7:0] Input to DUT
        self.uio_oe = None      # [7:0] Output enable from DUT

        # Clock/reset
        self.clk = None
        self.rst_n = None
