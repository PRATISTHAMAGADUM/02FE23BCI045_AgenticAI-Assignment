# Lab 11 - Assignment 2: Prove Test Independence With a Deliberate Bug

## Objective
Introduce a deliberate defect into `coding_agent`'s filtering logic (e.g., inverting comparison criteria to select non-matching records instead of matching records) while leaving the `testing_agent` completely unchanged. Execute the factory pipeline and demonstrate that the independently synthesized test suite catches the regression, rejecting the release and proving that tests evaluate acceptance criteria rather than mirroring implementation quirks.

## Key Implementation Details
1. **Deliberate Regression Injected**:
   - In `coding_agent_with_deliberate_bug`:
     ```python
     # Flawed inverted predicate
     filtered = [r for r in rows if any(r.get(k) != v for k, v in applied_filters.items())]
     ```
   - When filtering for `{"region": "North"}`, the buggy code excluded `North` rows and exported `South,200`.
2. **Untouched Independent Test Suite**:
   - `testing_agent` was preserved without any awareness of the bug.
   - Evaluated generated CSV output against Acceptance Criterion 2 (*"the CSV contains only rows matching the currently applied filters"*).
3. **Pipeline Failure & Human Review Gate**:
   - Test 1 (`produces output`): PASS.
   - Test 2 (`header matches columns`): PASS.
   - Test 3 (`only filtered rows present`): **FAIL (REGRESSION CAUGHT)**.
   - Review agent reported `clean: False`.
   - Human review checkpoint issued a `reject` decision, blocking release deployment.

## How to Run
```bash
python solution.py
```
Outputs and regression failure traces are captured in `output.txt`.

