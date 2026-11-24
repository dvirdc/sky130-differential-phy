// SPDX-License-Identifier: Apache-2.0
`timescale 1ns/1ps
`default_nettype none
module tt_um_dvirdc_sky130_diff8(
 input wire clk,rst_n,ena,input wire [7:0] ui_in,uio_in,
 output wire [7:0] uo_out,uio_out,uio_oe,inout wire [7:0] ua,
 inout wire VDPWR,VGND);
 wire tx_serial,rx_serial,boost;
 diff8_digital core(.clk(clk),.rst_n(rst_n),.ena(ena),.ui_in(ui_in),.uio_in(uio_in),
 .uo_out(uo_out),.uio_out(uio_out),.uio_oe(uio_oe),.phy_rx(rx_serial),.phy_tx(tx_serial),.phy_boost(boost));
 sky130_diff_phy phy(.din(tx_serial),.boost(boost),.dout(rx_serial),
 .txp(ua[0]),.txn(ua[1]),.rxp(ua[2]),.rxn(ua[3]),.VDPWR(VDPWR),.VGND(VGND));
endmodule
`default_nettype wire
