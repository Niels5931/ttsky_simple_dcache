module tt_um_simple_dcache_tb (
    input logic [7:0] ui_in,    // Dedicated inputs
    input logic [7:0] uo_out,   // Dedicated outputs
    input logic [7:0] uio_in,   // IOs: Input path
    input logic [7:0] uio_out,  // IOs: Output path
    input logic [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input logic       ena,      // always 1 when the design is powered, so you can ignore it
    input logic       clk,      // clock
    input logic       rst_n     // reset_n - low to reset
);

endmodule
