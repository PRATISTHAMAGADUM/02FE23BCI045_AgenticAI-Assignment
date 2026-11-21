"""
Lab 12: Safety, Evaluation, and Governance -- Assignment 2: Mandatory Re-Evaluation After N Proposals

Assignment Requirement:
Add a rule that the agent must be re-evaluated (call `evaluate()` again) after every
5 proposals it has made. Track the proposal count, and demonstrate a 6th proposal
being blocked with a clear message until `evaluate()` is called again.
"""

import json

REGRESSION_SUITE_RESULT = {"passed": 9, "total": 10}
MAX_PROPOSALS_BEFORE_REEVALUATION = 5


class PeriodicEvaluationAgent:
    permissions = {"can_write": "staging_only"}

    def __init__(self, max_proposals=MAX_PROPOSALS_BEFORE_REEVALUATION):
        self.audit_log = []
        self.evaluated = False
        self.evaluation_count = 0
        self.proposals_since_eval = 0
        self.max_proposals = max_proposals

    def evaluate(self):
        """
        Executes formal evaluation suite.
        Resets proposal counter upon passing the gate.
        """
        pass_rate = REGRESSION_SUITE_RESULT["passed"] / REGRESSION_SUITE_RESULT["total"]
        self.evaluated = pass_rate >= 0.8
        self.evaluation_count += 1
        self.proposals_since_eval = 0  # Reset quota counter

        self._log("evaluation", {
            "evaluation_run": self.evaluation_count,
            "pass_rate": pass_rate,
            "passed_gate": self.evaluated,
            "counter_reset_to": 0
        })
        return self.evaluated

    def _log(self, step, data):
        self.audit_log.append({"step": step, "data": data})

    def propose_change(self, diagnosis, action, rollback_plan, privacy_scrubbed=True):
        # 1. Base Evaluation check
        if not self.evaluated:
            return {"rejected": True, "reason": "Evaluation gate not passed; cannot propose changes."}

        # 2. Mandatory Re-Evaluation Cadence Check
        if self.proposals_since_eval >= self.max_proposals:
            rejection_msg = (
                f"GOVERNANCE BLOCK: Mandatory re-evaluation required! Agent has submitted "
                f"{self.proposals_since_eval} proposals since last evaluation (max allowed: {self.max_proposals}). "
                f"All further proposals are blocked until evaluate() is re-executed."
            )
            self._log("proposal_blocked_cadence", {
                "proposals_since_eval": self.proposals_since_eval,
                "threshold": self.max_proposals,
                "reason": "evaluation_stale"
            })
            return {
                "rejected": True,
                "code": "MANDATORY_REEVALUATION_REQUIRED",
                "proposals_count": self.proposals_since_eval,
                "max_allowed": self.max_proposals,
                "reason": rejection_msg
            }

        if not rollback_plan:
            return {"rejected": True, "reason": "No rollback plan defined."}

        # Record valid proposal and increment quota counter
        self.proposals_since_eval += 1
        request = {
            "proposal_index": self.proposals_since_eval,
            "diagnosis": diagnosis,
            "proposed_action": action,
            "rollback_plan": rollback_plan,
            "category": "production",
            "status": "APPROVAL_REQUESTED",
            "proposals_remaining_in_cycle": self.max_proposals - self.proposals_since_eval
        }
        self._log("proposal_accepted", request)
        return request


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 12 - Assignment 2: Mandatory Re-Evaluation After Every 5 Proposals")
    print("================================================================================\n")

    agent = PeriodicEvaluationAgent(max_proposals=5)

    print("--- Step 1: Initial System Evaluation ---")
    eval_ok = agent.evaluate()
    print(f"Evaluation Run #1 Passed: {eval_ok} | Proposals counter: {agent.proposals_since_eval}/5\n")

    # Submit 5 proposals in cycle 1
    print("--- Step 2: Submitting Proposals 1 Through 5 (Allowed Quota) ---")
    for i in range(1, 6):
        res = agent.propose_change(
            diagnosis=f"Issue #{i}: Database index fragmentation detected on table users_{i}.",
            action=f"REINDEX TABLE CONCURRENTLY users_{i}",
            rollback_plan=f"Drop and restore previous index on users_{i} if latency increases.",
        )
        print(f"  Proposal #{i}: {res['status']} | Cycle remaining: {res['proposals_remaining_in_cycle']}")

    # Submit 6th proposal (Should be BLOCKED)
    print("\n--- Step 3: Submitting 6th Proposal (Exceeds Cadence Threshold) ---")
    res_6 = agent.propose_change(
        diagnosis="Issue #6: Redis cache eviction rate elevated.",
        action="Increase maxmemory policy to volatile-lru",
        rollback_plan="Revert maxmemory policy to allkeys-lru.",
    )
    print(f"Proposal #6 Verdict: REJECTED={res_6.get('rejected')}")
    print(f"Error Code: {res_6.get('code')}")
    print(f"Rejection Message:\n  >>> {res_6.get('reason')} <<<\n")

    assert res_6["rejected"] is True
    assert res_6["code"] == "MANDATORY_REEVALUATION_REQUIRED"

    # Step 4: Re-evaluate agent
    print("--- Step 4: Operator Triggers Mandatory Re-Evaluation (evaluate()) ---")
    reeval_ok = agent.evaluate()
    print(f"Evaluation Run #2 Passed: {reeval_ok} | Proposals counter reset to: {agent.proposals_since_eval}/5\n")

    # Step 5: Retry 6th proposal after re-evaluation
    print("--- Step 5: Re-submitting Proposal #6 Following Successful Re-Evaluation ---")
    res_6_retry = agent.propose_change(
        diagnosis="Issue #6: Redis cache eviction rate elevated.",
        action="Increase maxmemory policy to volatile-lru",
        rollback_plan="Revert maxmemory policy to allkeys-lru.",
    )
    print(f"Proposal #6 Retry Verdict: {res_6_retry['status']} | Cycle remaining: {res_6_retry['proposals_remaining_in_cycle']}")
    assert res_6_retry.get("status") == "APPROVAL_REQUESTED"

    print("\n=== Audit Log Entries for Governance Cadence ===")
    for entry in agent.audit_log:
        if "cadence" in entry["step"] or "evaluation" in entry["step"]:
            print(f"  [{entry['step']}]: {entry['data']}")

    print("\nSUCCESS: 6th proposal blocked until evaluate() called; quota counter correctly enforces governance cycle.")

