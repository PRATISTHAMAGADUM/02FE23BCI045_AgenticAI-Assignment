# Lab 4 - Assignment 2: A Staleness / Retention Policy

## Objective
Introduce a `retention_days` control and a staleness verification mechanism into the memory retrieval workflow. If a retrieved record's age exceeds the threshold, `ProjectAssistantWithStaleness` must explicitly issue a warning to the user (*"this decision is from N days ago and may be out of date"*) before providing the stored fact.

## Key Implementation Details
1. **Retention Policy Configuration**: Configured `retention_days = 30` and dynamic elapsed-time calculation:
   ```python
   age_days = (self.current_date - rec_date).days
   is_stale = age_days > self.retention_days
   ```
2. **Test Cases Executed**:
   - **Case 1 (Fresh Record)**: Stored 10 days prior (`caching` -> `"we use Redis cluster for session cache"`). Verified within the 30-day window; served cleanly without warning.
   - **Case 2 (Stale Record)**: Stored 120 days prior (`ci_pipeline` -> `"we use Jenkins on dedicated EC2 VMs"`). Exceeds the 30-day threshold; user is explicitly alerted with:
     `[STALENESS WARNING: This decision is from 120 days ago and may be out of date! Configured retention threshold is 30 days.]`

## How to Run
```bash
python solution.py
```
Outputs demonstrating both cases are captured in `output.txt`.

