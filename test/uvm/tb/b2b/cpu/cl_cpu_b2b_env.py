from pyuvm import uvm_env, uvm_component, uvm_fatal, ConfigDB

from ....uvc.pyuvm_clkuvc import cl_clk_agent
from ....uvc.pyuvm_rstuvc import cl_rst_agent
from ....uvc.cpu import cl_cpu_agent
from .cl_cpu_b2b_cfg import cl_cpu_b2b_cfg
from .cl_cpu_b2b_virt_seqr import cl_cpu_b2b_vseqr


class cl_cpu_b2b_env(uvm_env):
    """Environment for CPU b2b testbench.

    Integrates clock, reset, and CPU master/slave agents.
    """

    def __init__(self, name: str = "cl_cpu_b2b_env", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.clk_agent: cl_clk_agent | None = None
        self.rst_agent: cl_rst_agent | None = None
        self.vseqr: cl_cpu_b2b_vseqr | None = None
        self.m_agent: cl_cpu_agent | None = None
        self.s_agent: cl_cpu_agent | None = None
        self.tb_cfg: cl_cpu_b2b_cfg | None = None

    def build_phase(self):
        super().build_phase()

        # Get testbench config from ConfigDB
        self.tb_cfg = ConfigDB().get(self, "", "tb_cfg")
        if self.tb_cfg is None:
            uvm_fatal("CPU_B2B_ENV", "Could not retrieve tb_cfg from ConfigDB")

        # Pass clock config to agent
        ConfigDB().set(self, "clk_agent", "clk_cfg", self.tb_cfg.clk_cfg)
        self.clk_agent = cl_clk_agent.create("clk_agent", self)

        # Pass reset config to agent
        ConfigDB().set(self, "rst_agent", "rst_cfg", self.tb_cfg.rst_cfg)
        self.rst_agent = cl_rst_agent.create("rst_agent", self)

        # Pass CPU configs to agents
        ConfigDB().set(self, "m_agent", "cpu_cfg", self.tb_cfg.cpu_master_cfg)
        self.m_agent = cl_cpu_agent.create("m_agent", self)

        ConfigDB().set(self, "s_agent", "cpu_cfg", self.tb_cfg.cpu_slave_cfg)
        self.s_agent = cl_cpu_agent.create("s_agent", self)

        # Virtual sequencer
        self.vseqr = cl_cpu_b2b_vseqr.create("vseqr", self)

    def connect_phase(self):
        super().connect_phase()
        self.vseqr.m_vseqr = self.m_agent.sequencer
        self.vseqr.s_vseqr = self.s_agent.sequencer
