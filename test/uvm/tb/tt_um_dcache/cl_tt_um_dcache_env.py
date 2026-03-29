from pyuvm import uvm_env, uvm_component, uvm_fatal, ConfigDB

from ...uvc.pyuvm_clkuvc import cl_clk_agent
from ...uvc.pyuvm_rstuvc import cl_rst_agent
from ...uvc.cpu import cl_cpu_agent
from ...uvc.mem import cl_mem_agent
from .cl_tt_um_dcache_cfg import cl_tt_um_dcache_cfg
from .cl_tt_um_dcache_vseqr import cl_tt_um_dcache_vseqr
from .cl_tt_um_dcache_sb import cl_tt_um_dcache_sb


class cl_tt_um_dcache_env(uvm_env):
    """Environment for tt_um_dcache testbench.

    Integrates clock, reset, CPU master, memory slave agents, and scoreboard.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_env", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.clk_agent: cl_clk_agent | None = None
        self.rst_agent: cl_rst_agent | None = None
        self.vseqr: cl_tt_um_dcache_vseqr | None = None
        self.cpu_agent: cl_cpu_agent | None = None
        self.mem_agent: cl_mem_agent | None = None
        self.sb: cl_tt_um_dcache_sb | None = None
        self.tb_cfg: cl_tt_um_dcache_cfg | None = None

    def build_phase(self):
        super().build_phase()

        self.tb_cfg = ConfigDB().get(self, "", "tb_cfg")
        if self.tb_cfg is None:
            uvm_fatal("TT_UM_DCACHE_ENV", "Could not retrieve tb_cfg from ConfigDB")

        ConfigDB().set(self, "clk_agent", "clk_cfg", self.tb_cfg.clk_cfg)
        self.clk_agent = cl_clk_agent.create("clk_agent", self)

        ConfigDB().set(self, "rst_agent", "rst_cfg", self.tb_cfg.rst_cfg)
        self.rst_agent = cl_rst_agent.create("rst_agent", self)

        ConfigDB().set(self, "cpu_agent", "cpu_cfg", self.tb_cfg.cpu_master_cfg)
        self.cpu_agent = cl_cpu_agent.create("cpu_agent", self)

        ConfigDB().set(self, "mem_agent", "mem_cfg", self.tb_cfg.mem_slave_cfg)
        self.mem_agent = cl_mem_agent.create("mem_agent", self)

        self.vseqr = cl_tt_um_dcache_vseqr.create("vseqr", self)

        if self.tb_cfg.scoreboard_enabled:
            self.sb = cl_tt_um_dcache_sb.create("sb", self)

    def connect_phase(self):
        super().connect_phase()
        self.vseqr.cpu_vseqr = self.cpu_agent.sequencer
        self.vseqr.mem_vseqr = self.mem_agent.sequencer
        if self.tb_cfg.scoreboard_enabled:
            self.cpu_agent.monitor.ap.connect(self.sb.cpu_fifo.analysis_export)
            self.mem_agent.monitor.ap.connect(self.sb.mem_fifo.analysis_export)
