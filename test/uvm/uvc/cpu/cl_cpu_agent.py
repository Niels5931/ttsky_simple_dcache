from pyuvm import (
    uvm_active_passive_enum,
    uvm_agent,
    uvm_component,
    uvm_fatal,
    uvm_sequencer,
    uvm_analysis_port,
    ConfigDB,
)
from .cl_cpu_base_driver import cl_cpu_base_driver
from .cl_cpu_master_driver import cl_cpu_master_driver
from .cl_cpu_slave_driver import cl_cpu_slave_driver
from .cl_cpu_monitor import cl_cpu_monitor
from .cl_cpu_config import cl_cpu_config
from .cl_cpu_types import CpuAgentMode


class cl_cpu_agent(uvm_agent):

    def __init__(self, name: str = "cl_cpu_agent", parent: uvm_component | None = None):
        super().__init__(name, parent)
        self.sequencer: uvm_sequencer | None = None
        self.driver: cl_cpu_base_driver | None = None
        self.monitor: cl_cpu_monitor | None = None
        self.cfg: cl_cpu_config | None = None
        self.ap: uvm_analysis_port | None = None

    def build_phase(self):
        super().build_phase()
        self.cfg = ConfigDB().get(self, "", "cpu_cfg")
        if self.cfg is None:
            uvm_fatal("CPU_AGENT", "Cannot retrieve config from ConfigDB")

        # Monitor is always present
        ConfigDB().set(self, "monitor", "cfg", self.cfg)
        self.monitor = cl_cpu_monitor.create("monitor", self)
        self.ap = uvm_analysis_port("ap", self)

        # Driver and sequencer only in active mode
        if self.cfg.is_active == uvm_active_passive_enum.UVM_ACTIVE:
            if self.cfg.agent_mode is None:
                uvm_fatal("CPU_AGENT", "agent_mode not set in config")
            self.sequencer = uvm_sequencer.create("sequencer", self)
            ConfigDB().set(self, "driver", "cfg", self.cfg)
            if self.cfg.agent_mode == CpuAgentMode.MASTER:
                self.driver = cl_cpu_master_driver.create("driver", self)
            else:
                self.driver = cl_cpu_slave_driver.create("driver", self)

    def connect_phase(self):
        super().connect_phase()
        # Connect monitor analysis port to agent analysis port
        self.monitor.ap.connect(self.ap)

        # Connect driver to sequencer in active mode
        if self.cfg.is_active == uvm_active_passive_enum.UVM_ACTIVE:
            self.driver.seq_item_port.connect(self.sequencer.seq_item_export)

        self.logger.info("Connect phase complete")
