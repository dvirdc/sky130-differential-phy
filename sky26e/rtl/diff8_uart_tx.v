// SPDX-License-Identifier: Apache-2.0
`timescale 1ns/1ps
`default_nettype none
module diff8_uart_tx(input wire clk, reset_n, tick16, start,
 input wire [7:0] data, output wire serial, output reg busy);
 reg [9:0] frame; reg [3:0] phase, bit_index;
 assign serial = busy ? frame[0] : 1'b1;
 always @(posedge clk or negedge reset_n) begin
  if (!reset_n) begin frame<=10'h3ff; phase<=0; bit_index<=0; busy<=0; end
  else if (start && !busy) begin frame<={1'b1,data,1'b0}; phase<=0; bit_index<=0; busy<=1; end
  else if (busy && tick16) begin
   if (phase==15) begin phase<=0; frame<={1'b1,frame[9:1]};
    if (bit_index==9) busy<=0; else bit_index<=bit_index+1'b1;
   end else phase<=phase+1'b1;
  end
 end
endmodule
`default_nettype wire
