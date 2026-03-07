from pyuvm import uvm_object

from ....uvc.pyuvm_clkuvc import cl_clk_config
from ....uvc.pyuvm_rstuvc import cl_rst_config
from ....uvc.mem import cl_mem_config, MemAgentMode


class cl_mem_b2b_cfg(uvm_object):
    """Testbench configuration for mem b2b tests.

    Contains clock, reset, and memory (master/slave) configurations.
    """

    def __init__(self, name: str = "cl_mem_b2b_cfg"):
        super().__init__(name)
        self.clk_cfg: cl_clk_config = cl_clk_config("clk_cfg")
        self.rst_cfg: cl_rst_config = cl_rst_config("rst_cfg")
        self.mem_master_cfg: cl_mem_config = cl_mem_config("mem_master_cfg")
        self.mem_master_cfg.agent_mode = MemAgentMode.MASTER
        self.mem_slave_cfg: cl_mem_config = cl_mem_config("mem_slave_cfg")
        self.mem_slave_cfg.agent_mode = MemAgentMode.SLAVE
