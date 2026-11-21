"""
Lab 13: Discipline-Specific Engineering Agents -- Assignment 1: Electrical Load Forecasting & Fault-Triage Agent

Assignment Requirement:
Implement a parallel agent for the Electrical Engineering example (load forecasting
or fault-triage from sensor/power-consumption data), using a comparable
threshold-based classification approach. Confirm the same human-review safety gate
applies before any ALARM-equivalent recommendation is acted on.
"""

import json

# ---- Electrical Substation Telemetry Log (50 MVA Substation) -----------
ELECTRICAL_SENSOR_LOG = [
    {"t": "12:00", "load_mva": 36.2, "voltage_kv": 33.1, "freq_hz": 50.01, "transformer_temp_c": 68},
    {"t": "12:15", "load_mva": 38.5, "voltage_kv": 32.9, "freq_hz": 49.98, "transformer_temp_c": 71},
    {"t": "12:30", "load_mva": 41.8, "voltage_kv": 32.7, "freq_hz": 49.92, "transformer_temp_c": 75},
    {"t": "12:45", "load_mva": 44.5, "voltage_kv": 32.4, "freq_hz": 49.85, "transformer_temp_c": 82},
    {"t": "13:00", "load_mva": 47.9, "voltage_kv": 31.8, "freq_hz": 49.71, "transformer_temp_c": 89},
    {"t": "13:15", "load_mva": 49.6, "voltage_kv": 30.9, "freq_hz": 49.52, "transformer_temp_c": 94},  # ALARM state
]

# IEEE / Grid Standard Operational Thresholds for 50 MVA Distribution Transformer
ELECTRICAL_THRESHOLDS = {
    "load_warning_mva": 43.0,     # 86% of rated transformer capacity
    "load_alarm_mva": 48.5,       # 97% of rated capacity (thermal breakdown hazard)
    "temp_warning_c": 80.0,
    "temp_alarm_c": 90.0,
    "voltage_alarm_min_kv": 31.0, # Excessive line sag
}


def tool_read_electrical_telemetry():
    return ELECTRICAL_SENSOR_LOG


def classify_electrical_condition(reading):
    """Classifies electrical telemetry against engineering limits."""
    if (reading["load_mva"] >= ELECTRICAL_THRESHOLDS["load_alarm_mva"] or
        reading["transformer_temp_c"] >= ELECTRICAL_THRESHOLDS["temp_alarm_c"] or
        reading["voltage_kv"] <= ELECTRICAL_THRESHOLDS["voltage_alarm_min_kv"]):
        return "ALARM"
    
    if (reading["load_mva"] >= ELECTRICAL_THRESHOLDS["load_warning_mva"] or
        reading["transformer_temp_c"] >= ELECTRICAL_THRESHOLDS["temp_warning_c"]):
        return "WARNING"

    return "NORMAL"


def electrical_load_trend(log):
    """Calculates load derivative (dLoad/dt) across recent readings."""
    deltas = [log[i + 1]["load_mva"] - log[i]["load_mva"] for i in range(len(log) - 1)]
    avg_growth_rate = sum(deltas) / len(deltas)
    trend_type = "RAPID_SURGE" if avg_growth_rate > 2.0 else ("STEADY_INCREASE" if avg_growth_rate > 0 else "STABLE")
    return {
        "trend_type": trend_type,
        "avg_growth_mva_per_15min": round(avg_growth_rate, 2),
        "consecutive_increases": all(d > 0 for d in deltas)
    }


def electrical_safety_check(condition):
    """
    CRITICAL SAFETY GATE:
    An ALARM condition in electrical distribution (e.g., rolling blackout load shedding)
    MUST NEVER be triggered automatically by an AI agent. Mandatory human grid dispatcher
    sign-off is required before any feeder trip or circuit interruption is initiated.
    """
    if condition == "ALARM":
        return {
            "action_allowed": "recommend_emergency_load_shedding_for_dispatcher_signoff",
            "auto_execute": False,
            "safety_rationale": "High-impact grid stability action: Automated breaker tripping strictly prohibited; requires human operator verification."
        }
    if condition == "WARNING":
        return {
            "action_allowed": "dispatch_demand_response_and_auxiliary_cooling",
            "auto_execute": False,
            "safety_rationale": "Advisory action: Operator alerted to enable secondary cooling pumps and curtail flexible industrial loads."
        }
    return {
        "action_allowed": "continue_economic_dispatch_monitoring",
        "auto_execute": True,
        "safety_rationale": "Nominal operations: Automated telemetry logging active."
    }


def electrical_load_agent():
    log = tool_read_electrical_telemetry()
    latest = log[-1]
    condition = classify_electrical_condition(latest)
    trend = electrical_load_trend(log)
    safety = electrical_safety_check(condition)

    return {
        "domain": "Electrical Engineering -- Load Forecasting & Grid Substation Fault Triage",
        "substation_id": "Substation-4A (North Hub 33kV/11kV)",
        "rated_capacity_mva": 50.0,
        "latest_reading": latest,
        "condition": condition,
        "trend_analysis": trend,
        "recommended_action": safety["action_allowed"],
        "auto_executed": safety["auto_execute"],
        "safety_governance": safety["safety_rationale"],
        "engineering_standard": "IEEE C57.91-style loading guide for power transformers with dynamic thermal tracking"
    }


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 13 - Assignment 1: Electrical Engineering Agent (Load Forecasting & Fault Triage)")
    print("================================================================================\n")

    result = electrical_load_agent()

    print("=== Electrical Grid Agent Assessment ===")
    for k, v in result.items():
        if isinstance(v, dict):
            print(f"{k}:")
            for sub_k, sub_v in v.items():
                print(f"  {sub_k}: {sub_v}")
        else:
            print(f"{k}: {v}")

    # Verify Human Safety Gate
    print("\n=== Verification of Safety Gate Enforcement ===")
    assert result["condition"] == "ALARM"
    assert result["auto_executed"] is False
    print("CONFIRMED: Electrical ALARM condition correctly routed to human grid dispatcher. Auto-execute is FALSE.")

