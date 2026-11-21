"""
Lab 10: Cloud Operations Agent -- Assignment 1: A Second Incident Type (DB Connection Pool Exhaustion)

Assignment Requirement:
Add a second scenario: a database connection-pool exhaustion incident, with its own
log lines, deploy history, and metrics. Confirm `classify_severity` and
`correlate_with_recent_changes` correctly produce a different diagnosis and severity
than the reference payments-service scenario.
"""

import json

# ==============================================================================
# Scenario 1 (Reference): Payments Service Refund Handler Regression
# ==============================================================================
SCENARIO_1_LOGS = [
    {"ts": "14:00:00", "level": "INFO", "msg": "deploy started: payments-service v2.4.1"},
    {"ts": "14:00:45", "level": "INFO", "msg": "deploy completed: payments-service v2.4.1"},
    {"ts": "14:03:10", "level": "WARN", "msg": "refund endpoint latency elevated"},
    {"ts": "14:03:40", "level": "ERROR", "msg": "refund endpoint: NullPointerException in RefundHandler"},
    {"ts": "14:04:05", "level": "ERROR", "msg": "refund endpoint: NullPointerException in RefundHandler"},
    {"ts": "14:04:30", "level": "ERROR", "msg": "refund endpoint: NullPointerException in RefundHandler"},
]
SCENARIO_1_DEPLOYS = [
    {"ts": "14:00:00", "service": "payments-service", "version": "v2.4.1", "prev_version": "v2.4.0"},
]
SCENARIO_1_METRICS = {"baseline_error_rate": 0.5, "current_error_rate": 1.6}  # ratio 3.2x -> degraded


# ==============================================================================
# Scenario 2 (New): Database Connection-Pool Exhaustion (Down / Outage)
# ==============================================================================
SCENARIO_2_LOGS = [
    {"ts": "16:00:00", "level": "INFO", "msg": "deploy completed: analytics-worker v3.2.0"},
    {"ts": "16:02:15", "level": "WARN", "msg": "HikariCP pool utilization exceeded 95% (95/100 active leases)"},
    {"ts": "16:03:00", "level": "ERROR", "msg": "database pool exhausted: ConnectionTimeoutException in UserAuthRepository"},
    {"ts": "16:03:15", "level": "ERROR", "msg": "database pool exhausted: ConnectionTimeoutException in OrderService"},
    {"ts": "16:03:45", "level": "ERROR", "msg": "database pool exhausted: Unable to acquire connection within 30000ms"},
]
SCENARIO_2_DEPLOYS = [
    {"ts": "16:00:00", "service": "analytics-worker", "version": "v3.2.0", "prev_version": "v3.1.9"},
]
SCENARIO_2_METRICS = {"baseline_error_rate": 0.2, "current_error_rate": 68.5}  # > 50% -> down


# ---- Diagnostic Engine --------------------------------------------------
def classify_severity(metrics):
    ratio = metrics["current_error_rate"] / metrics["baseline_error_rate"]
    if metrics["current_error_rate"] > 50:
        return "down"
    if ratio >= 2:
        return "degraded"
    return "early_warning"


def find_incident_start(logs):
    for entry in logs:
        if entry["level"] == "ERROR":
            return entry["ts"]
    return None


def correlate_with_recent_changes(logs, deploys, incident_start):
    error_msgs = [l["msg"] for l in logs if l["level"] == "ERROR"]

    # Identify affected subsystem
    if any("pool exhausted" in m.lower() or "connectiontimeout" in m.lower() for m in error_msgs):
        affected_path = "database connection pool"
    elif any("refund" in m.lower() for m in error_msgs):
        affected_path = "refund"
    else:
        affected_path = "unknown"

    for d in deploys:
        if d["ts"] <= incident_start:
            return {
                "hypothesis": (
                    f"Outage/degradation rose sharply starting {incident_start}, shortly after the "
                    f"{d['ts']} deployment of {d['service']} {d['version']}. Failures originate from "
                    f"{affected_path}, indicating an unclosed connection leak or resource contention "
                    f"introduced in that release."
                ),
                "suspect_deploy": d,
                "affected_path": affected_path,
            }
    return {
        "hypothesis": "No recent deploy correlates with the incident window.",
        "suspect_deploy": None,
        "affected_path": affected_path
    }


def diagnose(logs, deploys, metrics, scenario_name):
    severity = classify_severity(metrics)
    start_time = find_incident_start(logs)
    correlation = correlate_with_recent_changes(logs, deploys, start_time)

    return {
        "scenario": scenario_name,
        "severity": severity,
        "incident_start": start_time,
        "affected_path": correlation["affected_path"],
        "suspect_deploy": f"{correlation['suspect_deploy']['service']} {correlation['suspect_deploy']['version']}",
        "hypothesis": correlation["hypothesis"]
    }


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 10 - Assignment 1: Database Connection-Pool Exhaustion Incident")
    print("================================================================================\n")

    diag_1 = diagnose(SCENARIO_1_LOGS, SCENARIO_1_DEPLOYS, SCENARIO_1_METRICS, "Scenario 1: Payments Refund Error")
    diag_2 = diagnose(SCENARIO_2_LOGS, SCENARIO_2_DEPLOYS, SCENARIO_2_METRICS, "Scenario 2: DB Pool Exhaustion")

    print("=== Diagnostic Comparison ===")
    print(f"Scenario 1:\n{json.dumps(diag_1, indent=2)}\n")
    print(f"Scenario 2:\n{json.dumps(diag_2, indent=2)}\n")

    print("=== Verification of Divergent Diagnosis & Severity ===")
    print(f"Severity Check: Scenario 1='{diag_1['severity']}' vs Scenario 2='{diag_2['severity']}' (Different: {diag_1['severity'] != diag_2['severity']})")
    print(f"Subsystem Check: Scenario 1='{diag_1['affected_path']}' vs Scenario 2='{diag_2['affected_path']}' (Different: {diag_1['affected_path'] != diag_2['affected_path']})")
    print(f"Deploy Check: Scenario 1='{diag_1['suspect_deploy']}' vs Scenario 2='{diag_2['suspect_deploy']}' (Different: {diag_1['suspect_deploy'] != diag_2['suspect_deploy']})")
    assert diag_1["severity"] == "degraded" and diag_2["severity"] == "down"
    print("\nSUCCESS: Database connection-pool exhaustion produced distinct 'down' severity and accurate subsystem attribution.")

