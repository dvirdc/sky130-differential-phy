// SPDX-License-Identifier: Apache-2.0
// Analog layout boundary only. This declaration implements no circuit.
`timescale 1ns/1ps
`default_nettype none
(* blackbox *) module sky130_diff_phy(input wire din,boost,output wire dout,
 inout wire txp,txn,rxp,rxn,VDPWR,VGND);
endmodule
`default_nettype wire
