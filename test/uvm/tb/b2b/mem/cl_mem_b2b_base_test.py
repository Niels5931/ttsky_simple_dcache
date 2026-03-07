import cocotb
from cocotb.triggers import Timer

from pyuvm import uvm_test, uvm_component, uvm_fatal, ConfigDB

from ....uvc.pyuvm_clkuvc import cl_clk_base_seq, cl_clk_config
from ....uvc.pyuvm_rstuvc import cl_rst_apply_seq, cl_rst_release_seq, cl_rst_polarity
from ....uvc.mem import cl_mem_if
from .cl_mem_b2b_base_seq import cl_mem_b2b_base_vseq
from .cl_mem_b2b_env import cl_mem_b2b_env
from .cl_mem_b2b_cfg import cl_mem_b2b_cfg


class cl_mem_b2b_base_test(uvm_test):
    """Base test for mem b2b testbench.

    Creates memory interface, configures clock and reset agents,
    initializes DUT inputs, starts clock, applies reset, then releases reset.
    Derived tests can override test_body() for test-specific behavior.
    """

    def __init__(self, name: str = "cl_mem_b2b_base_test", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.env: cl_mem_b2b_env | None = None
        self.vseq: cl_mem_b2b_base_vseq | None = None

    def build_phase(self):
        super().build_phase()

        # Create memory interface and connect to DUT signals
        mem_if = cl_mem_if()
        mem_if.uio_out = cocotb.top.uio_out
        mem_if.uio_in = cocotb.top.uio_in
        mem_if.uio_oe = cocotb.top.uio_oe
        mem_if.clk = cocotb.top.clk
        mem_if.rst_n = cocotb.top.rst_n

        # Create and configure testbench config
        tb_cfg = cl_mem_b2b_cfg("tb_cfg")
        tb_cfg.mem_master_cfg.vif = mem_if
        tb_cfg.mem_slave_cfg.vif = mem_if
        tb_cfg.clk_cfg.set_num_clks(1)
        tb_cfg.clk_cfg.set_clk_signals([cocotb.top.clk])
        tb_cfg.clk_cfg.set_clk_periods([10])  # 10ns period (100MHz)
        tb_cfg.rst_cfg.set_rst_signals([cocotb.top.rst_n])
        tb_cfg.rst_cfg.set_polarity(cl_rst_polarity.ACTIVE_LOW)

        # Pass tb_cfg to env
        ConfigDB().set(self, "env", "tb_cfg", tb_cfg)

        # Create environment and virtual sequence
        self.env = cl_mem_b2b_env.create("env", self)
        self.vseq = cl_mem_b2b_base_vseq.create("vseq")

    async def run_phase(self):
        self.raise_objection()

        # Start clock via cl_clk_base_seq
        clk_seq = cl_clk_base_seq("clk_seq")
        await clk_seq.start(self.env.clk_agent.sequencer)

        # Apply reset via cl_rst_apply_seq
        apply_rst_seq = cl_rst_apply_seq("apply_rst_seq")
        await apply_rst_seq.start(self.env.rst_agent.sequencer)

        # Hold reset for 10 clock cycles (100ns at 10ns period)
        await Timer(100, unit="ns")

        # Release reset via cl_rst_release_seq
        release_rst_seq = cl_rst_release_seq("release_rst_seq")
        await release_rst_seq.start(self.env.rst_agent.sequencer)

        # Call test_body() for derived test behavior
        await self.test_body()

        self.drop_objection()

    async def test_body(self):
        await self.vseq.start(self.env.vseqr)
