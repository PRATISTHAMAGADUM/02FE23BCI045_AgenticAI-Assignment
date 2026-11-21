"""
Lab 2: Tool-Using Agent -- Assignment 1: Add a Notification Tool with Justified Use

Assignment Requirement:
Add a fourth tool, `send_notification(message)`, that only drafts a message
(it must not actually send anything). Extend the assistant so that when the
computed average sign-ups falls below a threshold you define (e.g. 10, or 15),
it calls this tool to draft a low-turnout notice, and states in the trace why
the tool was needed. Submit the updated code and a transcript showing the
notification being drafted with its justification.
"""

import csv
import io
import json

# Standard CSV data
SIGNUPS_CSV = """event,signups
AI Club Talk,12
Hackathon Kickoff,9
Robotics Demo,15
GenAI Workshop,7
Capstone Expo,20
Career Panel,11
"""

# Low-turnout CSV data for testing threshold trigger
LOW_TURNOUT_CSV = """event,signups
Morning Study Jam,5
Resume Review,8
Webinar on Git,6
Coding Office Hours,7
"""

MOCK_EVENTS_API_DB = {
    "AI Club Talk": {"date": "2026-07-02", "location": "CS Block Auditorium"},
    "Hackathon Kickoff": {"date": "2026-07-05", "location": "Innovation Lab"},
}


# Tool 1: Calculator
def calculator(operation, values):
    if operation == "average":
        if not values:
            return {"error": "no values supplied"}
        return {"result": sum(values) / len(values)}
    if operation == "sum":
        return {"result": sum(values)}
    return {"error": f"unsupported operation: {operation}"}


# Tool 2: Read CSV
def read_csv(source_text=SIGNUPS_CSV):
    reader = csv.DictReader(io.StringIO(source_text))
    rows = list(reader)
    if not rows:
        return {"error": "empty file", "rows": [], "row_count": 0}
    return {"rows": rows, "row_count": len(rows)}


# Tool 3: Events API
def mock_events_api(event_name):
    record = MOCK_EVENTS_API_DB.get(event_name)
    if record is None:
        return {"error": f"no event metadata found for '{event_name}'"}
    return record


# Tool 4: Send Notification (Drafts only, does not send externally)
def send_notification(message, recipient_group="Event Organizers"):
    """
    Drafts an urgent or informational notification.
    Strictly isolated: drafts message to an outbox buffer, never performs external dispatch.
    """
    draft = {
        "status": "DRAFT_CREATED",
        "recipient_group": recipient_group,
        "draft_body": message,
        "dispatched": False,
        "note": "Message drafted for human review; no external network dispatch performed."
    }
    return draft


TOOLS = {
    "calculator": calculator,
    "read_csv": read_csv,
    "events_api": mock_events_api,
    "send_notification": send_notification,
}


class CampusDataAssistantWithNotification:
    def __init__(self, low_turnout_threshold=10.0):
        self.trace = []
        self.low_turnout_threshold = low_turnout_threshold

    def _call(self, tool_name, reason, **kwargs):
        result = TOOLS[tool_name](**kwargs)
        entry = {"tool": tool_name, "reason": reason, "input": kwargs, "output": result}
        self.trace.append(entry)
        if "error" in result:
            raise RuntimeError(f"{tool_name} failed: {result['error']}")
        return result

    def answer(self, question, csv_source=SIGNUPS_CSV):
        q = question.lower()

        if "average" in q and "sign" in q:
            csv_result = self._call(
                "read_csv", "sign-up counts live in the CSV export, not the events API",
                source_text=csv_source
            )
            values = [int(r["signups"]) for r in csv_result["rows"]]
            total = self._call("calculator", "sum the extracted signup column",
                                operation="sum", values=values)
            avg = self._call("calculator", "compute average over the same column",
                              operation="average", values=values)
            
            avg_value = avg["result"]
            response = (f"Total sign-ups: {total['result']}. "
                        f"Average per event: {avg_value:.2f} "
                        f"(across {csv_result['row_count']} events).")

            # Check threshold for low-turnout notification
            if avg_value < self.low_turnout_threshold:
                notice_text = (
                    f"LOW TURNOUT ALERT: Average sign-ups ({avg_value:.2f}) fell below the minimum "
                    f"operational threshold of {self.low_turnout_threshold}. Recommended action: boost event marketing."
                )
                draft_result = self._call(
                    "send_notification",
                    f"average turnout ({avg_value:.2f}) is below threshold ({self.low_turnout_threshold}); drafting organizer alert",
                    message=notice_text,
                    recipient_group="Event Coordination Board"
                )
                response += f"\n[NOTICE DRAFTED]: {draft_result['draft_body']}"
            else:
                response += f" Turnout is healthy (above threshold of {self.low_turnout_threshold})."

            return response

        if "where" in q and "hackathon" in q:
            meta = self._call(
                "events_api", "location/date metadata lives in the events API, not the CSV",
                event_name="Hackathon Kickoff")
            return f"Hackathon Kickoff is at {meta['location']} on {meta['date']}."

        return "I don't have a tool path configured for that question."


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 2 - Assignment 1: Notification Tool with Justified Use")
    print("================================================================================\n")

    assistant = CampusDataAssistantWithNotification(low_turnout_threshold=10.0)

    print("--- Scenario 1: Standard Turnout (Expected Avg > 10.0) ---")
    q1 = "What's the average sign-up per event for this month?"
    a1 = assistant.answer(q1, csv_source=SIGNUPS_CSV)
    print(f"Q: {q1}")
    print(f"A: {a1}\n")

    print("--- Scenario 2: Low Turnout Event Batch (Expected Avg < 10.0) ---")
    q2 = "What's the average sign-up per event for morning study sessions?"
    a2 = assistant.answer(q2, csv_source=LOW_TURNOUT_CSV)
    print(f"Q: {q2}")
    print(f"A: {a2}\n")

    print("=== Complete Execution Trace (Showing Notification Tool & Explicit Reason) ===")
    for i, entry in enumerate(assistant.trace, 1):
        print(f"\n[{i}] Tool: {entry['tool']}")
        print(f"    Reason: \"{entry['reason']}\"")
        print(f"    Input:  {entry['input']}")
        print(f"    Output: {entry['output']}")

