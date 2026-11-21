"""
Lab 10: Cloud Operations Agent -- Assignment 2: Safe Auto-Remediation Path

Assignment Requirement:
Add a WARNING-level (not ALARM/degraded-critical) scenario where the proposed action
is a low-risk `restart_single_pod`. Demonstrate that this low-risk action is allowed
to execute automatically (per `risk_level`), while any rollback-class action anywhere
in your extended code still always routes through the approval-request path and never
auto-executes. Submit updated code and output.
"""

import json

# ==============================================================================
# Scenario 1 (WARNING Level): Transient Memory Spike / Single Pod Zombie Thread
# ==============================================================================
WARNING_LOGS = [
    {"ts": "11:15:00", "level": "INFO", "msg": "worker-pool-node-4: JVM heap usage 74%"},
    {"ts": "11:18:20", "level": "WARN", "msg": "worker-pool-node-4: minor GC pause exceeded 400ms"},
    {"ts": "11:20:00", "level": "WARN", "msg": "worker-pool-node-4: thread stuck in socketRead0, 1 unresponsive pod detected"},
]
WARNING_DEPLOYS = [
    {"ts": "08:00:00", "service": "worker-pool", "version": "v1.2.0", "prev_version": "v1.1.9"}
]
# Error rate ratio = 0.35 / 0.3 = 1.16x (< 2x, < 50%) -> "early_warning"
WARNING_METRICS = {"baseline_error_rate": 0.3, "current_error_rate": 0.35}


# ==============================================================================
# Scenario 2 (CRITICAL Level): Production Regression Requiring Rollback
# ==============================================================================
CRITICAL_LOGS = [
    {"ts": "14:00:45", "level": "INFO", "msg": "deploy completed: payments-service v2.4.1"},
    {"ts": "14:03:40", "level": "ERROR", "msg": "refund endpoint: NullPointerException in RefundHandler"},
    {"ts": "14:04:30", "level": "ERROR", "msg": "refund endpoint: NullPointerException in RefundHandler"},
]
CRITICAL_DEPLOYS = [
    {"ts": "14:00:00", "service": "payments-service", "version": "v2.4.1", "prev_version": "v2.4.0"}
]
CRITICAL_METRICS = {"baseline_error_rate": 0.5, "current_error_rate": 2.5}  # ratio 5.0x -> "degraded"


# ---- Policy & Risk Classification --------------------------------------
def classify_severity(metrics):
    ratio = metrics["current_error_rate"] / metrics["baseline_error_rate"]
    if metrics["current_error_rate"] > 50:
        return "down"
    if ratio >= 2:
        return "degraded"
    return "early_warning"


def risk_level(action):
    HIGH_RISK = {"rollback", "scale", "config_change", "delete"}
    LOW_RISK = {"open_ticket", "notify", "restart_single_pod"}
    if action in HIGH_RISK:
        return "high"
    if action in LOW_RISK:
        return "low"
    return "unknown"


def draft_approval_request(diagnosis, action, rollback_plan):
    return {
        "status": "AWAITING HUMAN APPROVAL -- NOT EXECUTED",
        "diagnosis": diagnosis,
        "proposed_action": action,
        "risk_classification": "HIGH_RISK",
        "risk_mitigation": "Requires SRE manual signoff to prevent unintended traffic disruption.",
        "rollback_plan": rollback_plan,
        "auto_executed": False
    }


def execute_low_risk_remediation(action, target_pod="worker-pool-node-4"):
    """Simulates safe automated execution for low-risk actions."""
    return {
        "status": "EXECUTED_AUTOMATICALLY",
        "action": action,
        "target": target_pod,
        "risk_classification": "LOW_RISK",
        "result": f"Successfully issued restart signal to '{target_pod}'. Health checks returned PASS in 12s.",
        "auto_executed": True
    }


def run_ops_agent(logs, deploys, metrics, scenario_name, force_urgent=False):
    severity = classify_severity(metrics)
    
    if severity == "early_warning":
        proposed_action = "restart_single_pod"
        diagnosis = "Transient stuck socket thread on worker-pool-node-4; early warning threshold met."
    else:
        proposed_action = "rollback"
        diagnosis = "Sustained high error rate spike in payments-service following v2.4.1 deployment."

    action_risk = risk_level(proposed_action)

    print(f"=== {scenario_name} ===")
    print(f"  Severity:        {severity.upper()}")
    print(f"  Proposed Action: {proposed_action} (Risk: {action_risk.upper()})")

    # Safety Gate Decision Engine
    if action_risk == "high":
        # Hard Human-in-the-Loop boundary
        approval_envelope = draft_approval_request(
            diagnosis, proposed_action,
            rollback_plan=f"Revert payments-service to v2.4.0."
        )
        if force_urgent:
            approval_envelope["governance_note"] = "URGENCY DETECTED: Automated execution still strictly prohibited for high-risk action!"
        return {"severity": severity, "decision": approval_envelope}

    elif action_risk == "low":
        # Safe auto-remediation path
        execution_envelope = execute_low_risk_remediation(proposed_action)
        return {"severity": severity, "decision": execution_envelope}

    raise ValueError(f"Unmapped risk level: {action_risk}")


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 10 - Assignment 2: Safe Auto-Remediation vs High-Risk Human Review Gate")
    print("================================================================================\n")

    # Test 1: Low-risk WARNING scenario
    res_warning = run_ops_agent(
        WARNING_LOGS, WARNING_DEPLOYS, WARNING_METRICS,
        scenario_name="Scenario A: Minor Memory Spike / Pod Hang (WARNING)"
    )
    print("Agent Output Envelope:")
    print(json.dumps(res_warning, indent=2))
    assert res_warning["decision"]["auto_executed"] is True
    print("Verified: Low-risk 'restart_single_pod' executed automatically without human intervention.\n")

    # Test 2: High-risk rollback scenario with urgency prompt
    res_critical = run_ops_agent(
        CRITICAL_LOGS, CRITICAL_DEPLOYS, CRITICAL_METRICS,
        scenario_name="Scenario B: Payments Service Degradation (CRITICAL)",
        force_urgent=True
    )
    print("Agent Output Envelope:")
    print(json.dumps(res_critical, indent=2))
    assert res_critical["decision"]["auto_executed"] is False
    assert res_critical["decision"]["status"] == "AWAITING HUMAN APPROVAL -- NOT EXECUTED"
    print("Verified: High-risk 'rollback' blocked from auto-execution and routed to approval gate.")

