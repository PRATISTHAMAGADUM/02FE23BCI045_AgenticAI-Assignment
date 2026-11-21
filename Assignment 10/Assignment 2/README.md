# Lab 10 - Assignment 2: A Safe Auto-Remediation Path

## Objective
Establish a bifurcated operational risk boundary in the Cloud Operations Agent. Low-risk operational remediation actions (such as `restart_single_pod` during an `early_warning` incident) are permitted to auto-execute. Conversely, any destructive or high-blast-radius action (such as `rollback`) is strictly prevented from automated execution—even under explicit urgency conditions—and must always route to human SRE approval.

## Key Implementation Details
1. **Risk-Classified Decision Model**:
   - `LOW_RISK = {"restart_single_pod", "notify", "open_ticket"}`
   - `HIGH_RISK = {"rollback", "scale", "config_change", "delete"}`
2. **Scenario A (WARNING / Early Warning)**:
   - Minor memory spike and unresponsive socket thread detected on `worker-pool-node-4`.
   - Proposed action: `restart_single_pod`.
   - Classified as `LOW_RISK` -> System returns `status: "EXECUTED_AUTOMATICALLY"`, `auto_executed: True`.
3. **Scenario B (CRITICAL / Degraded)**:
   - Payments service NullPointerException regression.
   - Proposed action: `rollback`.
   - Classified as `HIGH_RISK` -> System blocks execution, returning `status: "AWAITING HUMAN APPROVAL -- NOT EXECUTED"`, `auto_executed: False`.
4. **Governance Guarantee**: Verified that even with `urgency_prompt=True`, the safety gate prevents automated rollbacks.

## How to Run
```bash
python solution.py
```
Output results showing both auto-execution and human-gated paths are captured in `output.txt`.

