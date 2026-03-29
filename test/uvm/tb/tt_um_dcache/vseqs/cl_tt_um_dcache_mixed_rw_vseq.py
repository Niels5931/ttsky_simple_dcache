import cocotb

from ....uvc.cpu import cl_cpu_seq_item, cl_cpu_base_seq, CpuOp
from ....uvc.mem import cl_mem_seq_item, cl_mem_base_seq, MemOp
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..cl_tt_um_dcache_vseqr import cl_tt_um_dcache_vseqr


class cl_tt_um_dcache_mixed_rw_vseq(cl_tt_um_dcache_base_vseq):
    """Mixed random read/write test virtual sequence.

    Tests random mixture of read and write operations:
    10 iterations of random operation type, address, and data.
    This provides broader coverage of cache state transitions.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_mixed_rw_vseq"):
        super().__init__(name)
        self.num_iterations = 10

    async def body(self):
        await super().body()
        vseqr: cl_tt_um_dcache_vseqr = self.sequencer

        for i in range(self.num_iterations):
            # Create random CPU item
            cpu_item = cl_cpu_seq_item(f"cpu_item_{i}")
            cpu_item.randomize()
            # Ensure nibble_sel is 0 or 1
            cpu_item.nibble_sel = i % 2

            # Create corresponding memory item
            mem_item = cl_mem_seq_item(f"mem_item_{i}")
            mem_item.addr = int(cpu_item.addr)
            if cpu_item.op == CpuOp.READ:
                mem_item.op = MemOp.READ
                # Memory data should match what CPU expects
                mem_item.data = (int(cpu_item.data) << 4) | int(cpu_item.data)
            else:
                mem_item.op = MemOp.WRITE
                mem_item.data = int(cpu_item.data)

            cpu_task = cocotb.start_soon(self.cpu_fork(vseqr, cpu_item))
            mem_task = cocotb.start_soon(self.mem_fork(vseqr, mem_item))
            await cpu_task

    async def cpu_fork(self, vseqr, cpu_item):
        cpu_seq = cl_cpu_base_seq(f"cpu_seq_{cpu_item.get_name()}")
        cpu_seq.seq_item = cpu_item
        await cpu_seq.start(vseqr.cpu_vseqr)

    async def mem_fork(self, vseqr, mem_item):
        mem_seq = cl_mem_base_seq(f"mem_seq_{mem_item.get_name()}")
        mem_seq.seq_item = mem_item
        await mem_seq.start(vseqr.mem_vseqr)
