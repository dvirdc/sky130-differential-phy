// SPDX-License-Identifier: Apache-2.0
// DIGITAL-ONLY boundary model: no voltage, gain, noise, PDK, pad or PEX claim.
// Different propagation delays exercise boost control without claiming gain.
`timescale 1ns/1ps
`default_nettype none
module sky130_diff_phy(input wire din,boost,output wire dout,
 inout wire txp,txn,rxp,rxn,VDPWR,VGND);
 reg delayed_tx;
 initial delayed_tx=1;
 always @(din or boost) begin
  if(boost) delayed_tx<=#20 din;else delayed_tx<=#40 din;
 end
 assign txp=delayed_tx;assign txn=~delayed_tx;
 // An open/invalid differential pair resolves idle; the BIST must time out.
 assign #20 dout=(rxp===1'b0 && rxn===1'b1)?1'b0:1'b1;
 wire unused=&{1'b0,VDPWR,VGND};
endmodule
`default_nettype wire
