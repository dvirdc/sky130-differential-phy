gds maskhints yes
gds read /work/sky26e/build/candidate_2x2/gds/tt_um_dvirdc_sky130_diff8.gds
load tt_um_dvirdc_sky130_diff8
select top cell
extract do local
extract no capacitance
extract no coupling
extract no resistance
extract no adjust
extract all
ext2spice lvs
ext2spice
quit -noprompt
