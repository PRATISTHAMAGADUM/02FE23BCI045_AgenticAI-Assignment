# Lab 7 - Assignment 2: Add a Retry Limit to the Builder Node

## Objective
Enhance the delivery node graph so the `builder` node enforces a strict retry boundary: exactly one automated retry is permitted upon failure. If the retry succeeds, the pipeline continues forward; if the second attempt fails, the graph must cease automated retries and escalate to human engineering support.

## Key Implementation Details
1. **Retry Guard (`MAX_BUILDER_RETRIES = 1`)**:
   - The graph tracks `builder_attempts`.
   - On initial failure (`attempt == 1`), the graph logs `"Retry permitted... Initiating retry 1"`.
   - On subsequent failure (`attempt == 2`), the graph triggers `"NO MORE RETRIES: Attempt 2 exceeded 1 retry limit. Triggering failure behavior: escalate_to_human"`.
2. **Scenarios Demonstrated**:
   - **Scenario A (Fail once -> Retry -> Succeed)**:
     - Attempt 1: Fails due to missing dependency (`fastapi`).
     - Retry 1: Resolves dependency; `build_ok` becomes `True`.
     - Pipeline smoothly completes `tester`, `reviewer`, and `human_gate`.
   - **Scenario B (Fail twice -> Escalate)**:
     - Attempt 1: Fails with AST syntax error.
     - Retry 1: Fails with AST syntax error.
     - Graph halts and escalates directly to human.

## How to Run
```bash
python solution.py
```
Output traces for both scenarios are captured in `output.txt`.

