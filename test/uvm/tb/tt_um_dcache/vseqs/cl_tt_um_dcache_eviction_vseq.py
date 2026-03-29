import cocotb

from ....uvc.cpu import cl_cpu_seq_item, cl_cpu_base_seq, CpuOp
from ....uvc.mem import cl_mem_seq_item, cl_mem_base_seq, MemOp
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..cl_tt_um_dcache_vseqr import cl_tt_um_dcache_vseqr


class cl_tt_um_dcache_eviction_vseq(cl_tt_um_dcache_base_vseq):
    """Cache eviction test virtual sequence.

    Tests cache line eviction with direct-mapped cache:
    - Addresses 0x00, 0x08, 0x10, 0x18 all map to cache index 0
    - But have different tags: 0x00>>3=0, 0x08>>3=1, 0x10>>3=2, 0x18>>3=3
    
    Scenario:
    1. READ 0x00 -> MISS (cache empty), loads line with tag 0
    2. READ 0x08 -> MISS (tag mismatch), evicts 0x00, loads tag 1
    3. READ 0x10 -> MISS (tag mismatch), evicts 0x08, loads tag 2
    4. READ 0x18 -> MISS (tag mismatch), evicts 0x10, loads tag 3
    
    All 4 reads require memory access since they conflict on same index.
    """

    def __init__(self, name: str = "cl_tt_um_dcache_eviction_vseq"):
        super().__init__(name)

    async def body(self):
        await super().body()

        vseqr: cl_tt_um_dcache_vseqr = self.sequencer

        # CPU reads: all to index 0, different tags
        cpu_reads = [
            (0x00, 0xA0),  # tag=0, index=0
            (0x08, 0xA1),  # tag=1, index=0 (same index, different tag)
            (0x10, 0xA2),  # tag=2, index=0
            (0x18, 0xA3),  # tag=3, index=0
        ]

        # All 4 reads miss and need memory responses
        mem_responses = [
            (0x00, 0xA0),
            (0x08, 0xA1),
            (0x10, 0xA2),
            (0x18, 0xA3),
        ]

        # Start memory responses in parallel
        mem_tasks = []
        for addr, data in mem_responses:
            item = cl_mem_seq_item("mem_item")
            item.op = MemOp.READ
            item.addr = addr
            item.data = data
            seq = cl_mem_base_seq("mem_seq")
            seq.seq_item = item
            mem_tasks.append(cocotb.start_soon(seq.start(vseqr.mem_vseqr)))

        # Execute CPU reads sequentially (each will miss and wait for memory)
        for addr, expected_data in cpu_reads:
            item = cl_cpu_seq_item("cpu_item")
            item.op = CpuOp.READ
            item.addr = addr
            item.data = expected_data & 0x0F  # Low nibble
            item.nibble_sel = 0
            seq = cl_cpu_base_seq("cpu_seq")
            seq.seq_item = item
            await seq.start(vseqr.cpu_vseqr)

        # Wait for all memory tasks
        for task in mem_tasks:
            await task
