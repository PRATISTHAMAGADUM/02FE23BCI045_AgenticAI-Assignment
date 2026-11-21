# Lab 12 - Assignment 2: Mandatory Re-Evaluation After N Proposals

## Objective
Enforce an operational safety governance rule requiring mandatory re-evaluation after every 5 proposals made by the change agent. Track the proposal submission count across operational lifecycles, and demonstrate that a 6th proposal is strictly blocked until `evaluate()` is executed again to reset the governance quota.

## Key Implementation Details
1. **Evaluation Cadence Guard**:
   - `max_proposals = 5` and `self.proposals_since_eval` counter.
   - When `self.proposals_since_eval >= 5`, any subsequent proposal is blocked:
     ```python
     if self.proposals_since_eval >= self.max_proposals:
         return {"rejected": True, "code": "MANDATORY_REEVALUATION_REQUIRED", ...}
     ```
2. **Quota Reset via Evaluation**:
   - Calling `agent.evaluate()` runs the diagnostic regression suite and, upon passing, resets `self.proposals_since_eval = 0`.
3. **Execution Verification**:
   - Initial `evaluate()` run: Counter initialized to 0/5.
   - Proposals 1 through 5: Successfully accepted and forwarded to SRE approval.
   - Proposal 6: Strictly rejected with `MANDATORY_REEVALUATION_REQUIRED`.
   - Re-evaluation: `evaluate()` called, resetting the counter.
   - Proposal 6 retry: Successfully submitted and approved for review.

## How to Run
```bash
python solution.py
```
Output traces and governance audit logs are captured in `output.txt`.

