import cocotb
from cocotb.triggers import RisingEdge, Timer

from pyuvm import uvm_test, uvm_component, uvm_fatal, ConfigDB

from ...uvc.pyuvm_clkuvc import cl_clk_base_seq, cl_clk_config
from ...uvc.pyuvm_rstuvc import cl_rst_apply_seq, cl_rst_release_seq, cl_rst_polarity
from ...uvc.cpu import cl_cpu_if
from ...uvc.mem import cl_mem_if
from .cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from .cl_tt_um_dcache_env import cl_tt_um_dcache_env
from .cl_tt_um_dcache_cfg import cl_tt_um_dcache_cfg


class cl_tt_um_dcache_base_test(uvm_test):
    """Base test for tt_um_dcache testbench."""

    def __init__(self, name: str = "cl_tt_um_dcache_base_test", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.env: cl_tt_um_dcache_env | None = None
        self.vseq: cl_tt_um_dcache_base_vseq | None = None

    def build_phase(self):
        super().build_phase()

        cpu_if = cl_cpu_if()
        cpu_if.clk = cocotb.top.clk
        cpu_if.rst_n = cocotb.top.rst_n
        cpu_if.ui_in = cocotb.top.ui_in
        cpu_if.uo_out = cocotb.top.uo_out

        mem_if = cl_mem_if()
        mem_if.clk = cocotb.top.clk
        mem_if.rst_n = cocotb.top.rst_n
        mem_if.uio_in = cocotb.top.uio_in
        mem_if.uio_out = cocotb.top.uio_out
        mem_if.uio_oe = cocotb.top.uio_oe

        tb_cfg = cl_tt_um_dcache_cfg("tb_cfg")
        tb_cfg.cpu_master_cfg.vif = cpu_if
        tb_cfg.mem_slave_cfg.vif = mem_if
        tb_cfg.clk_cfg.set_num_clks(1)
        tb_cfg.clk_cfg.set_clk_signals([cocotb.top.clk])
        tb_cfg.clk_cfg.set_clk_periods([20])
        tb_cfg.rst_cfg.set_rst_signals([cocotb.top.rst_n])
        tb_cfg.rst_cfg.set_polarity(cl_rst_polarity.ACTIVE_LOW)

        ConfigDB().set(self, "", "tb_cfg", tb_cfg)
        ConfigDB().set(self, "env", "tb_cfg", tb_cfg)

        self.env = cl_tt_um_dcache_env.create("env", self)
        self.vseq = cl_tt_um_dcache_base_vseq.create("vseq")

    async def run_phase(self):
        self.raise_objection()

        clk_seq = cl_clk_base_seq("clk_seq")
        await clk_seq.start(self.env.clk_agent.sequencer)

        apply_rst_seq = cl_rst_apply_seq("apply_rst_seq")
        await apply_rst_seq.start(self.env.rst_agent.sequencer)

        await Timer(100, unit="ns")

        release_rst_seq = cl_rst_release_seq("release_rst_seq")
        await release_rst_seq.start(self.env.rst_agent.sequencer)

        await RisingEdge(cocotb.top.clk)

        self.logger.info("Released reset")

        await self.test_body()

        self.drop_objection()

    async def test_body(self):
        await self.vseq.start(self.env.vseqr)
