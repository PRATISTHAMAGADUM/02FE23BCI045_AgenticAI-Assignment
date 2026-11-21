"""
Lab 13: Discipline-Specific Engineering Agents -- Assignment 2: Escalate on a Trend, Not Just a Threshold

Assignment Requirement:
Extend the Mechanical agent so that three consecutive WARNING-level readings
(even if none individually reaches ALARM) escalate to a "schedule_inspection"
recommendation instead of "continue_monitoring". Demonstrate this with a modified
sensor log that stays under the ALARM threshold throughout but trends upward for
three readings.
"""

import json

# ISO-10816 Style Thresholds
THRESHOLDS = {
    "vibration_warn": 2.8,
    "vibration_alarm": 4.5,
    "temp_warn": 70.0,
    "temp_alarm": 80.0
}

# ==============================================================================
# Sensor Log A: Stays strictly UNDER ALARM thresholds throughout (vibration < 4.5, temp < 80)
# but exhibits 3 consecutive WARNING-level readings trending upwards.
# ==============================================================================
SUSTAINED_WARNING_TREND_LOG = [
    {"t": 0, "vibration_mm_s": 1.8, "temp_c": 61.0},  # NORMAL
    {"t": 1, "vibration_mm_s": 2.1, "temp_c": 63.0},  # NORMAL
    {"t": 2, "vibration_mm_s": 2.4, "temp_c": 65.0},  # NORMAL
    {"t": 3, "vibration_mm_s": 3.2, "temp_c": 71.0},  # WARNING 1 (vibe >= 2.8, temp >= 70)
    {"t": 4, "vibration_mm_s": 3.7, "temp_c": 74.0},  # WARNING 2 (higher than t=3)
    {"t": 5, "vibration_mm_s": 4.2, "temp_c": 78.0},  # WARNING 3 (higher than t=4, but STILL < 4.5 alarm)
]

# ==============================================================================
# Sensor Log B: Transient Warning (Only 1 warning reading, then stabilizes back to normal)
# ==============================================================================
TRANSIENT_WARNING_LOG = [
    {"t": 0, "vibration_mm_s": 1.8, "temp_c": 61.0},  # NORMAL
    {"t": 1, "vibration_mm_s": 2.0, "temp_c": 62.0},  # NORMAL
    {"t": 2, "vibration_mm_s": 3.0, "temp_c": 71.0},  # WARNING (isolated transient spike)
    {"t": 3, "vibration_mm_s": 2.5, "temp_c": 66.0},  # NORMAL (recovers)
    {"t": 4, "vibration_mm_s": 2.3, "temp_c": 64.0},  # NORMAL
    {"t": 5, "vibration_mm_s": 2.2, "temp_c": 63.0},  # NORMAL
]


def classify_single_reading(reading):
    if reading["vibration_mm_s"] >= THRESHOLDS["vibration_alarm"] or reading["temp_c"] >= THRESHOLDS["temp_alarm"]:
        return "ALARM"
    if reading["vibration_mm_s"] >= THRESHOLDS["vibration_warn"] or reading["temp_c"] >= THRESHOLDS["temp_warn"]:
        return "WARNING"
    return "NORMAL"


def evaluate_temporal_trend(sensor_log, window_size=3):
    """
    Evaluates whether the last `window_size` readings exhibit a continuous
    un-remediated WARNING trend.
    """
    if len(sensor_log) < window_size:
        return {"trend_escalation_triggered": False, "reason": "Insufficient history"}

    recent_window = sensor_log[-window_size:]
    conditions = [classify_single_reading(r) for r in recent_window]

    # Check 1: Are all readings in the window at WARNING level?
    all_warnings = all(c == "WARNING" for c in conditions)

    # Check 2: Are vibration or temperature readings strictly trending upward?
    vibe_trending_up = all(
        recent_window[i]["vibration_mm_s"] <= recent_window[i + 1]["vibration_mm_s"]
        for i in range(len(recent_window) - 1)
    )
    temp_trending_up = all(
        recent_window[i]["temp_c"] <= recent_window[i + 1]["temp_c"]
        for i in range(len(recent_window) - 1)
    )

    is_persistent_warning_trend = all_warnings and (vibe_trending_up or temp_trending_up)

    return {
        "trend_escalation_triggered": is_persistent_warning_trend,
        "window_size": window_size,
        "conditions_in_window": conditions,
        "vibrations_in_window": [r["vibration_mm_s"] for r in recent_window],
        "temperatures_in_window": [r["temp_c"] for r in recent_window],
    }


