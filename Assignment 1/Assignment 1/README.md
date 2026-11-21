# Lab 1 - Assignment 1: Two Rounds of Feedback

## Objective
Extend the `StudyPlannerAgent` reference implementation to accept a second, independent round of user feedback after the first revision (e.g., *"Also make Friday's session shorter, only one hour"*). Crucially, both revisions must mutate the same plan object in memory without restarting the loop or regenerating the schedule from scratch. The iteration log must record two distinct revision iterations with clear stop reasons.

## Key Implementation Details
1. **In-Place Mutation**: `StudyPlannerAgent.revise(feedback, round_num)` directly updates `self.plan["Tuesday"]["time"]` in Round 1 and `self.plan["Friday"]` (shortening duration to 1 hour, `17:00-18:00`) in Round 2.
2. **Object Identity Verification**: Verified that `id(agent.plan)` remains strictly identical across initial plan generation, round 1 revision, and round 2 revision.
3. **Structured Audit Log**:
   - Iterations 1–5: Goal initialization, information gathering (`ask`), schedule reading (`read_existing_schedule`), and initial plan generation.
   - Iterations 6–7: Round 1 revision logged with action `"mutated existing plan in place for round 1"` and stop reason `"round 1 revision applied without restarting loop"`.
   - Iterations 8–9: Round 2 revision logged with action `"mutated existing plan in place for round 2"` and stop reason `"round 2 revision applied without restarting loop"`.

## How to Run
```bash
python solution.py
```
The full execution transcript is captured in `output.txt`.

