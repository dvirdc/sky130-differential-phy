# 1.6 MHz external system clock. SPI and PHY RX enter two-stage synchronizers.
create_clock -name clk -period 625 [get_ports clk]
set_clock_uncertainty -setup 2 [get_clocks clk]
set_clock_uncertainty -hold 0.5 [get_clocks clk]
set_clock_transition 2 [get_clocks clk]
set_false_path -from [get_ports {rst_n ena ui_in[*] uio_in[*]}]
# Analog RX arrival is asynchronous; downstream synchronizer stages remain timed.
set_false_path -from [get_ports {ua[*]}]
set_output_delay -clock clk -max 100 [all_outputs]
set_output_delay -clock clk -min 0 [all_outputs]
set_load 0.05 [all_outputs]

# Reserve electrical margin for extracted interconnect at the slow corner.
set_max_transition 1.0 [current_design]
set_max_capacitance 0.10 [current_design]
set_max_fanout 16 [current_design]
