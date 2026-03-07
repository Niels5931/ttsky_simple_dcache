from pyuvm import uvm_active_passive_enum, uvm_object
from .cl_mem_types import MEM_IF_PARAMS, MemAgentMode, cl_mem_if


class cl_mem_config(uvm_object):

    def __init__(self, name: str = "cl_mem_config"):
        super().__init__(name)
        self.is_active: uvm_active_passive_enum = uvm_active_passive_enum.UVM_ACTIVE
        self.agent_mode: MemAgentMode | None = None
        self.params: MEM_IF_PARAMS = MEM_IF_PARAMS()
        self.vif: cl_mem_if | None = None

    def set_params(self, params: MEM_IF_PARAMS) -> None:
        """Set interface parameters."""
        self.params = params
