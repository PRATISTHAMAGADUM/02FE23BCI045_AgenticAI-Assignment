# Lab 8 - Assignment 2: Distributed Critique

## Objective
Replace the monolithic centralized `critique()` function with a distributed multi-agent critique model. Each domain role (`budget`, `research`, `judging`, `logistics`) executes an independent critique of the merged draft against its own domain constraints. The system records an explicit conflict log identifying the specific objecting role, violated constraint, and remediation recommendation.

## Key Implementation Details
1. **Decoupled Critique Handlers**:
   - `critique_budget`: Audits fiscal caps (`venue_cost` vs `budget_cap`).
   - `critique_research`: Audits format feasibility (`target_participants` vs `venue_capacity`, and 24-hr overnight requirements vs `venue_overnight`).
   - `critique_judging`: Audits schedule adequacy for judging windows (`required_demo_hours` vs venue closure time).
2. **Concurrent Distributed Execution**:
   - `run_distributed_critique()` executes all critique handlers in parallel via `ThreadPoolExecutor`.
   - Aggregates objections into a unified conflict log.
3. **Verification**:
   - 3 distinct roles (`budget`, `research`, `judging`) independently raised 4 substantive objections.
   - Every entry explicitly records `objecting_role`, `target`, `objection`, and `recommendation`.

## How to Run
```bash
python solution.py
```
Outputs and distributed critique logs are stored in `output.txt`.

