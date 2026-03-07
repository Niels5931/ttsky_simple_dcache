from enum import Enum, auto
from dataclasses import dataclass


class CpuOp(Enum):
    READ = auto()
    WRITE = auto()


class CpuAgentMode(Enum):
    MASTER = auto()
    SLAVE = auto()


@dataclass
class CPU_IF_PARAMS:
    """Interface parameters matching dcache_ahb_ctrl parameters."""
    word_size: int = 8
    addr_length: int = 8
    response_timeout_cycles: int = 1000


class cl_cpu_if:
    """Virtual interface for Tiny Tapeout CPU signals (TT pins)."""

    def __init__(self):
        self.clk = None
        self.rst_n = None
        self.ui_in = None
        self.uo_out = None
