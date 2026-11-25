// SPDX-License-Identifier: Apache-2.0
`timescale 1ns/1ps
`default_nettype none
module tb;
 reg clk=0; always #312.5 clk=~clk; // 1.6 MHz, 16 clocks per bit
 localparam real BIT_NS=10000.0;
 reg rst_n=0,ena=1;reg [7:0] ui=8'h01;wire [7:0] uo,uio_out,uio_oe;
 tri [7:0] ua; supply1 vdd; supply0 gnd;
 integer fault=0;reg invert_payload=0,bad_stop=0,peer=1;
 // ONLY top-level pins are driven or observed. No DUT hierarchy access.
 wire p=(fault==2)?1'b0:(fault==3 || fault==5)?1'b1:(fault==6)?peer:
        bad_stop?1'b0:invert_payload?~ua[0]:ua[0];
 wire n=(fault==2)?1'b1:(fault==3)?1'b0:(fault==5)?1'b1:(fault==6)?~peer:
        bad_stop?1'b1:invert_payload?~ua[1]:ua[1];
 assign ua[2]=(fault==1)?1'bz:p;
 assign ua[3]=(fault==1)?1'bz:n;
 tt_um_dvirdc_sky130_diff8 dut(.clk(clk),.rst_n(rst_n),.ena(ena),.ui_in(ui),.uio_in(8'b0),
  .uo_out(uo),.uio_out(uio_out),.uio_oe(uio_oe),.ua(ua),.VDPWR(vdd),.VGND(gnd));
 integer snapshot_reset_reads=0;
 integer tests=0;reg [7:0] status,value,received,captured;reg [31:0] count,bits,errbytes,errbits,frames,touts,ov;
 integer mode,b,j;reg [7:0] random_byte;
 task check(input bit condition,input string message);
  if(condition!==1'b1)begin $display("FAIL %s time=%0t status=%02x",message,$time,status);$fatal(1);end
 endtask
 task reset;
  begin rst_n=0;ena=1;ui=8'h01;fault=0;invert_payload=0;bad_stop=0;peer=1;
   repeat(12)@(negedge clk);rst_n=1;repeat(12)@(negedge clk);zero_snapshots();end
 endtask
 task transfer(input [15:0] request,output [15:0] response);
  integer k;
  begin response=0;@(negedge clk);ui[0]=0;repeat(8)@(negedge clk);
   for(k=15;k>=0;k=k-1)begin
    ui[1]=0;ui[2]=request[k];repeat(8)@(negedge clk);
    ui[1]=1;repeat(4)@(negedge clk);response[k]=uo[0];repeat(4)@(negedge clk);
   end
   ui[1]=0;repeat(8)@(negedge clk);ui[0]=1;repeat(8)@(negedge clk);
  end
 endtask
 task wr(input [6:0] address,input [7:0] data);reg [15:0] reply;
  begin transfer({1'b1,address,data},reply);end
 endtask
 task rd(input [6:0] address,output [7:0] data);reg [15:0] reply;
  begin transfer({1'b0,address,8'h00},reply);data=reply[7:0];end
 endtask
 task zero_snapshots;
  integer a; reg [7:0] reply;
  begin
   for(a=16;a<=43;a=a+1)begin
    rd(7'(a),reply);check(reply===8'h00,"snapshot reads zero before first snapshot after reset");
    snapshot_reset_reads=snapshot_reset_reads+1;
   end
  end
 endtask
 task rd32(input [6:0] address,output [31:0] data);reg [7:0] x;integer k;
  begin for(k=0;k<4;k=k+1)begin rd(address+7'(k),x);data[k*8+:8]=x;end end
 endtask
 task configure(input integer length,input integer kind,input integer boost);
  begin wr(2,8'(boost));wr(7,8'(kind));wr(8,8'(length));wr(9,8'(length>>8));wr(10,8'(length>>16));wr(11,8'(length>>24));
   check(uio_oe==1 && uio_out[0]==1'(boost),"boost monitor/output enable");end
 endtask
 task await_done;
  integer tries;
  begin tries=0;status=0;
   while(!status[1] && tries<400)begin rd(6,status);tries=tries+1;end
   check(status[1],"bounded completion");check(!status[0],"not RUNNING when DONE");
  end
 endtask
 task snapshot;
  begin wr(3,16);rd32(16,count);rd32(20,bits);rd32(24,errbytes);rd32(28,errbits);rd32(32,frames);rd32(36,touts);rd32(40,ov);end
 endtask
 task pass_test(input string label);
  begin tests=tests+1;$display("PASS %0d %s",tests,label);end
 endtask
 task receive_peer(input [7:0] data,input real bit_period);
  integer k;
  begin peer=1;#(bit_period*1.37);peer=0;#(bit_period);
   for(k=0;k<8;k=k+1)begin peer=data[k];#(bit_period);end
   peer=1;#(bit_period*2.0);
  end
 endtask
 task capture_tx(output [7:0] data);
  integer k;
  begin @(negedge ua[0]);#(BIT_NS*1.5);
   for(k=0;k<8;k=k+1)begin data[k]=ua[0];check(ua[1]===~ua[0],"complementary TX pair");#(BIT_NS);end
   check(ua[0]===1'b1,"TX stop bit");end
 endtask
 initial begin
  #2000000000;$fatal(1,"global testbench timeout");
 end
 initial begin
  reset();rd(0,value);check(value==8'hd8,"SPI ID");rd(1,value);check(value==1,"version");rd(6,status);check(!status[2],"reset never PASS");pass_test("SPI identity and reset");
  // Long enough to traverse the full nonzero 8-bit pseudorandom sequence.
  for(b=0;b<2;b=b+1)for(mode=0;mode<5;mode=mode+1)begin
   reset();configure(mode==0?300:24,mode,b);wr(4,8'h3c);wr(3,1);await_done();
   check(status[2]&&!status[3],"good loopback PASS without FAIL");check(uo[3]&&!uo[4],"pass/fail pins");snapshot();
   check(count==(mode==0?300:24) && bits==count*8,"exact checked-byte and payload-bit counts");
   check(errbytes==0&&errbits==0&&frames==0&&touts==0&&ov==0,"zero good-loopback error counters");
   pass_test($sformatf("external analog-boundary loopback pattern=%0d boost=%0d",mode,b));
  end
  for(b=0;b<2;b=b+1)begin
   reset();configure(8,0,b);
   fork
    begin @(negedge uo[6]);#(BIT_NS*3.0);invert_payload=1;#(BIT_NS);invert_payload=0;end
    begin wr(3,1);end
   join
   await_done();check(status[3]&&!status[2],"corrupted payload cannot PASS");snapshot();
   check(count==8&&errbytes==1&&errbits==1&&frames==0,"one wrong payload bit accounted exactly");
   rd(44,value);rd(45,received);check((value^received)==8'h04,"last bad expected/actual byte");pass_test($sformatf("one-bit corruption boost=%0d",b));
   reset();configure(8,0,b);
   fork
    begin @(negedge uo[6]);#(BIT_NS*9.0);bad_stop=1;#(BIT_NS);bad_stop=0;end
    begin wr(3,1);end
   join
   await_done();check(status[3]&&!status[2],"bad stop bit cannot PASS");snapshot();check(frames>=1,"framing error counter");pass_test($sformatf("bad framing boost=%0d",b));
   for(j=1;j<=5;j=j+1)begin
    if(j!=4)begin
     reset();configure(8,0,b);
     fork begin @(negedge uo[6]);fault=j;end begin wr(3,1);end join
     await_done();
     check(status[3]&&!status[2],"open/stuck/invalid pair cannot PASS");snapshot();
     check(frames>0||touts>0,"fault has framing or timeout evidence");pass_test($sformatf("external fault=%0d boost=%0d",j,b));
    end
   end
  end
  // Normal byte mode: independently decode the signal leaving the TX pins.
  for(b=0;b<2;b=b+1)begin
   reset();wr(2,8'(b));
   for(j=0;j<8;j=j+1)begin
    random_byte=8'($random);wr(4,random_byte);
    fork capture_tx(captured);begin wr(3,4);end join
    check(captured==random_byte,"normal TX externally decoded payload");rd(6,status);check(status[5],"normal RX valid");rd(5,received);check(received==random_byte,"normal mode received payload");
    rd(6,status);check(!status[5],"RX data read clears valid");
   end
   pass_test($sformatf("normal user-byte mode boost=%0d",b));
  end
  // Independent serial source, +/-2 percent bit-clock mismatch and phase offset.
  for(mode=0;mode<3;mode=mode+1)begin
   reset();fault=6;
   for(j=0;j<12;j=j+1)begin
    random_byte=8'($random);receive_peer(random_byte,BIT_NS*(0.98+0.02*mode));
    rd(6,status);check(status[5]&&!status[3],"independent source accepted");rd(5,received);check(received==random_byte,"independent source payload");
   end
   pass_test($sformatf("independent RX clock factor=%0.2f",0.98+0.02*mode));
  end
  reset();fault=6;receive_peer(8'h12,BIT_NS);receive_peer(8'h34,BIT_NS);rd(6,status);check(status[3],"unread normal data overrun fails");snapshot();check(ov==1,"one overrun counted");pass_test("normal receive overrun");
  reset();configure(0,0,0);wr(3,1);rd(6,status);check(status[7]&&status[3]&&!status[2]&&!status[0],"zero-length test rejected");pass_test("zero-length cannot falsely PASS");
  reset();wr(12,0);rd(12,value);check(value==1,"zero baud divider rejected");rd(6,status);check(status[7]&&status[3],"bad divider flags error");pass_test("invalid divider");
  reset();configure(1024,0,0);wr(3,1);wr(2,1);rd(2,value);check(value==0,"configuration frozen while active");wr(3,8);rd(6,status);check(status[1]&&status[3]&&!status[2],"abort not PASS");pass_test("active config guard and abort");
  reset();configure(1024,0,1);wr(3,1);rst_n=0;repeat(20)@(negedge clk);rst_n=1;repeat(20)@(negedge clk);rd(6,status);check(!status[0]&&!status[1]&&!status[2],"reset during active test clears completion");pass_test("reset during transmission");
  reset();configure(1024,0,1);wr(3,1);ena=0;repeat(20)@(negedge clk);ena=1;repeat(20)@(negedge clk);rd(6,status);check(!status[0]&&!status[2],"deselect cannot leave PASS");pass_test("project deselection");
  reset();configure(8,0,0);fault=1;wr(3,1);await_done();check(status[3],"initial fault");fault=0;#(BIT_NS*12);wr(3,2);wr(3,1);await_done();check(status[2]&&!status[3],"restart after failed test");pass_test("clear and restart");
  reset();configure(255,0,0);random_byte=8'ha5;
  fork
   begin
    for(j=0;j<255;j=j+1)begin capture_tx(captured);check(captured==random_byte,"independent PRBS transmitter oracle");random_byte={random_byte[6:0],random_byte[7]^random_byte[5]^random_byte[4]^random_byte[3]};end
    check(random_byte==8'ha5,"PRBS nonzero period 255");
   end
   begin wr(3,1);end
  join
  await_done();check(status[2],"independent PRBS capture test");pass_test("all 255 PRBS bytes independently decoded at TX pins");
  wr(2,1);rd(6,status);check(!status[2]&&!status[1],"configuration change invalidates prior PASS");pass_test("no stale PASS after boost change");
  for(b=0;b<2;b=b+1)begin
   reset();configure(32,0,b);
   fork
    begin repeat(3)@(posedge uo[7]);fault=1;end
    begin wr(3,1);end
   join
   await_done();check(status[3]&&!status[2],"link loss after progress fails");snapshot();check(count==3&&touts==1,"partial progress retained on disconnect");pass_test($sformatf("mid-test disconnect boost=%0d",b));
   reset();configure(8,0,b);wr(12,4);wr(3,1);await_done();check(status[2]&&!status[3],"programmable divider loopback");snapshot();check(count==8&&errbits==0,"divider counts");pass_test($sformatf("25 kbit/s divider boost=%0d",b));
  end
  for(b=0;b<2;b=b+1)begin
   reset();configure(1,0,b);wr(12,16);fault=6;peer=0;#(BIT_NS*4);
   wr(3,1);rd(6,status);
   check(status[7]&&status[3]&&!status[0]&&!status[2],"BIST rejects an already active external frame");
   peer=1;pass_test($sformatf("RX-busy start rejected boost=%0d",b));
  end
  // A truncated SPI command must not start a test.
  reset();@(negedge clk);ui[0]=0;repeat(8)@(negedge clk);
  for(j=7;j>=0;j=j-1)begin ui[2]=(8'h83>>j)&1;ui[1]=0;repeat(8)@(negedge clk);ui[1]=1;repeat(8)@(negedge clk);end
  ui[1]=0;ui[0]=1;repeat(12)@(negedge clk);rd(6,status);check(!status[0]&&!status[2],"truncated SPI transaction ignored");pass_test("truncated control transaction");
  $display("SNAPSHOT_RESET_READS=%0d",snapshot_reset_reads);$display("ALL_PASS tests=%0d",tests);$finish;
 end
endmodule
`default_nettype wire
