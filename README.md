# Tiny D-Cache (AHB Controller)

This project implements a miniaturized Data Cache Controller based on the `dcache_ahb_ctrl` core, optimized for the Tiny Tapeout environment.

## Overview

The Tiny D-Cache is a direct-mapped cache designed for 8-bit architectures. It provides a simple request/response interface for a CPU and uses an AHB-Lite master interface to communicate with external memory. For this tapeout, the AHB interface is mapped to the bidirectional `uio` pins to simulate external memory interaction.

## Technical Specifications

- **Word Size**: 8 bits (1 byte)
- **Cache Size**: 8 entries
- **Address Space**: 8 bits
- **CPU Interface**: 4-bit nibble-based reads (multiplexed)
- **Memory Interface**: AHB-Lite over UIO pins

## Pinout Mapping

### CPU Side (Dedicated Inputs/Outputs)

| Pin | Name | Description |
|---|---|---|
| `ui_in[4:0]` | `addr` | Cache address bits [4:0] (padded to 8 bits internally) |
| `ui_in[5]` | `valid` | CPU Request Valid |
| `ui_in[6]` | `write` | CPU Request Write (1=Write, 0=Read) |
| `ui_in[7]` | `sel` | Nibble Select (0=Lower 4 bits, 1=Upper 4 bits) |
| `uo_out[3:0]` | `rdata` | 4-bit CPU Read Data (selected nibble) |
| `uo_out[4]` | `ready` | Cache Ready for next request |
| `uo_out[5]` | `vld_out`| Cache Response Valid |
| `uo_out[6]` | `hwrite` | AHB Write status (for debug) |
| `uo_out[7]` | `htrans` | AHB Transfer status (for debug) |

**Note**: `wdata` is currently hardwired to `0` in this implementation.

### Memory Side (Bidirectional IOs)

The `uio` pins are managed by an internal FSM to simulate external memory:
1. When an AHB request occurs, the chip drives `0x69` on `uio_out` as a handshake.
2. It then switches to input mode and samples `uio_in` to retrieve data from the "external memory".

## How to Test

1. Apply Reset (`rst_n` low).
2. Set an address on `ui_in[4:0]`.
3. Assert `ui_in[5]` (Valid).
4. Monitor `uo_out[4]` (Ready) and `uo_out[5]` (Response Valid).
5. Use `ui_in[7]` to toggle between the upper and lower nibbles of the cached byte.
