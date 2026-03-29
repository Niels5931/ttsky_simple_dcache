"""CPU Coverage Subscriber

Collects functional coverage from CPU transactions using vsc covergroups.
"""

import vsc
from pyuvm import uvm_subscriber, uvm_component, ConfigDB

from .cl_cpu_seq_item import cl_cpu_seq_item
from .cl_cpu_types import CpuOp


@vsc.covergroup
class cl_cpu_cg:
    """CPU Transaction Coverage Group"""
    
    def __init__(self):
        self.with_sample(
            op=vsc.bit_t(1),
            addr=vsc.bit_t(5),
            nibble_sel=vsc.bit_t(1),
        )
        
        # Coverpoint: Operation type (READ=0 vs WRITE=1)
        self.cp_op = vsc.coverpoint(self.op, bins={
            "READ": vsc.bin(0),
            "WRITE": vsc.bin(1),
        })
        
        # Coverpoint: Address - focus on cache index (lower 3 bits) and tag
        # 5-bit address: [4:3] = tag (2 bits), [2:0] = index (3 bits)
        self.cp_addr_idx = vsc.coverpoint(self.addr & 0x07, bins={
            f"IDX_{i}": vsc.bin(i) for i in range(8)
        })
        
        self.cp_addr_tag = vsc.coverpoint((self.addr >> 3) & 0x03, bins={
            f"TAG_{i}": vsc.bin(i) for i in range(4)
        })
        
        # Coverpoint: Nibble selection
        self.cp_nibble = vsc.coverpoint(self.nibble_sel, bins={
            "LOW_NIBBLE": vsc.bin(0),
            "HIGH_NIBBLE": vsc.bin(1),
        })
        
        # Cross: Operation vs Cache Index
        self.cross_op_idx = vsc.cross([self.cp_op, self.cp_addr_idx])
        
        # Cross: Operation vs Tag
        self.cross_op_tag = vsc.cross([self.cp_op, self.cp_addr_tag])


class cl_cpu_coverage(uvm_subscriber):
    """
    CPU Coverage Subscriber
    
    Subscribes to CPU monitor analysis port and samples coverage
    for each transaction received.
    """
    
    def __init__(self, name: str = "cl_cpu_coverage", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.cg: cl_cpu_cg | None = None
        self.sample_count: int = 0
        self.enabled: bool = True
    
    def build_phase(self):
        super().build_phase()
        
        # Check if coverage is disabled via config
        try:
            enabled_cfg = ConfigDB().get(self, "", "coverage_enabled")
            if enabled_cfg is not None:
                self.enabled = enabled_cfg
        except:
            pass  # Default is enabled
        
        if self.enabled:
            self.cg = cl_cpu_cg()
            self.logger.info("CPU coverage enabled")
        else:
            self.logger.warning("CPU coverage disabled")
    
    def write(self, item: cl_cpu_seq_item):
        """
        Called by analysis port when a transaction is written.
        Samples coverage for the received transaction.
        """
        if not self.enabled or self.cg is None:
            return
        
        # Convert enum to integer (READ=0, WRITE=1)
        op_val = 0 if item.op == CpuOp.READ else 1
        
        # vsc covergroups use positional arguments with with_sample
        self.cg.sample(op_val, int(item.addr), int(item.nibble_sel))
        self.sample_count += 1
    
    def get_coverage(self) -> float:
        """Get current coverage percentage."""
        if self.cg is None:
            return 0.0
        return self.cg.get_coverage()
    
    def report_phase(self):
        """Report coverage statistics at end of simulation."""
        if not self.enabled:
            return
        
        cov_pct = self.get_coverage()
        self.logger.info(f"{'='*60}")
        self.logger.info("CPU Coverage Report")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Total samples: {self.sample_count}")
        self.logger.info(f"Coverage: {cov_pct:.2f}%")
        self.logger.info(f"{'='*60}")
        
        # Detailed coverpoint coverage
        if self.cg is not None:
            self.logger.info("\nCoverpoint Coverage:")
            self.logger.info(f"  cp_op:        {self.cg.cp_op.get_coverage():.2f}%")
            self.logger.info(f"  cp_addr_idx:  {self.cg.cp_addr_idx.get_coverage():.2f}%")
            self.logger.info(f"  cp_addr_tag:  {self.cg.cp_addr_tag.get_coverage():.2f}%")
            self.logger.info(f"  cp_nibble:    {self.cg.cp_nibble.get_coverage():.2f}%")
            self.logger.info(f"  cross_op_idx: {self.cg.cross_op_idx.get_coverage():.2f}%")
            self.logger.info(f"  cross_op_tag: {self.cg.cross_op_tag.get_coverage():.2f}%")
