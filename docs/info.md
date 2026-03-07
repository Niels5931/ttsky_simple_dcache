<!---

This file is used to generate your project datasheet. Please fill in the information below and delete any unused
sections.

You can also include images in this folder and reference them in the markdown. Each image must be less than
512 kb in size, and the combined size of all images must be less than 1 MB.
-->

## How it works

The Tiny D-Cache is a direct-mapped 8-entry cache for 8-bit architectures. It sits between a CPU and external memory using an AHB-Lite interface. The CPU communicates via a nibble-based (4-bit) read interface - the upper or lower nibble can be selected using the `sel` pin. When a cache miss occurs, the controller drives a handshake signal on the `uio` pins and reads data from "external memory" (simulated via bidirectional UIO pins).

## How to test

1. Apply Reset (`rst_n` low).
2. Set an address on `ui_in[4:0]`.
3. Assert `ui_in[5]` (Valid).
4. Monitor `uo_out[4]` (Ready) and `uo_out[5]` (Response Valid).
5. Use `ui_in[7]` to toggle between the upper and lower nibbles of the cached byte.

## External hardware

List external hardware used in your project (e.g. PMOD, LED display, etc), if any
