import cocotb
from cocotb.triggers import Timer

from pyuvm import uvm_test, uvm_component, uvm_fatal, ConfigDB

from ....uvc.pyuvm_clkuvc import cl_clk_base_seq, cl_clk_config
from ....uvc.pyuvm_rstuvc import cl_rst_apply_seq, cl_rst_release_seq, cl_rst_polarity
from ....uvc.cpu import cl_cpu_if
from .cl_cpu_b2b_base_seq import cl_cpu_b2b_base_vseq
from .cl_cpu_b2b_env import cl_cpu_b2b_env
from .cl_cpu_b2b_cfg import cl_cpu_b2b_cfg


class cl_cpu_b2b_base_test(uvm_test):
    """Base test for CPU b2b testbench."""

    def __init__(self, name: str = "cl_cpu_b2b_base_test", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.env: cl_cpu_b2b_env | None = None
        self.vseq: cl_cpu_b2b_base_vseq | None = None

    def build_phase(self):
        super().build_phase()

        cpu_if = cl_cpu_if()
        cpu_if.clk = cocotb.top.clk
        cpu_if.rst_n = cocotb.top.rst_n
        cpu_if.ui_in = cocotb.top.ui_in
        cpu_if.uo_out = cocotb.top.uo_out

        tb_cfg = cl_cpu_b2b_cfg("tb_cfg")
        tb_cfg.cpu_master_cfg.vif = cpu_if
        tb_cfg.cpu_slave_cfg.vif = cpu_if
        tb_cfg.clk_cfg.set_num_clks(1)
        tb_cfg.clk_cfg.set_clk_signals([cocotb.top.clk])
        tb_cfg.clk_cfg.set_clk_periods([10])
        tb_cfg.rst_cfg.set_rst_signals([cocotb.top.rst_n])
        tb_cfg.rst_cfg.set_polarity(cl_rst_polarity.ACTIVE_LOW)

        ConfigDB().set(self, "", "tb_cfg", tb_cfg)
        ConfigDB().set(self, "env", "tb_cfg", tb_cfg)

        self.env = cl_cpu_b2b_env.create("env", self)
        self.vseq = cl_cpu_b2b_base_vseq.create("vseq")

    async def run_phase(self):
        self.raise_objection()

        cocotb.top.ena.value = 1
        cocotb.top.ui_in.value = 0
        cocotb.top.uio_in.value = 0

        clk_seq = cl_clk_base_seq("clk_seq")
        await clk_seq.start(self.env.clk_agent.sequencer)

        apply_rst_seq = cl_rst_apply_seq("apply_rst_seq")
        await apply_rst_seq.start(self.env.rst_agent.sequencer)

        await Timer(100, unit="ns")

        release_rst_seq = cl_rst_release_seq("release_rst_seq")
        await release_rst_seq.start(self.env.rst_agent.sequencer)

        await self.test_body()

        self.drop_objection()

    async def test_body(self):
        await self.vseq.start(self.env.vseqr)
