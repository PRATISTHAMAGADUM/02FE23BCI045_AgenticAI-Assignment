# Lab 13 - Assignment 1: Add a Second Domain: Electrical Load Forecasting

## Objective
Implement an autonomous engineering agent for Electrical Engineering: electrical load forecasting and substation fault triage on a 50 MVA transformer station. Apply threshold classification (IEEE C57.91-style loading standards) and confirm that the identical human-in-the-loop safety boundary applies to high-impact electrical actions (e.g., emergency load shedding/rolling blackout mitigation) before any recommendation is executed.

## Key Implementation Details
1. **Domain Telemetry**:
   - Monitored parameters: `load_mva`, `voltage_kv`, `freq_hz`, and `transformer_temp_c`.
   - Rated capacity: 50.0 MVA.
2. **Classification Logic**:
   - Normal: Load < 43 MVA, temp < 80°C.
   - Warning: Load >= 43 MVA or temp >= 80°C.
   - Alarm: Load >= 48.5 MVA (97% utilization), temp >= 90°C, or voltage sag <= 31.0 kV.
3. **Safety Gate Enforcement**:
   - Telemetry reading at `13:15` hits 49.6 MVA and 94°C -> classified as `ALARM`.
   - Recommended action: `recommend_emergency_load_shedding_for_dispatcher_signoff`.
   - `auto_executed: False` with governance rationale: *"Automated breaker tripping strictly prohibited; requires human operator verification."*

## How to Run
```bash
python solution.py
```
Output results and telemetry assessments are stored in `output.txt`.

