from pyuvm import uvm_object

from ....uvc.pyuvm_clkuvc import cl_clk_config
from ....uvc.pyuvm_rstuvc import cl_rst_config
from ....uvc.cpu import cl_cpu_config, CpuAgentMode


class cl_cpu_b2b_cfg(uvm_object):
    """Testbench configuration for CPU b2b tests.

    Contains clock, reset, and CPU (master/slave) configurations.
    """

    def __init__(self, name: str = "cl_cpu_b2b_cfg"):
        super().__init__(name)
        self.clk_cfg: cl_clk_config = cl_clk_config("clk_cfg")
        self.rst_cfg: cl_rst_config = cl_rst_config("rst_cfg")
        self.cpu_master_cfg: cl_cpu_config = cl_cpu_config("cpu_master_cfg")
        self.cpu_master_cfg.agent_mode = CpuAgentMode.MASTER
        self.cpu_slave_cfg: cl_cpu_config = cl_cpu_config("cpu_slave_cfg")
        self.cpu_slave_cfg.agent_mode = CpuAgentMode.SLAVE
