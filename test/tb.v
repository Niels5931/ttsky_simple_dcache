module tt_um_simple_dcache_tb (
    input  reg [7:0] ui_in,    // Dedicated inputs
    output reg [7:0] uo_out,   // Dedicated outputs
    input  reg [7:0] uio_in,   // IOs: Input path
    inout  reg [7:0] uio_out,  // IOs: Output path
    output reg [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  reg       ena,      // always 1 when the design is powered, so you can ignore it
    input  reg       clk,      // clock
    input  reg       rst_n     // reset_n - low to reset
  );

`ifdef GL_TEST
  wire VPWR = 1'b1;
  wire VGND = 1'b0;
`endif

  tt_um_simple_dcache dut (
`ifdef GL_TEST
      .VPWR    (VPWR),
      .VGND    (VGND),
`endif
      .ui_in   (ui_in),
      .uo_out  (uo_out),
      .uio_in  (uio_in),
      .uio_out (uio_out),
      .uio_oe  (uio_oe),
      .ena     (ena),
      .clk     (clk),
      .rst_n   (rst_n)
  );

  initial begin
    $dumpfile("tb.vcd");
    $dumpvars(0);
  end

endmodule
