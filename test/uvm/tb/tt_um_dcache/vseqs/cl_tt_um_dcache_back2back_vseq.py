import cocotb

from ....uvc.cpu import cl_cpu_seq_item, cl_cpu_base_seq, CpuOp
from ....uvc.mem import cl_mem_seq_item, cl_mem_base_seq, MemOp
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..cl_tt_um_dcache_vseqr import cl_tt_um_dcache_vseqr


class cl_tt_um_dcache_back2back_vseq(cl_tt_um_dcache_base_vseq):
    """Back-to-back stress test virtual sequence.

    Stress tests the cache with rapid consecutive transactions:
    8 consecutive READ operations to different addresses with minimal gaps.
    Uses addresses that map to different cache indices to maximize hit rate.
    
    Addresses: 0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07
    All map to indices 0-7, same tag (0)
    """

    def __init__(self, name: str = "cl_tt_um_dcache_back2back_vseq"):
        super().__init__(name)
        self.num_transactions = 8

    async def body(self):
        await super().body()

        vseqr: cl_tt_um_dcache_vseqr = self.sequencer

        # Prepare CPU reads to consecutive addresses
        cpu_reads = []
        mem_responses = []
        
        for i in range(self.num_transactions):
            addr = i  # 0x00 to 0x07
            data = 0xA0 | (i & 0x0F)  # 0xA0, 0xA1, ..., 0xA7
            cpu_reads.append((addr, data & 0x0F))  # Store expected low nibble
            mem_responses.append((addr, data))

        # Start all memory responses in parallel
        mem_tasks = []
        for addr, data in mem_responses:
            item = cl_mem_seq_item("mem_item")
            item.op = MemOp.READ
            item.addr = addr
            item.data = data
            seq = cl_mem_base_seq("mem_seq")
            seq.seq_item = item
            mem_tasks.append(cocotb.start_soon(seq.start(vseqr.mem_vseqr)))

        # Execute CPU reads back-to-back as fast as possible
        cpu_tasks = []
        for addr, expected_data in cpu_reads:
            item = cl_cpu_seq_item("cpu_item")
            item.op = CpuOp.READ
            item.addr = addr
            item.data = expected_data
            item.nibble_sel = 0
            seq = cl_cpu_base_seq("cpu_seq")
            seq.seq_item = item
            cpu_tasks.append(cocotb.start_soon(seq.start(vseqr.cpu_vseqr)))

        # Wait for all CPU tasks
        for task in cpu_tasks:
            await task

        # Wait for all memory tasks
        for task in mem_tasks:
            await task
