# 2×2 feasibility experiment

The 2×2 candidate now passes local physical and functional checks; see verification/STATUS.md. The original verified 4×2 candidate remains preserved. The archived `layout/` and `verification/layout/` files remain the 4×2 evidence; they do not qualify the changed RTL or compact macro. The original local checkpoint is 9e7a25e; the private repository main remains separate.

## Measured baseline

The routed 4×2 design uses 58,683.8 µm² of digital standard cells and a 38,400 µm² analog macro. OpenROAD reports 53.5598% digital utilization of core area excluding the macro, and 65.6118% combined occupancy of the 147,967 µm² core. The full die is 682.64×225.76 µm.

The official 2×2 die is 334.88×225.76 µm (75,602.5088 µm²). Directly resizing the original 97,083.8 µm² cells+macro footprint cannot fit.

## Implemented reductions

- Analog macro: 240×160 → 140×90 µm (38,400 → 12,600 µm²). Device sizes, models and connectivity stay unchanged. Independent GDS DRC, official FEOL/BEOL and transistor-level LVS pass; all 30 extracted RC loopback cases pass. See `verification/compact-analog.json`.
- Digital state: remove 125 redundant bits by deriving live/snapshot bit totals, removing a guarded duplicate target and retaining only the three transmitted-pattern index bits. Public 32-bit protocol and counters remain. Unchanged 44 RTL and 44 mapped tests pass; targeted saturation/transition proofs pass. Native mapped area37,664.9 →32,389.8 µm² (14.0% reduction). Whole-core formal equivalence is not claimed. See `verification/compact-digital/`.
- A separate snapshot-valid experiment saves another 1,331 µm² in native mapping. It is not currently production RTL; its independent physical trial is separate.

## Physical trials

Placement and clock-tree synthesis fit, with about 82–84% digital utilization after timing repair. Several routing trials failed congestion following clock/electrical/antenna repair, including a top-right macro placement. `compact_library_02` reached detailed routing using the unchanged PDK signoff limits and full available routing capacity. That high-margin run and the snapshot-reset backup were later intentionally interrupted when the official-hold-default trial became the preferred candidate; they are not claimed as completed passes or failures. No congestion, DRC, antenna or timing acceptance test was waived.

`physical/compact_2x2.json` uses the stricter implementation margin targets. `physical/compact_library.json` instead optimizes against the unchanged library signoff constraints; this does not relax final acceptance limits. Run records under ignored `physical/runs/` preserve resolved configurations and logs. The macro remains at (185,90), with 4 µm placement halos. `physical/info.yaml` and the export helper now describe2×2 experimental exports.

The final compact_hold025 run passes integrated routing, full exported-GDS LVS, DRC, nine-corner timing, all 44 external-pin tests and all 17 official prechecks. The actual shuttle/package/board and post-fill qualifications remain separate for either size.

## Final candidate

`compact_hold025` uses the official 0.25 ns SKY130 hold uncertainty instead of the previous 0.5 ns total. Setup uncertainty remains 2 ns and clock transition remains 2 ns. This removes 877 post-global-route timing-repair buffers versus the prior production trial. Final standard-cell area is 39,567.9 µm² (67.3515% digital utilization); combined core occupancy is 73.1172%. The analog macro remains 12,600 µm². Full 32-bit protocol and counters remain; no 16-bit tradeoff or snapshot-reset experiment was adopted. The exact exported GDS and evidence are in `layout_compact/` and `verification/compact-layout/`.
