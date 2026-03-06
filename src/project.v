/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_simple_dcache (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // dcache_ahb_ctrl instantiation signals
  logic                   req_valid;
  logic [7:0]             req_addr;
  logic [7:0]             req_wdata;
  logic                   req_write;
  logic [2:0]             req_size;
  logic                   req_ready;
  logic                   resp_valid;
  logic [7:0]             resp_rdata;

  // AHB Master Interface
  logic [7:0]             haddr;
  logic [7:0]             hwdata;
  logic [1:0]             htrans;
  logic                   hwrite;
  logic [2:0]             hsize;
  logic [2:0]             hburst;
  logic [3:0]             hprot;
  logic [7:0]             hrdata;
  logic                   hready;
  logic                   hresp;

  // Tiny Design Mapping
  assign req_valid = ui_in[5];
  assign req_write = ui_in[6];
  assign req_addr  = {3'd0, ui_in[4:0]};  // 5 bits address for 16 indexes, 1 offset
  assign req_wdata = 0;
  assign req_size  = 3'b000;              // Byte size (8-bit)

  // Nibble selection for 4-bit CPU read
  wire nibble_sel = ui_in[7];
  wire [3:0] resp_nibble = nibble_sel ? resp_rdata[7:4] : resp_rdata[3:0];

  // -------------------------------------------------------------------------
  // External Memory Simulation (AHB -> UIO)
  // -------------------------------------------------------------------------
  typedef enum logic [1:0] {
    MEM_IDLE,
    MEM_DRIVE,
    MEM_SAMPLE
  } mem_state_t;

  mem_state_t mem_state, mem_next;
  logic [7:0] uio_out_reg;
  logic [7:0] uio_oe_reg;
  logic [7:0] hrdata_reg;
  logic       hready_reg;

  always_ff @(posedge clk or negedge rst_n) begin
    if (!rst_n) begin
      mem_state <= MEM_IDLE;
    end else begin
      mem_state <= mem_next;
    end
  end

  always_comb begin
    mem_next    = mem_state;
    hready_reg  = 1'b1;
    uio_oe_reg  = 8'h00;
    uio_out_reg = 8'h00;
    hrdata_reg  = 8'h00; // Default, overriden in SAMPLE

    case (mem_state)
      MEM_IDLE: begin
        hready_reg = 1'b1;
        // Check for Non-Sequential (2) or Sequential (3) transfer
        if (htrans[1]) begin
          mem_next = MEM_DRIVE;
        end
      end

      MEM_DRIVE: begin
        hready_reg  = 1'b0;      // Stall the master
        uio_oe_reg  = 8'hFF;     // Drive outputs
        uio_out_reg = 8'h69;     // Drive pattern
        mem_next    = MEM_SAMPLE;
      end

      MEM_SAMPLE: begin
        hready_reg  = 1'b1;      // Ready to complete
        uio_oe_reg  = 8'h00;     // Release bus (input mode)
        hrdata_reg  = uio_in;    // Sample input
        mem_next    = MEM_IDLE;
      end

      default: begin
        mem_next = MEM_IDLE;
      end
    endcase
  end

  assign hready  = hready_reg;
  assign hrdata  = hrdata_reg;
  assign hresp   = 1'b0; // OKAY
  assign uio_out = uio_out_reg;
  assign uio_oe  = uio_oe_reg;

  dcache_ahb_ctrl #(
    .WORD_SIZE(8),
    .CACHE_SIZE(8),
    .ADDR_LENGTH(8)
  ) u_dcache (
    .clk        (clk),
    .rst_n      (rst_n),
    .req_valid  (req_valid),
    .req_addr   (req_addr),
    .req_wdata  (req_wdata),
    .req_write  (req_write),
    .req_size   (req_size),
    .req_ready  (req_ready),
    .resp_valid (resp_valid),
    .resp_rdata (resp_rdata),
    .haddr      (haddr),
    .hwdata     (hwdata),
    .htrans     (htrans),
    .hwrite     (hwrite),
    .hsize      (hsize),
    .hburst     (hburst),
    .hprot      (hprot),
    .hrdata     (hrdata),
    .hready     (hready),
    .hresp      (hresp)
  );

  // Output Mapping
  assign uo_out[3:0] = resp_nibble;
  assign uo_out[4]   = req_ready;
  assign uo_out[5]   = resp_valid;
  assign uo_out[6]   = hwrite;
  assign uo_out[7]   = htrans[1];

  // List all unused inputs to prevent warnings
  wire _unused = &{ena, clk, rst_n, 1'b0, haddr, hwdata, htrans[0], hsize, hburst, hprot};

endmodule
