// SPDX-License-Identifier: Apache-2.0
`timescale 1ns/1ps
`default_nettype none
// Start detection and sampling are independent of the transmit engine.
module diff8_uart_rx(input wire clk, reset_n, tick16, serial,
 output reg [7:0] data, output reg valid, frame_error, output reg busy);
 (* async_reg = "true" *) reg rx_meta, rx_sync;
 reg [3:0] phase, bit_index; reg [1:0] ones; reg [7:0] shift;
 wire [2:0] data_index = bit_index[2:0]-3'd1;
 wire majority = ({1'b0,ones}+{2'b00,rx_sync})>=3'd2;
 always @(posedge clk or negedge reset_n) begin
  if (!reset_n) begin rx_meta<=1; rx_sync<=1; end
  else begin rx_meta<=serial; rx_sync<=rx_meta; end
 end
 always @(posedge clk or negedge reset_n) begin
  if (!reset_n) begin data<=0; valid<=0; frame_error<=0; busy<=0;
   phase<=0; bit_index<=0; ones<=0; shift<=0; end
  else begin
   valid<=0; frame_error<=0;
   if (tick16) begin
    if (!busy) begin
     if (!rx_sync) begin busy<=1; phase<=0; bit_index<=0; ones<=0; end
    end else begin
     if (phase==6 || phase==7) ones<=ones+{1'b0,rx_sync};
     if (phase==8) begin
      if (bit_index==0 && majority) begin busy<=0; frame_error<=1; end
      else if (bit_index>=1 && bit_index<=8) shift[data_index]<=majority;
      else if (bit_index==9) begin
       busy<=0;
       if (majority) begin data<=shift; valid<=1; end else frame_error<=1;
      end
     end
     if (phase==15) begin phase<=0; bit_index<=bit_index+1'b1; ones<=0; end
     else phase<=phase+1'b1;
    end
   end
  end
 end
endmodule
`default_nettype wire
