# Lab 8 - Assignment 1: Add a Fifth Role: Marketing

## Objective
Extend the parallel multi-agent hackathon planning swarm by adding a fifth concurrent agent: `marketing_agent`. The marketing agent submits a publicity campaign proposal with an associated cost. Extend the `critique()` engine to detect budgetary collisions between marketing spend and the overall fiscal cap, and resolve all conflicts using the established `budget_over_preference` prioritization policy.

## Key Implementation Details
1. **Fifth Swarm Agent (`marketing_agent`)**:
   - Executes concurrently via `ThreadPoolExecutor(max_workers=5)`.
   - Proposes a high-reach marketing blitz costing 12,000.
2. **Merged Plan Integration**:
   - `merge()` captures `marketing_campaign` and `marketing_cost`.
   - Total requested spend across logistics (45,000) and marketing (12,000) totals 57,000, creating severe budgetary pressure against the 30,000 cap.
3. **Multi-Constraint Critique Engine**:
   - Detects 3 explicit conflict dimensions:
     - Venue cost exceeds budget cap (Logistics vs Budget).
     - Marketing cost exceeds allowable allocation ceiling (Marketing vs Budget).
     - Total combined spend (57,000) exceeds total budget (57,000 > 30,000).
4. **Resolution via `budget_over_preference`**:
   - Marketing spend is curtailed from 12,000 down to 3,000 utilizing organic university channels.
   - All resolutions are structured into an extended JSON conflict log artifact.

## How to Run
```bash
python solution.py
```
Output results and the extended conflict log are captured in `output.txt`.