def analyze_predictive_maintenance(log, scenario_name):
    latest = log[-1]
    latest_condition = classify_single_reading(latest)
    trend_analysis = evaluate_temporal_trend(log, window_size=3)

    # Escalation Rule:
    # 1. Individual ALARM -> recommend_shutdown (human signoff required)
    # 2. 3 Consecutive WARNINGs trending upward -> ESCALATE to schedule_inspection
    # 3. Isolated WARNING -> continue_monitoring with enhanced frequency
    # 4. NORMAL -> continue_monitoring
    if latest_condition == "ALARM":
        recommended_action = "recommend_shutdown_for_human_review"
        auto_execute = False
        decision_reason = "Individual reading exceeded hard ALARM threshold."
    elif trend_analysis["trend_escalation_triggered"]:
        recommended_action = "schedule_inspection"
        auto_execute = False
        decision_reason = (
            f"TREND ESCALATION: 3 consecutive WARNING readings detected ({trend_analysis['vibrations_in_window']} mm/s, "
            f"{trend_analysis['temperatures_in_window']} °C) trending monotonically upward. "
            f"Escalated from continue_monitoring to schedule_inspection prior to ALARM breach."
        )
    elif latest_condition == "WARNING":
        recommended_action = "continue_monitoring"
        auto_execute = True
        decision_reason = "Isolated/transient WARNING; continuing standard monitoring without dispatch."
    else:
        recommended_action = "continue_monitoring"
        auto_execute = True
        decision_reason = "All readings within nominal operating parameters."

    # Confirm safety invariant: check that no individual reading hit ALARM
    any_hit_alarm = any(classify_single_reading(r) == "ALARM" for r in log)

    return {
        "scenario": scenario_name,
        "any_reading_hit_alarm": any_hit_alarm,
        "latest_reading": latest,
        "latest_condition": latest_condition,
        "trend_escalation": trend_analysis["trend_escalation_triggered"],
        "recommended_action": recommended_action,
        "auto_executed": auto_execute,
        "decision_rationale": decision_reason
    }


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 13 - Assignment 2: Predictive Maintenance Trend Escalation (3 Consecutive Warnings)")
    print("================================================================================\n")

    # Run Scenario 1: Sustained 3-Reading Warning Trend
    res_trend = analyze_predictive_maintenance(
        SUSTAINED_WARNING_TREND_LOG,
        "Scenario 1: Sustained Upward Warning Trend (Sub-Alarm)"
    )
    print("=== Evaluation of Scenario 1 (3 Consecutive Warnings) ===")
    print(json.dumps(res_trend, indent=2))

    # Run Scenario 2: Transient Warning Spike
    res_transient = analyze_predictive_maintenance(
        TRANSIENT_WARNING_LOG,
        "Scenario 2: Isolated Transient Spike (Non-Persistent)"
    )
    print("\n=== Evaluation of Scenario 2 (Transient Spike) ===")
    print(json.dumps(res_transient, indent=2))

    # Invariant Checks
    print("\n=== Assignment Invariant Assertions ===")
    assert res_trend["any_reading_hit_alarm"] is False, "Scenario 1 readings must all remain below ALARM!"
    assert res_trend["latest_condition"] == "WARNING", "Latest reading must be WARNING, not ALARM!"
    assert res_trend["recommended_action"] == "schedule_inspection", "Must escalate to schedule_inspection!"
    assert res_transient["recommended_action"] == "continue_monitoring", "Transient spike should not trigger inspection!"

    print("ALL ASSERTIONS PASSED:")
    print("1. Confirmed zero individual readings reached ALARM (max vibration=4.2 < 4.5, max temp=78 < 80).")
    print("2. Confirmed 3 consecutive WARNING readings triggered escalation to 'schedule_inspection'.")
    print("3. Confirmed isolated transient reading safely resolved to 'continue_monitoring'.")

