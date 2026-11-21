# Lab 10 - Assignment 1: A Second Incident Type

## Objective
Model a distinct secondary cloud operational incident: a database connection-pool exhaustion outage. Provide independent log streams, deployment records, and telemetry metrics. Verify that `classify_severity` and `correlate_with_recent_changes` correctly differentiate this incident from the reference payments refund scenario in both severity classification and diagnostic root-cause hypothesis.

## Key Implementation Details
1. **Telemetry & Incident Modeling**:
   - **Scenario 1 (Payments Service)**: `current_error_rate = 1.6%` (ratio 3.2x over baseline) -> Classified as `"degraded"`. Attributed to `RefundHandler` NullPointerException following `payments-service v2.4.1` deploy.
   - **Scenario 2 (DB Pool Exhaustion)**: `current_error_rate = 68.5%` (> 50% threshold) -> Classified as `"down"`. Attributed to `ConnectionTimeoutException` in HikariCP pool following `analytics-worker v3.2.0` deploy.
2. **Correlation Verification**:
   - Incident start detected at `16:03:00`.
   - Affected subsystem flagged as `database connection pool`.
   - Suspect deployment accurately attributed to `analytics-worker v3.2.0`.
3. **Comparative Divergence**: Both incidents produce strictly independent diagnostics and severity ratings.

## How to Run
```bash
python solution.py
```
Outputs and comparative diagnoses are recorded in `output.txt`.

