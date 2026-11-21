# Lab 6 - Assignment 2: Escalate After Two Failures

## Objective
Implement an escalation rule in the agent runtime: if a particular skill fails twice in one session for the same user, any subsequent attempt must escalate to a human operator rather than retrying the skill. Crucially, this must be evaluated directly from the existing immutable `Audit` log without introducing hidden global state variables or private counters.

## Key Implementation Details
1. **Zero-Hidden-State Audit Inspection**:
   - `Audit.count_failures(user, skill_name)` queries prior error entries:
     ```python
     return sum(1 for e in self.entries if e.get("user") == user and e.get("skill") == skill_name and e.get("error") is not None)
     ```
2. **Escalation Logic in Runtime Loop**:
   - Before instantiating or executing `skill.execute()`, the runtime inspects `audit.count_failures(user, skill_name)`.
   - If `prior_errors >= 2`, execution short-circuits with `status: "ESCALATED_TO_HUMAN"`.
   - Logs an escalation record into the audit trail.
3. **Transcript Verification**:
   - Attempt 1: Fails with `ConnectionError` (Audit failure count = 1).
   - Attempt 2: Fails with `ConnectionError` (Audit failure count = 2).
   - Attempt 3: Evaluates audit log, halts automated retry, and escalates to human on-call engineer.

## How to Run
```bash
python solution.py
```
Output results and audit verification are captured in `output.txt`.

