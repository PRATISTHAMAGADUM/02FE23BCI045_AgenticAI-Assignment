# Lab 11 - Assignment 1: A Second, Concurrent Story with Full Lineage

## Objective
Extend the Agentic SDLC software factory to process two concurrent user stories side by side: `US-1` (CSV Export) and `US-2` (PDF Export). Implement an end-to-end `SDLCLineageTracker` that unambiguously attributes each design document, code module, test suite, and release manifest to its corresponding originating user story.

## Key Implementation Details
1. **Concurrent User Stories**:
   - `US-1`: *"As a user, I can export the current report view as a CSV file, preserving applied filters."*
   - `US-2`: *"As a user, I can export the current report view as a formatted PDF document, preserving applied filters and title header."*
2. **Artifact Generation**:
   - **Design Stage**: Produces `DESIGN-US1-CSV` (CSV serializer, endpoints) and `DESIGN-US2-PDF` (PDF canvas renderer, layout).
   - **Coding Stage**: Produces `CODE-US1-CSV` (`export_csv`) and `CODE-US2-PDF` (`export_pdf`).
   - **Testing Stage**: Independently generates and executes `TEST-US1-CSV` and `TEST-US2-PDF` derived strictly from story acceptance criteria.
3. **Trace Matrix**:
   - The `SDLCLineageTracker` constructs a structured lineage matrix establishing explicit parent-child traceability across all SDLC phases for each story independently.

## How to Run
```bash
python solution.py
```
Outputs and lineage matrices are captured in `output.txt`.

