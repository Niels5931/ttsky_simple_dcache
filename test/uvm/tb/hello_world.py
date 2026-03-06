import cocotb
import pyuvm
from cocotb.triggers import Timer
from pyuvm import ConfigDB, uvm_fatal

from uvm.uvc.cpu.cl_cpu_types import cl_cpu_if
from uvm.uvc.pyuvm_clkuvc import cl_clk_base_seq
from uvm.uvc.pyuvm_rstuvc import cl_rst_polarity, cl_rst_apply_seq, cl_rst_release_seq
from uvm.tb.cl_dcache_b2b_cfg import cl_dcache_b2b_cfg
from uvm.tb.cl_dcache_b2b_base_test import cl_dcache_b2b_base_test


@pyuvm.test()
class hello_world(cl_dcache_b2b_base_test):
    """Simple test that verifies clock and reset initialization."""

    def build_phase(self):
        # Create testbench config
        tb_cfg = cl_dcache_b2b_cfg("tb_cfg")

        # Create and configure CPU interface with DUT signals
        cpu_vif = cl_cpu_if()
        cpu_vif.clk = cocotb.top.clk
        cpu_vif.rst_n = cocotb.top.rst_n
        tb_cfg.cpu_cfg.vif = cpu_vif

        # Configure clock using interface signals
        tb_cfg.clk_cfg.set_num_clks(1)
        tb_cfg.clk_cfg.set_clk_signals([cpu_vif.clk])
        tb_cfg.clk_cfg.set_clk_periods([10])  # 10ns period (100MHz)

        # Configure reset using interface signals
        tb_cfg.rst_cfg.set_rst_signals([cpu_vif.rst_n])
        tb_cfg.rst_cfg.set_polarity(cl_rst_polarity.ACTIVE_LOW)

        # Set tb_cfg in ConfigDB before parent build_phase
        ConfigDB().set(self, "", "tb_cfg", tb_cfg)

        super().build_phase()

    async def run_phase(self):
        self.raise_objection()

        # Initialize DUT inputs
        cocotb.top.ena.value = 1
        cocotb.top.ui_in.value = 0
        cocotb.top.uio_in.value = 0

        # Start clock via cl_clk_base_seq
        clk_seq = cl_clk_base_seq("clk_seq")
        await clk_seq.start(self.env.clk_agent.sequencer)

        # Apply reset via cl_rst_apply_seq
        apply_rst_seq = cl_rst_apply_seq("apply_rst_seq")
        await apply_rst_seq.start(self.env.rst_agent.sequencer)

        # Verify reset is asserted (active low, so should be 0)
        await Timer(1, unit="ns")
        if cocotb.top.rst_n.value != 0:
            uvm_fatal("HELLO_WORLD", f"Reset not asserted! rst_n = {cocotb.top.rst_n.value}")
        self.logger.info(f"Reset asserted: rst_n = {cocotb.top.rst_n.value}")

        # Hold reset for 10 clock cycles (100ns at 10ns period)
        await Timer(99, unit="ns")

        # Release reset via cl_rst_release_seq
        release_rst_seq = cl_rst_release_seq("release_rst_seq")
        await release_rst_seq.start(self.env.rst_agent.sequencer)

        # Verify reset is released (active low, so should be 1)
        await Timer(1, unit="ns")
        if cocotb.top.rst_n.value != 1:
            uvm_fatal("HELLO_WORLD", f"Reset not released! rst_n = {cocotb.top.rst_n.value}")
        self.logger.info(f"Reset released: rst_n = {cocotb.top.rst_n.value}")

        # Call test_body() for derived test behavior
        await self.test_body()

        self.drop_objection()

    async def test_body(self):
        self.logger.info("Hello World from UVM test_body!")

        # Wait a few clock cycles to verify simulation runs
        await Timer(50, unit="ns")

        self.logger.info("Hello World test completed successfully!")
