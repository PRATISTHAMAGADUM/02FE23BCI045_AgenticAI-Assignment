# Lab 7 - Assignment 1: Add a Security-Scan Node

## Objective
Insert a new `security_scan` node into the software delivery graph between the `builder` and `tester` nodes. The node must declare its own input contract (`state['code']`), output schema (`security_clean`, `vulnerabilities`), owner (`security_agent`), success condition (`lambda s: s.get("security_clean", False)`), and failure behavior (`quarantine_build_and_alert_security_team`). Update the simulation harness and generate traces for all execution paths, specifically highlighting a path where the security scan fails.

## Key Implementation Details
1. **Node Insertion**:
   - Placed sequentially between `builder` and `tester`.
   - `tester` stage requires both `build_ok` and `security_clean` to proceed.
2. **Failure Handling**:
   - If vulnerabilities are flagged (e.g., `CWE-89`, `CWE-798`), `security_clean` is set to `False`.
   - Halts pipeline immediately and triggers:
     `"failure_behavior_triggered": "quarantine_build_and_alert_security_team('Vulnerability detected in generated code')"`
3. **Execution Paths Demonstrated**:
   - **Path 1 (Success Path)**: All 7 stages pass cleanly (requirement -> planner -> builder -> security_scan -> tester -> reviewer -> human_gate).
   - **Path 2 (Security Scan Failure)**: Builder passes, but security scan flags SQL injection risks and quarantines the build before tests run.
   - **Path 3 (Builder Failure)**: Builder fails, triggering retry/escalation before security is even invoked.

## How to Run
```bash
python solution.py
```
Outputs for all three paths are stored in `output.txt`.

