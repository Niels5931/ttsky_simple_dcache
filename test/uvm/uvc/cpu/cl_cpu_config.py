from pyuvm import uvm_active_passive_enum, uvm_object
from .cl_cpu_types import CPU_IF_PARAMS, CpuAgentMode, cl_cpu_if


class cl_cpu_config(uvm_object):

    def __init__(self, name: str = "cl_cpu_config"):
        super().__init__(name)
        self.is_active: uvm_active_passive_enum = uvm_active_passive_enum.UVM_ACTIVE
        self.agent_mode: CpuAgentMode | None = None
        self.params: CPU_IF_PARAMS = CPU_IF_PARAMS()
        self.vif: cl_cpu_if | None = None

    def set_params(self, params: CPU_IF_PARAMS) -> None:
        """Set interface parameters."""
        self.params = params
