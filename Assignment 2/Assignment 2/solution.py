"""
Lab 2: Tool-Using Agent -- Assignment 2: A Three-Tool Chain

Assignment Requirement:
Add a category field to the CSV data (e.g. "technical" vs "social") and implement
a new question ("What's the average sign-up for technical events only?") that
requires three steps: read the CSV, filter rows by category, then compute the
average over the filtered subset. Validate the filter step's output (non-empty)
before computing the average. Submit the updated code and the trace for this new question.
"""

import csv
import io
import json

# Extended CSV data with category column
EXTENDED_SIGNUPS_CSV = """event,signups,category
AI Club Talk,12,technical
Hackathon Kickoff,9,technical
Robotics Demo,15,technical
GenAI Workshop,7,technical
Capstone Expo,20,academic
Career Panel,11,social
Alumni Networking,14,social
"""


def calculator(operation, values):
    if operation == "average":
        if not values:
            return {"error": "no values supplied"}
        return {"result": sum(values) / len(values)}
    if operation == "sum":
        return {"result": sum(values)}
    return {"error": f"unsupported operation: {operation}"}


def read_csv(source_text=EXTENDED_SIGNUPS_CSV):
    reader = csv.DictReader(io.StringIO(source_text))
    rows = list(reader)
    if not rows:
        return {"error": "empty file", "rows": [], "row_count": 0}
    return {"rows": rows, "row_count": len(rows)}


def filter_by_category(rows, category):
    """
    Tool: Filters rows by category and validates that result is non-empty.
    """
    matched = [r for r in rows if r.get("category", "").strip().lower() == category.strip().lower()]
    if not matched:
        return {
            "error": f"no records found matching category '{category}'",
            "filtered_rows": [],
            "match_count": 0
        }
    return {
        "category": category,
        "filtered_rows": matched,
        "match_count": len(matched)
    }


def mock_events_api(event_name):
    db = {
        "AI Club Talk": {"date": "2026-07-02", "location": "CS Block Auditorium"},
        "Hackathon Kickoff": {"date": "2026-07-05", "location": "Innovation Lab"},
    }
    record = db.get(event_name)
    if record is None:
        return {"error": f"no event metadata found for '{event_name}'"}
    return record


TOOLS = {
    "calculator": calculator,
    "read_csv": read_csv,
    "filter_by_category": filter_by_category,
    "events_api": mock_events_api,
}


class ThreeToolChainAssistant:
    def __init__(self):
        self.trace = []

    def _call(self, tool_name, reason, **kwargs):
        result = TOOLS[tool_name](**kwargs)
        entry = {"tool": tool_name, "reason": reason, "input": kwargs, "output": result}
        self.trace.append(entry)
        if "error" in result:
            raise RuntimeError(f"{tool_name} failed: {result['error']}")
        return result

    def answer(self, question):
        q = question.lower()

        # Three-tool chain: Category-specific average sign-ups
        if "average" in q:
            # Target category extraction
            category = "technical"
            if "social" in q:
                category = "social"
            elif "academic" in q:
                category = "academic"
            elif "sports" in q or "athletic" in q:
                category = "athletic"

            # Step 1: Read raw CSV
            csv_result = self._call(
                "read_csv",
                "Step 1/3: Ingest entire dataset containing event sign-ups and category annotations"
            )

            # Step 2: Filter rows by target category & validate non-empty output
            try:
                filter_result = self._call(
                    "filter_by_category",
                    f"Step 2/3: Filter dataset down to '{category}' category rows and validate non-empty",
                    rows=csv_result["rows"],
                    category=category
                )
            except RuntimeError as e:
                return f"Chain halted at Step 2 (validation failure): {e}"

            # Step 3: Compute average on the validated subset
            filtered_rows = filter_result["filtered_rows"]
            values = [int(r["signups"]) for r in filtered_rows]

            avg_result = self._call(
                "calculator",
                f"Step 3/3: Calculate average signups across {len(values)} filtered '{category}' events",
                operation="average",
                values=values
            )

            return (
                f"Average sign-up for {category} events only: {avg_result['result']:.2f} "
                f"(computed across {filter_result['match_count']} events: "
                f"{', '.join([r['event'] for r in filtered_rows])})."
            )

        return "I don't have a configured chain for that question."


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 2 - Assignment 2: Three-Tool Chain (Read CSV -> Filter Category -> Calculator)")
    print("================================================================================\n")

    assistant = ThreeToolChainAssistant()

    # Required query
    q1 = "What's the average sign-up for technical events only?"
    print(f"Query 1: \"{q1}\"")
    a1 = assistant.answer(q1)
    print(f"Answer 1: {a1}\n")

    # Edge case query (validation guard test)
    q2 = "What's the average sign-up for sports events only?"
    print(f"Query 2 (Edge Case - Non-existent Category): \"{q2}\"")
    a2 = assistant.answer(q2)
    print(f"Answer 2: {a2}\n")

    print("=== Full Execution Trace for Three-Tool Chain ===")
    for i, entry in enumerate(assistant.trace, 1):
        print(f"\nStep {i}:")
        print(f"  Tool:   {entry['tool']}")
        print(f"  Reason: {entry['reason']}")
        print(f"  Input:  {entry['input']}")
        print(f"  Output: {entry['output']}")
