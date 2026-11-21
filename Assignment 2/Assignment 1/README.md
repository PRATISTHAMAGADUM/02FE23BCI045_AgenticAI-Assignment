# Lab 2 - Assignment 1: Notification Tool with Justified Use

## Objective
Add a fourth tool, `send_notification(message, recipient_group)`, to `CampusDataAssistant` that drafts a notification message without performing external network calls. When the computed average sign-ups fall below a predefined threshold (e.g., 10.0), the assistant must call this tool to draft an alert for event organizers, explicitly recording in the execution trace *why* the tool was needed.

## Key Implementation Details
1. **Tool Contract (`send_notification`)**:
   - Accepts `message` and optional `recipient_group`.
   - Returns a structured dictionary with `status: "DRAFT_CREATED"` and `dispatched: False`.
   - Strictly isolated from external messaging services.
2. **Threshold Guard**:
   - Compares the calculated average against `self.low_turnout_threshold` (10.0).
   - If turnout is low (demonstrated with average 6.50), triggers `_call("send_notification", reason=...)`.
   - The trace explicitly captures the reason: `"average turnout (6.50) is below threshold (10.0); drafting organizer alert"`.
3. **Trace Justification**:
   - Both normal turnout and low turnout scenarios are executed.
   - The trace shows tool 7 (`send_notification`) only firing when justified by data.

## How to Run
```bash
python solution.py
```
Outputs and full trace are captured in `output.txt`.

