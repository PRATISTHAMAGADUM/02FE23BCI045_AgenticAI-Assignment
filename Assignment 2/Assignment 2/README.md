# Lab 2 - Assignment 2: A Three-Tool Chain

## Objective
Extend `CampusDataAssistant` and the event sign-ups dataset to incorporate a `category` dimension (e.g., `"technical"`, `"social"`, `"academic"`). Implement support for answering *"What's the average sign-up for technical events only?"* by chaining three distinct tools:
1. `read_csv`: Ingest raw rows from data storage.
2. `filter_by_category`: Filter records by the target category and validate that the output subset is non-empty.
3. `calculator`: Compute the mean on the validated subset of sign-up numbers.

## Key Implementation Details
1. **Schema Extension**: Added a `category` column to `EXTENDED_SIGNUPS_CSV`.
2. **Intermediate Filter Tool**: Added `filter_by_category(rows, category)` with an explicit validation check: returns an error if no rows match the given category.
3. **Execution Chain**:
   - Step 1: `read_csv` reads 7 rows.
   - Step 2: `filter_by_category` extracts the 4 technical events (`AI Club Talk`, `Hackathon Kickoff`, `Robotics Demo`, `GenAI Workshop`).
   - Step 3: `calculator(operation="average", values=[12, 9, 15, 7])` yields `10.75`.
4. **Validation Guard Demonstration**: Querying for a non-existent category (`"athletic"`) demonstrates the fail-safe behavior: the pipeline safely halts at Step 2 with `filter_by_category failed: no records found matching category 'athletic'` without invoking the calculator on empty data.

## How to Run
```bash
python solution.py
```
Outputs and full trace are captured in `output.txt`.

