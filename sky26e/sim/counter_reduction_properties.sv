// SPDX-License-Identifier: Apache-2.0
// Algebraic/transition proofs for the area reductions, not a whole-core equivalence proof.
module counter_reduction_properties(
 input [31:0] bytes, snapshot_bytes, target, active, checked,
 input increment, clear_counts, reset, snapshot,
 input running, done, fail, overflow,
 input [3:0] event_kind,
 input [31:0] replacement_target, sent);
 function [31:0] sat_bits(input [31:0] n);
  sat_bits=(|n[31:29])?32'hffffffff:{n[28:0],3'b000};
 endfunction
 wire [31:0] old_bits=sat_bits(bytes);
 wire [31:0] next_bytes=(reset||clear_counts)?0:increment?((&bytes)?bytes:bytes+1'b1):bytes;
 wire [31:0] reference_next_bits=(reset||clear_counts)?0:increment?((old_bits>32'hfffffff7)?32'hffffffff:old_bits+32'd8):old_bits;
 wire [31:0] next_snapshot=reset?0:snapshot?bytes:snapshot_bytes;
 wire [31:0] reference_snapshot_bits=reset?0:snapshot?old_bits:sat_bits(snapshot_bytes);
 // target_active differs from target_count only when neither running nor potentially PASS.
 // Start/config/clear/send guards and DONE invalidation are preserved in the RTL.
 wire invariant=!(running || (done&&!fail)) || active==target;
 reg [31:0] next_target,next_active;
 reg next_running,next_done,next_fail;
 always @* begin
  next_target=target;next_active=active;
  next_running=running;next_done=done;next_fail=fail;
  case(event_kind)
   1:begin next_active=target;next_running=1;next_done=0;next_fail=0;end
   2:begin next_target=replacement_target;next_active=0;next_done=0;end
   3:begin next_active=0;next_done=0;next_fail=0;end
   4:begin next_active=0;next_done=0;end
   5:begin next_running=0;next_done=1;next_fail=1;end
   6:begin next_running=0;next_done=1;end
   7:begin next_fail=1;end
   default:begin end
  endcase
 end
 always @* begin
  assert(reference_next_bits==sat_bits(next_bytes));
  assert(reference_snapshot_bits==sat_bits(next_snapshot));
  assume(invariant);
  if(event_kind>=1 && event_kind<=4)assume(!running);
  if(event_kind==1)assume(target!=0);
  if(event_kind==6)assume(running);
  assert(!(next_running || (next_done&&!next_fail)) || next_active==next_target);
  assert((done&&!fail&&!overflow&&active!=0&&checked==active)==
         (done&&!fail&&!overflow&&target!=0&&checked==target));
  // At each TX launch: sent==checked<target. There is one outstanding BIST frame;
  // each subsequent launch follows a receive, and the last receive ends the run.
  if(sent<target) begin
   assert(sent!=32'hffffffff);
   assert(((sent+32'd1)&32'h7)=={29'd0,(sent[2:0]+3'd1)});
  end
 end
endmodule
