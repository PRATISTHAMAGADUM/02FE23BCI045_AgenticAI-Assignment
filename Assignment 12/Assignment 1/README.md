# Lab 12 - Assignment 1: A Cost-Category Control

## Objective
Incorporate a cost estimation and financial governance guardrail into the production change control pipeline. Proposed modifications with costs exceeding a configurable budget threshold (e.g., $5,000) must be rejected unless explicitly accompanied by a `finance_approved=True` authorization. Implement an adversarial test attempting to bypass the budget check by omitting the cost estimate, confirming that the system fails closed with a structured error.

## Key Implementation Details
1. **Financial Governance Guardrail**:
   - `cost_estimate`: Enforced as mandatory non-negative numeric input.
   - If `cost_estimate > self.budget_threshold` and not `finance_approved`:
     Proposal is rejected with error code `BUDGET_EXCEEDED`.
   - If `finance_approved` is provided, high-cost initiatives ($14,500) are permitted to proceed to human SRE review.
2. **Adversarial Bypass Test (Fail-Closed Enforcement)**:
   - Evaluated a request with `cost_estimate=None` designed to evade comparison thresholds.
   - The agent strictly rejects the request with `code: "COST_ESTIMATE_MISSING"` and reason: *"Financial Governance Violation: Cost estimate was omitted. Omitting financial estimates cannot bypass budget controls."*
3. **Audit Trail**: Every financial decision and adversarial attempt is logged in `self.audit_log`.

## How to Run
```bash
python solution.py
```
Outputs and adversarial test records are captured in `output.txt`.

