# Stage II hardware roadmap (planned, NOT implemented)

The Stage I proposal selects the **Workplace AI** theme and **Battlefield Lightning / ASUS UGen300 (Hailo-10H)** track.

## Functional split

- **Host CPU:** local SQLite sales record, feature preparation, small demand forecasting model, deterministic newsvendor optimizer, and UI.
- **UGen300:** evaluate compatible quantized edge vision models for anonymous footfall detection/tracking; evaluate whether small speech workloads are feasible under vendor software and device-memory constraints.
- **Output:** local large-text recommendation, explanations and end-of-day reconciliation.

## Validation gates before claiming hardware support

1. Verify actual hardware and SDK/driver/host OS, model compiler and operators.
2. Load a supported Hailo model and confirm real on-device inference instead of CPU emulation.
3. Demonstrate anonymous counting accuracy and failure modes in an authorized video setting; never deploy facial identification.
4. Benchmark FPS, end-to-end latency, peak memory, power and thermals; compare with CPU under fair conditions.
5. Confirm speech model feasibility and noisy-market accuracy; offer large-button manual fallback.
6. Run an extended stability test (proposal target 72 hours) and clearly report results.
7. Confirm camera permissions, notices and privacy compliance before collecting any real person imagery.

## Business experiment (H3)

- Recruit consenting vendors and log product-unit costs, salvage value, sales, spoilage, on-hand stock and sell-out times.
- Record that real demand is censored on sell-out days; do not infer all lost sales from observed receipts.
- Prefer a controlled evaluation across comparable products/days or a prospective shadow-mode trial before following the model's orders.
- Define H3 success in advance: lower leftover loss **without increasing stockouts**, compared with vendor's baseline.
- Report negative and null results too. Synthetic backtests in Stage I are an algorithm demonstration only.

**Scheduling:** The submitted screenshot specifies Stage I closes October 28, 2026, 17:00 (Taiwan time). Dates on an earlier presentation slide should be updated using the latest official Stage II timetable.
