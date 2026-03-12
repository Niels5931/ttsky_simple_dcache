import cocotb

from ....uvc.cpu import cl_cpu_seq_item, cl_cpu_base_seq, CpuOp
from ....uvc.mem import cl_mem_seq_item, cl_mem_base_seq, MemOp
from ..cl_tt_um_dcache_base_seq import cl_tt_um_dcache_base_vseq
from ..cl_tt_um_dcache_vseqr import cl_tt_um_dcache_vseqr


class cl_tt_um_dcache_read_miss_vseq(cl_tt_um_dcache_base_vseq):
    """Cache read miss test sequence.

    Tests the following scenario:
    1. READ addr 0x00 -> MISS (cache empty)
    2. READ addr 0x00 -> HIT (same line cached)
    3. READ addr 0x10 -> MISS (different cache line)
    4. READ addr 0x00 -> HIT (original line still cached)
    """

    def __init__(self, name: str = "cl_tt_um_dcache_read_miss_vseq"):
        super().__init__(name)

    async def body(self):
        await super().body()

        vseqr: cl_tt_um_dcache_vseqr = self.sequencer

        cpu_reads = [
            (0x00, 0xA5),
            (0x00, 0xA5),
            (0x10, 0xB5),
            (0x00, 0xA5),
        ]

        mem_responses = [
            (0x00, 0xA5),
            (0x10, 0xB5),
        ]

        mem_tasks = []
        for addr, data in mem_responses:
            item = cl_mem_seq_item("mem_item")
            item.op = MemOp.READ
            item.addr = addr
            item.data = data
            seq = cl_mem_base_seq("mem_seq")
            seq.seq_item = item
            mem_tasks.append(cocotb.start_soon(seq.start(vseqr.mem_vseqr)))

        cpu_tasks = []
        for addr, expected_data in cpu_reads:
            item = cl_cpu_seq_item("cpu_item")
            item.op = CpuOp.READ
            item.addr = addr
            item.data = expected_data
            seq = cl_cpu_base_seq("cpu_seq")
            seq.seq_item = item
            cpu_tasks.append(cocotb.start_soon(seq.start(vseqr.cpu_vseqr)))

        for task in cpu_tasks:
            await task
