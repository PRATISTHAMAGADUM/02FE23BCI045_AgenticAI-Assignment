# Lab 1 - Assignment 2: Detect a Scheduling Conflict

## Objective
Extend `read_existing_schedule` to return multiple busy days (e.g., Wednesday and Friday) and introduce a conflict-detection check before finalizing the plan. If the student's declared unavailable days (e.g., Sunday only) do not cover all external busy commitments discovered by the calendar tool, the agent must explicitly detect and flag the clash to the user rather than silently double-booking.

## Key Implementation Details
1. **Extended Tool Data**: `read_existing_schedule()` now returns multiple busy days: `["Wednesday", "Friday"]` along with specific commitment details (exam, hackathon preparation).
2. **Conflict Detection Guard**: Added `detect_conflicts(busy_info)` method in `StudyPlannerAgentWithConflictDetection` that computes the difference between tool-discovered busy days and student-declared unavailable days.
3. **Transparent Reporting**:
   - Conflicts are explicitly warned in the terminal prior to finalizing the plan.
   - Flagged conflicts are logged in the agent audit trail.
   - The generated schedule highlights conflicting days with `status: "CONFLICT_FLAGGED_NEEDS_REVIEW"` and attaches clear descriptive notes instead of silently double-booking the slot.

## How to Run
```bash
python solution.py
```
The full execution transcript showing conflict detection and warning output is stored in `output.txt`.

