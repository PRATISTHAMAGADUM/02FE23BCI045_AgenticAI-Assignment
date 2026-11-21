# Lab 13 - Assignment 2: Escalate on a Trend, Not Just a Threshold

## Objective
Extend the Mechanical Engineering Predictive Maintenance agent to evaluate temporal trend patterns across consecutive sensor readings. If the agent detects three consecutive `WARNING`-level readings trending monotonically upward—even when zero individual readings reach the `ALARM` threshold—it must escalate the operational recommendation from `"continue_monitoring"` to `"schedule_inspection"` prior to an actual component breakdown.

## Key Implementation Details
1. **Temporal Trend Analysis (`evaluate_temporal_trend`)**:
   - Inspects a sliding window of the last 3 telemetry samples.
   - Evaluates whether all readings are in `WARNING` state (`vibration >= 2.8 mm/s` or `temp >= 70 °C`) and trending upward (`r[i] <= r[i+1]`).
2. **Scenario 1 (Sustained Sub-Alarm Warning Trend)**:
   - Readings at t=3, 4, 5: `[3.2, 3.7, 4.2]` mm/s and `[71, 74, 78]` °C.
   - Maximum reading (4.2 mm/s, 78 °C) remains strictly below `ALARM` thresholds (4.5 mm/s, 80 °C).
   - Trend engine triggers: `"TREND ESCALATION: 3 consecutive WARNING readings detected... Escalated from continue_monitoring to schedule_inspection prior to ALARM breach."`
3. **Scenario 2 (Transient Spike Contrast)**:
   - Evaluates an isolated spike that self-recovers to nominal operating bounds.
   - Verified that the transient spike does not trigger inspection, safely continuing standard monitoring.

## How to Run
```bash
python solution.py
```
Output results and trend evaluations are captured in `output.txt`.

