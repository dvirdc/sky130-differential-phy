// SPDX-License-Identifier: Apache-2.0
`timescale 1ns/1ps
`default_nettype none
module diff8_digital(input wire clk, rst_n, ena,
 input wire [7:0] ui_in, uio_in,
 output wire [7:0] uo_out, uio_out, uio_oe,
 input wire phy_rx, output wire phy_tx, phy_boost);
 wire reset_n = rst_n & ena;
 reg [15:0] baud_div, div_count;
 wire tick16 = div_count==0;
 reg boost; reg [2:0] pattern;
 reg [7:0] tx_register, rx_register;
 reg [31:0] target_count;
 reg running, done, fail, command_error, overflow, rx_ready;
 reg [31:0] checked_bytes, error_bytes, error_bits;
 // Every checked byte contributes eight payload bits; derive the saturated total.
 wire [31:0] checked_bits=(|checked_bytes[31:29])?32'hffffffff:{checked_bytes[28:0],3'b000};
 reg [31:0] framing_errors, timeouts, overruns;
 reg snapshot_valid;
 reg [31:0] snap_bytes,snap_error_bytes,snap_error_bits;
 wire [31:0] snap_bits=(|snap_bytes[31:29])?32'hffffffff:{snap_bytes[28:0],3'b000};
 reg [31:0] snap_framing,snap_timeouts,snap_overruns;
 reg [7:0] bad_expected,bad_actual;
 reg [1:0] bist_state;
 reg [9:0] wait_ticks; reg [5:0] gap_ticks;
 reg [7:0] tx_sequence, rx_sequence;
 // Only the pattern index is needed; no run can send more than 2^32-1 frames.
 reg [2:0] sent_bytes;
 reg tx_start; reg [7:0] tx_data;
 wire tx_busy, rx_busy, rx_valid, rx_frame_error; wire [7:0] rx_data;
 reg [19:0] heartbeat;
 wire passed = done && !fail && !overflow && target_count!=0 && checked_bytes==target_count;
 assign phy_boost = boost;
 diff8_uart_tx tx(.clk(clk),.reset_n(reset_n),.tick16(tick16),.start(tx_start),.data(tx_data),.serial(phy_tx),.busy(tx_busy));
 diff8_uart_rx rx(.clk(clk),.reset_n(reset_n),.tick16(tick16),.serial(phy_rx),.data(rx_data),.valid(rx_valid),.frame_error(rx_frame_error),.busy(rx_busy));
 function [31:0] inc32; input [31:0] x; begin inc32=(&x)?x:x+1'b1; end endfunction
 function [31:0] addsmall; input [31:0] x; input [3:0] n;
  begin addsmall=(x>32'hffffffff-{28'b0,n})?32'hffffffff:x+{28'b0,n}; end endfunction
 function [3:0] popcount; input [7:0] x; integer i; begin popcount=0; for(i=0;i<8;i=i+1) popcount=popcount+{3'b0,x[i]}; end endfunction
 function [7:0] lfsr_next; input [7:0] x; begin lfsr_next={x[6:0],x[7]^x[5]^x[4]^x[3]}; end endfunction
 function [7:0] pattern_byte; input [2:0] mode; input [2:0] index; input [7:0] seq, fixed_byte;
  begin case(mode)
   0:pattern_byte=seq;
   1:pattern_byte=index[0]?8'haa:8'h55;
   2:pattern_byte=8'h01<<index[2:0];
   3:pattern_byte=~(8'h01<<index[2:0]);
   default:pattern_byte=fixed_byte;
  endcase end
 endfunction
 wire [7:0] expected=pattern_byte(pattern,checked_bytes[2:0],rx_sequence,tx_register);
 wire [3:0] differences=popcount(rx_data^expected);
 // SPI mode 0, one command byte then one data byte per CS assertion.
 // Synchronize input pins; require >=8 system clocks per SCK half-period.
 (* async_reg = "true" *) reg [1:0] cs_pipe,sck_pipe,mosi_pipe;
 reg sck_old; reg [4:0] spi_count; reg [6:0] spi_shift; reg [7:0] spi_reply;
 reg [6:0] spi_address; reg spi_write;
 reg bus_wr,bus_rd; reg [6:0] bus_address; reg [7:0] bus_data;
 wire sck_rise=sck_pipe[1] && !sck_old;
 wire sck_fall=!sck_pipe[1] && sck_old;
 wire [6:0] incoming_address={spi_shift[5:0],mosi_pipe[1]};
 function [7:0] read_register; input [6:0] address;
  begin if (!snapshot_valid && address>=7'd16 && address<=7'd43) read_register=0;
  else case(address)
   0:read_register=8'hd8;
   1:read_register=8'h01;
   2:read_register={7'b0,boost};
   4:read_register=tx_register;
   5:read_register=rx_register;
   6:read_register={command_error,overflow,rx_ready,tx_busy,fail,passed,done,running};
   7:read_register={5'b0,pattern};
   8:read_register=target_count[7:0]; 9:read_register=target_count[15:8];
   10:read_register=target_count[23:16]; 11:read_register=target_count[31:24];
   12:read_register=baud_div[7:0]; 13:read_register=baud_div[15:8];
   16:read_register=snap_bytes[7:0];17:read_register=snap_bytes[15:8];18:read_register=snap_bytes[23:16];19:read_register=snap_bytes[31:24];
   20:read_register=snap_bits[7:0];21:read_register=snap_bits[15:8];22:read_register=snap_bits[23:16];23:read_register=snap_bits[31:24];
   24:read_register=snap_error_bytes[7:0];25:read_register=snap_error_bytes[15:8];26:read_register=snap_error_bytes[23:16];27:read_register=snap_error_bytes[31:24];
   28:read_register=snap_error_bits[7:0];29:read_register=snap_error_bits[15:8];30:read_register=snap_error_bits[23:16];31:read_register=snap_error_bits[31:24];
   32:read_register=snap_framing[7:0];33:read_register=snap_framing[15:8];34:read_register=snap_framing[23:16];35:read_register=snap_framing[31:24];
   36:read_register=snap_timeouts[7:0];37:read_register=snap_timeouts[15:8];38:read_register=snap_timeouts[23:16];39:read_register=snap_timeouts[31:24];
   40:read_register=snap_overruns[7:0];41:read_register=snap_overruns[15:8];42:read_register=snap_overruns[23:16];43:read_register=snap_overruns[31:24];
   44:read_register=bad_expected;45:read_register=bad_actual;
   default:read_register=0;
  endcase end
 endfunction
 always @(posedge clk or negedge reset_n) begin
  if (!reset_n) begin cs_pipe<=2'b11;sck_pipe<=0;mosi_pipe<=0;sck_old<=0;
   spi_count<=0;spi_shift<=0;spi_reply<=0;spi_address<=0;spi_write<=0;
   bus_wr<=0;bus_rd<=0;bus_address<=0;bus_data<=0;end
  else begin
   cs_pipe<={cs_pipe[0],ui_in[0]};sck_pipe<={sck_pipe[0],ui_in[1]};mosi_pipe<={mosi_pipe[0],ui_in[2]};sck_old<=sck_pipe[1];
   bus_wr<=0;bus_rd<=0;
   if(cs_pipe[1]) begin spi_count<=0;spi_reply<=0;end
   else begin
    if(sck_rise && spi_count<16) begin
     spi_shift<={spi_shift[5:0],mosi_pipe[1]};spi_count<=spi_count+1'b1;
     if(spi_count==7) begin spi_address<=incoming_address;spi_write<=spi_shift[6];spi_reply<=read_register(incoming_address);end
     if(spi_count==15) begin bus_address<=spi_address;bus_data<={spi_shift[6:0],mosi_pipe[1]};bus_wr<=spi_write;bus_rd<=!spi_write;end
    end
    if(sck_fall && spi_count>8 && spi_count<16) spi_reply<={spi_reply[6:0],1'b0};
   end
  end
 end
 always @(posedge clk or negedge reset_n) begin
  if(!reset_n) begin div_count<=0;heartbeat<=0;end
  else begin
   heartbeat<=heartbeat+1'b1;
   if(tick16)div_count<=baud_div-1'b1;else div_count<=div_count-1'b1;
  end
 end
 always @(posedge clk or negedge reset_n) begin
  if(!reset_n) begin
   baud_div<=1;boost<=0;pattern<=0;tx_register<=8'ha5;rx_register<=0;
   target_count<=32;running<=0;done<=0;fail<=0;command_error<=0;overflow<=0;rx_ready<=0;
   checked_bytes<=0;error_bytes<=0;error_bits<=0;framing_errors<=0;timeouts<=0;overruns<=0;
   bad_expected<=0;bad_actual<=0;bist_state<=0;wait_ticks<=0;gap_ticks<=0;
   tx_sequence<=8'ha5;rx_sequence<=8'ha5;sent_bytes<=0;tx_start<=0;tx_data<=0;
  end else begin
   tx_start<=0;
   if(bus_rd && bus_address==5)rx_ready<=0;
   if(rx_frame_error) begin
    framing_errors<=inc32(framing_errors);if(&framing_errors)overflow<=1;
    fail<=1;
    if(running)begin running<=0;done<=1;bist_state<=0;end
   end
   if(rx_valid && !running) begin
    rx_register<=rx_data;rx_ready<=1;
    if(rx_ready && !(bus_rd && bus_address==5))begin overruns<=inc32(overruns);if(&overruns)overflow<=1;fail<=1;end
   end
   if(running && !rx_frame_error) begin
    if(rx_valid && bist_state!=2) begin framing_errors<=inc32(framing_errors);if(&framing_errors)overflow<=1;fail<=1;done<=1;running<=0;end
    else case(bist_state)
     1:if(!tx_busy && !tx_start) begin
      tx_data<=pattern_byte(pattern,sent_bytes[2:0],tx_sequence,tx_register);tx_start<=1;
      tx_sequence<=lfsr_next(tx_sequence);sent_bytes<=sent_bytes+3'd1;wait_ticks<=0;bist_state<=2;
     end
     2:if(rx_valid)begin
      checked_bytes<=inc32(checked_bytes);
      if(&checked_bytes || checked_bits>32'hfffffff7)overflow<=1;
      rx_sequence<=lfsr_next(rx_sequence);
      if(differences!=0)begin
       error_bytes<=inc32(error_bytes);error_bits<=addsmall(error_bits,differences);
       if(&error_bytes || error_bits>32'hffffffff-{28'b0,differences})overflow<=1;
       bad_expected<=expected;bad_actual<=rx_data;fail<=1;
      end
      if(checked_bytes==target_count-1'b1)begin running<=0;done<=1;bist_state<=0;end
      else begin gap_ticks<=0;bist_state<=3;end
     end else if(tick16)begin
      if(wait_ticks==511)begin timeouts<=inc32(timeouts);if(&timeouts)overflow<=1;fail<=1;done<=1;running<=0;bist_state<=0;end
      else wait_ticks<=wait_ticks+1'b1;
     end
     3:if(tick16 && !tx_busy) begin if(gap_ticks==31)bist_state<=1;else gap_ticks<=gap_ticks+1'b1;end
     default:begin fail<=1;done<=1;running<=0;end
    endcase
   end
   if(bus_wr) begin
    if(bus_address==3)begin
     case(bus_data)
      1:if(!running && !tx_busy && !rx_busy && !tx_start && target_count!=0)begin
       running<=1;done<=0;fail<=0;command_error<=0;overflow<=0;rx_ready<=0;
       checked_bytes<=0;error_bytes<=0;error_bits<=0;framing_errors<=0;timeouts<=0;overruns<=0;
       bad_expected<=0;bad_actual<=0;tx_sequence<=8'ha5;rx_sequence<=8'ha5;sent_bytes<=0;wait_ticks<=0;gap_ticks<=0;bist_state<=1;
      end else begin command_error<=1;fail<=1;end
      2:if(!running && !tx_busy && !tx_start)begin
       done<=0;fail<=0;command_error<=0;overflow<=0;rx_ready<=0;
       checked_bytes<=0;error_bytes<=0;error_bits<=0;framing_errors<=0;timeouts<=0;overruns<=0;
      end else begin command_error<=1;fail<=1;end
      4:if(!running && !tx_busy && !tx_start)begin tx_data<=tx_register;tx_start<=1;done<=0;end
        else begin command_error<=1;fail<=1;end
      8:begin running<=0;done<=1;fail<=1;bist_state<=0;end
      16:begin end
      default:begin command_error<=1;fail<=1;end
     endcase
    end else if(running || tx_busy || rx_busy || tx_start)begin command_error<=1;fail<=1;end
    else begin
     done<=0;
     case(bus_address)
     2:if(bus_data<=1)boost<=bus_data[0];else begin command_error<=1;fail<=1;end
     4:tx_register<=bus_data;
     7:if(bus_data<=4)pattern<=bus_data[2:0];else begin command_error<=1;fail<=1;end
     8:target_count[7:0]<=bus_data;9:target_count[15:8]<=bus_data;
     10:target_count[23:16]<=bus_data;11:target_count[31:24]<=bus_data;
     12:if({baud_div[15:8],bus_data}!=0)baud_div[7:0]<=bus_data;else begin command_error<=1;fail<=1;end
     13:if({bus_data,baud_div[7:0]}!=0)baud_div[15:8]<=bus_data;else begin command_error<=1;fail<=1;end
     default:begin command_error<=1;fail<=1;end
     endcase
    end
   end
  end
 end
 // Snapshot payload uses ordinary flops; one resettable validity bit preserves
 // all externally observable zero-after-reset semantics.
 wire snapshot_strobe = bus_wr && bus_address==3 && bus_data==16;
 always @(posedge clk or negedge reset_n) begin
  if(!reset_n) snapshot_valid<=0;
  else if(snapshot_strobe) snapshot_valid<=1;
 end
 always @(posedge clk) begin
  if(snapshot_strobe)begin
   snap_bytes<=checked_bytes;snap_error_bytes<=error_bytes;snap_error_bits<=error_bits;
   snap_framing<=framing_errors;snap_timeouts<=timeouts;snap_overruns<=overruns;
  end
 end
 assign uo_out={rx_valid,phy_tx,heartbeat[19],fail,passed,running,phy_rx,spi_reply[7]};
 assign uio_out={7'b0,boost};assign uio_oe=8'h01;
 wire unused=&{1'b0,ui_in[7:3],uio_in};
endmodule
`default_nettype wire
