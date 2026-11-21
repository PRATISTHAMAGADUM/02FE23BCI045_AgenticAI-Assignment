"""
Lab 12: Safety, Evaluation, and Governance -- Assignment 1: A Cost-Category Control

Assignment Requirement:
Add a cost estimate to each proposed action and a budget threshold. Reject any proposal
whose estimated cost exceeds the threshold unless a separate `finance_approved` flag
is set. Write an adversarial test that attempts to bypass this by omitting the cost
estimate entirely, and confirm it is rejected rather than defaulting to approved.
"""

import json

REGRESSION_SUITE_RESULT = {"passed": 9, "total": 10}
DEFAULT_BUDGET_THRESHOLD = 5000.0  # Maximum cost without prior Finance authorization ($5,000)


class GovernedProdChangeAgent:
    permissions = {"can_write": "staging_only"}

    def __init__(self, budget_threshold=DEFAULT_BUDGET_THRESHOLD):
        self.audit_log = []
        self.evaluated = False
        self.budget_threshold = budget_threshold

    def evaluate(self):
        pass_rate = REGRESSION_SUITE_RESULT["passed"] / REGRESSION_SUITE_RESULT["total"]
        self.evaluated = pass_rate >= 0.8
        self._log("evaluation", {"pass_rate": pass_rate, "passed_gate": self.evaluated})
        return self.evaluated

    def _log(self, step, data):
        self.audit_log.append({"step": step, "data": data})

    def propose_change(self, diagnosis, action, rollback_plan, privacy_scrubbed,
                       cost_estimate=None, finance_approved=False):
        """
        Submits a production change proposal subjected to financial and safety guardrails.
        """
        # Baseline Gates
        if not self.evaluated:
            self._log("propose_change", {"rejected": True, "reason": "agent not evaluated"})
            return {"rejected": True, "reason": "Evaluation gate not passed; cannot propose changes."}

        if self.permissions["can_write"] != "staging_only":
            raise PermissionError("Agent must not hold direct production write access.")

        if not privacy_scrubbed:
            self._log("propose_change", {"rejected": True, "reason": "unscrubbed customer data"})
            return {"rejected": True, "reason": "Diagnostic input was not privacy-scrubbed; rejecting."}

        if not rollback_plan:
            self._log("propose_change", {"rejected": True, "reason": "no rollback plan supplied"})
            return {"rejected": True, "reason": "No rollback plan defined; rejecting proposal."}

        # ---- FINANCIAL GOVERNANCE GUARDRAIL ----------------------------------
        # Adversarial bypass guard: cost estimate MUST be provided explicitly
        if cost_estimate is None:
            rejection_reason = (
                "Financial Governance Violation: Cost estimate was omitted. "
                "Omitting financial estimates cannot bypass budget controls. Rejecting proposal."
            )
            self._log("financial_guardrail", {
                "rejected": True,
                "reason": "missing_cost_estimate",
                "adversarial_attempt": True
            })
            return {"rejected": True, "reason": rejection_reason, "code": "COST_ESTIMATE_MISSING"}

        if not isinstance(cost_estimate, (int, float)) or cost_estimate < 0:
            rejection_reason = f"Invalid cost estimate '{cost_estimate}'. Must be a non-negative number."
            self._log("financial_guardrail", {"rejected": True, "reason": "invalid_cost_type"})
            return {"rejected": True, "reason": rejection_reason, "code": "INVALID_COST_ESTIMATE"}

        # Budget Threshold Check
        if cost_estimate > self.budget_threshold and not finance_approved:
            rejection_reason = (
                f"Budget Threshold Exceeded: Estimated cost ${cost_estimate:,.2f} exceeds standard "
                f"threshold of ${self.budget_threshold:,.2f}, and finance_approved flag is False."
            )
            self._log("financial_guardrail", {
                "rejected": True,
                "reason": "budget_exceeded_no_finance_approval",
                "cost_estimate": cost_estimate,
                "budget_threshold": self.budget_threshold
            })
            return {"rejected": True, "reason": rejection_reason, "code": "BUDGET_EXCEEDED"}

        # Proposal accepted for human SRE review
        request = {
            "diagnosis": diagnosis,
            "proposed_action": action,
            "cost_estimate": cost_estimate,
            "finance_approved": finance_approved,
            "budget_threshold": self.budget_threshold,
            "rollback_plan": rollback_plan,
            "category": "production",
            "requires_approval": True,
        }
        self._log("approval_requested", request)
        return request


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 12 - Assignment 1: Cost-Category Financial Governance Guardrails")
    print("================================================================================\n")

    agent = GovernedProdChangeAgent(budget_threshold=5000.0)
    agent.evaluate()

    # 1. Normal Proposal: Within budget ($2,400 < $5,000)
    print("--- 1. Proposal Within Budget ($2,400 <= $5,000 threshold) ---")
    res1 = agent.propose_change(
        diagnosis="Scale staging workers to handle evening surge.",
        action="provision 2 additional r6g.large compute instances",
        rollback_plan="Deprovision instances after queue drains.",
        privacy_scrubbed=True,
        cost_estimate=2400.0,
        finance_approved=False
    )
    print(f"Status: Accepted for Review | Requires Approval: {res1.get('requires_approval')}")
    print(f"Cost: ${res1.get('cost_estimate')}\n")

    # 2. Over-Budget Proposal Without Finance Signoff ($14,500 > $5,000)
    print("--- 2. Proposal Exceeding Budget Without Finance Approval ($14,500 > $5,000) ---")
    res2 = agent.propose_change(
        diagnosis="Migrate cluster to multi-region active-active deployment.",
        action="spin up secondary standby region with multi-AZ replication",
        rollback_plan="Tear down secondary region if latency does not improve.",
        privacy_scrubbed=True,
        cost_estimate=14500.0,
        finance_approved=False
    )
    print(f"Status: REJECTED | Reason: {res2.get('reason')}\n")

    # 3. Over-Budget Proposal With Finance Signoff ($14,500 > $5,000, finance_approved=True)
    print("--- 3. Over-Budget Proposal WITH Finance Approval (finance_approved=True) ---")
    res3 = agent.propose_change(
        diagnosis="Migrate cluster to multi-region active-active deployment.",
        action="spin up secondary standby region with multi-AZ replication",
        rollback_plan="Tear down secondary region if latency does not improve.",
        privacy_scrubbed=True,
        cost_estimate=14500.0,
        finance_approved=True  # Authorized by VP of Finance
    )
    print(f"Status: Accepted for Review | Finance Authorized: {res3.get('finance_approved')}")
    print(f"Cost: ${res3.get('cost_estimate')}\n")

    # 4. ADVERSARIAL TEST: Attempt to bypass budget checks by omitting cost estimate entirely
    print("--- 4. ADVERSARIAL TEST: Omission of Cost Estimate to Bypass Budget Check ---")
    res_adv = agent.propose_change(
        diagnosis="Adversarial cluster re-allocation.",
        action="provision unbounded multi-tenant GPU nodes",
        rollback_plan="Teardown GPUs.",
        privacy_scrubbed=True,
        cost_estimate=None,  # Deliberately omitting cost estimate
        finance_approved=False
    )
    print(f"Adversarial Attempt Result: REJECTED: {res_adv.get('rejected')}")
    print(f"Rejection Code: {res_adv.get('code')}")
    print(f"Rejection Reason: {res_adv.get('reason')}\n")

    assert res_adv["rejected"] is True
    assert res_adv["code"] == "COST_ESTIMATE_MISSING"
    print("=== Verification of Adversarial Security ===")
    print("CONFIRMED: Omitting cost estimate failed closed with structured rejection; cannot bypass financial gate.")

