set circuit1 [readnet spice /work/sky26e/build/candidate_2x2/verification/tt_um_dvirdc_sky130_diff8.spice]
set circuit2 [readnet verilog /dev/null]
puts "Reading SPICE netlist file '/pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__decap_12.spice'..."
readnet spice /pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__decap_12.spice $circuit2
puts "Reading SPICE netlist file '/pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__decap_20_12.spice'..."
readnet spice /pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__decap_20_12.spice $circuit2
puts "Reading SPICE netlist file '/pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__decap_40_12.spice'..."
readnet spice /pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__decap_40_12.spice $circuit2
puts "Reading SPICE netlist file '/pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__decap_60_12.spice'..."
readnet spice /pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__decap_60_12.spice $circuit2
puts "Reading SPICE netlist file '/pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__decap_80_12.spice'..."
readnet spice /pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__decap_80_12.spice $circuit2
puts "Reading SPICE netlist file '/pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__fill_12.spice'..."
readnet spice /pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__fill_12.spice $circuit2
puts "Reading SPICE netlist file '/pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__fill_2.spice'..."
readnet spice /pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__fill_2.spice $circuit2
puts "Reading SPICE netlist file '/pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__fill_4.spice'..."
readnet spice /pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__fill_4.spice $circuit2
puts "Reading SPICE netlist file '/pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__fill_8.spice'..."
readnet spice /pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_ef_sc_hd__fill_8.spice $circuit2
puts "Reading SPICE netlist file '/pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice'..."
readnet spice /pdk/sky130A/libs.ref/sky130_fd_sc_hd/spice/sky130_fd_sc_hd.spice $circuit2
puts "Reading SPICE netlist file '/work/sky26e/physical/phy_reference.spice'..."
readnet spice /work/sky26e/physical/phy_reference.spice $circuit2
readnet verilog /work/sky26e/physical/runs/compact_hold025/54-openroad-fillinsertion/tt_um_dvirdc_sky130_diff8.pnl.v $circuit2
lvs "$circuit1 tt_um_dvirdc_sky130_diff8" "$circuit2 tt_um_dvirdc_sky130_diff8" /pdk/sky130A/libs.tech/netgen/sky130A_setup.tcl /work/sky26e/build/candidate_2x2/verification/lvs.rpt -json
