# Lab 6 - Assignment 1: Add Per-User Rate Limiting

## Objective
Enforce a runtime rate-limiting control restricting each user to a maximum of 3 tasks per session. The check must be implemented inside `receive_task` (or a wrapper) without altering `run_task`'s core loop signature or skill-dispatch mechanics. Demonstrate in an execution transcript that a 4th task from the same user is rejected.

## Key Implementation Details
1. **Rate Limiter Guard**:
   - `USER_TASK_COUNTS = defaultdict(int)` tracks executions per user ID.
   - Inside `receive_task(task, user, memory, audit)`, before delegating to `run_task`:
     ```python
     if USER_TASK_COUNTS[user] >= MAX_TASKS_PER_USER:
         err_msg = f"RateLimitExceeded: User '{user}' has reached the maximum allowed limit of {MAX_TASKS_PER_USER} tasks per session."
         audit.log(task, task.get("skill", "unknown"), [], error=err_msg)
         raise RuntimeError(err_msg)
     ```
2. **Core Loop Preservation**: The `run_task` function, skill instantiation, and dynamic dispatch are left 100% untouched.
3. **Multi-User Quota Independence**: Verified that when user `uday` reaches 3 tasks and gets blocked on task 4, user `priya` can still execute tasks against their own independent quota.
4. **Audit Logging**: The blocked 4th task attempt is immutably logged into the audit trail with `Status: ERROR`.

## How to Run
```bash
python solution.py
```
Output results and audit records are captured in `output.txt`.

