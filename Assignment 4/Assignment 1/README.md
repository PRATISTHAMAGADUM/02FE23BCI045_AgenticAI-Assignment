# Lab 4 - Assignment 1: A Second, Isolated Topic

## Objective
Extend `ProjectMemory` and `ProjectAssistant` to support multiple distinct architectural topics (e.g., `"database"` and `"hosting"`). Demonstrate in an execution transcript that retrieval scoped to `"database"` never leaks or returns `"hosting"` facts, and vice versa.

## Key Implementation Details
1. **Scoped Topic Partitioning**: `ScopedProjectMemory.retrieve(topic)` performs strict topic filtering:
   ```python
   return [r for r in self.records if r.topic.lower() == topic.lower()]
   ```
2. **Two Isolated Topics Seeded**:
   - `database`: `"we chose PostgreSQL with pgvector"` (dated 2026-07-03)
   - `hosting`: `"we chose AWS ECS Fargate with Terraform"` (dated 2026-07-04)
3. **Cross-Leakage Verification**:
   - Evaluated `db_answer` against hosting keywords (`hosting`, `fargate`, `aws`) -> `False` (zero leakage).
   - Evaluated `hosting_answer` against database keywords (`database`, `postgres`, `sqlite`) -> `False` (zero leakage).
4. **Independent Topic Mutation**: Updating `"hosting"` to `"Google Cloud Run"` mutates only the hosting partition, leaving the database decision completely unchanged.

## How to Run
```bash
python solution.py
```
Outputs and verification assertions are captured in `output.txt`.

