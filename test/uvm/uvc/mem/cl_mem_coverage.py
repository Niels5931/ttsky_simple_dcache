"""MEM Coverage Subscriber

Collects functional coverage from memory transactions using vsc covergroups.
"""

import vsc
from pyuvm import uvm_subscriber, uvm_component, ConfigDB

from .cl_mem_seq_item import cl_mem_seq_item
from .cl_mem_types import MemOp


@vsc.covergroup
class cl_mem_cg:
    """Memory Transaction Coverage Group"""
    
    def __init__(self):
        self.with_sample(
            op=vsc.bit_t(1),
            addr=vsc.bit_t(8),
        )
        
        # Coverpoint: Operation type (READ=0 vs WRITE=1)
        self.cp_op = vsc.coverpoint(self.op, bins={
            "READ": vsc.bin(0),
            "WRITE": vsc.bin(1),
        })
        
        # Coverpoint: Address - focus on lower 4 bits (useful for small tests)
        # Full 8-bit address range can be bucketed
        self.cp_addr_lo = vsc.coverpoint(self.addr & 0x0F, bins={
            f"ADDR_{i:02x}": vsc.bin(i) for i in range(16)
        })
        
        self.cp_addr_hi = vsc.coverpoint((self.addr >> 4) & 0x0F, bins={
            f"ADDR_HI_{i:x}": vsc.bin(i) for i in range(16)
        })
        
        # Cross: Operation vs Address lower nibble
        self.cross_op_addr = vsc.cross([self.cp_op, self.cp_addr_lo])


class cl_mem_coverage(uvm_subscriber):
    """
    MEM Coverage Subscriber
    
    Subscribes to memory monitor analysis port and samples coverage
    for each transaction received.
    """
    
    def __init__(self, name: str = "cl_mem_coverage", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.cg: cl_mem_cg | None = None
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
            self.cg = cl_mem_cg()
            self.logger.info("MEM coverage enabled")
        else:
            self.logger.warning("MEM coverage disabled")
    
    def write(self, item: cl_mem_seq_item):
        """
        Called by analysis port when a transaction is written.
        Samples coverage for the received transaction.
        """
        if not self.enabled or self.cg is None:
            return
        
        # Convert enum to integer (READ=0, WRITE=1)
        op_val = 0 if item.op == MemOp.READ else 1
        
        # vsc covergroups use positional arguments with with_sample
        self.cg.sample(op_val, int(item.addr))
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
        self.logger.info("MEM Coverage Report")
        self.logger.info(f"{'='*60}")
        self.logger.info(f"Total samples: {self.sample_count}")
        self.logger.info(f"Coverage: {cov_pct:.2f}%")
        self.logger.info(f"{'='*60}")
        
        # Detailed coverpoint coverage
        if self.cg is not None:
            self.logger.info("\nCoverpoint Coverage:")
            self.logger.info(f"  cp_op:         {self.cg.cp_op.get_coverage():.2f}%")
            self.logger.info(f"  cp_addr_lo:    {self.cg.cp_addr_lo.get_coverage():.2f}%")
            self.logger.info(f"  cp_addr_hi:    {self.cg.cp_addr_hi.get_coverage():.2f}%")
            self.logger.info(f"  cross_op_addr: {self.cg.cross_op_addr.get_coverage():.2f}%")
