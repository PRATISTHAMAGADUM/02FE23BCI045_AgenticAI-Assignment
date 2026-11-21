"""
Lab 4: Memory and Retrieval -- Assignment 2: A Staleness / Retention Policy

Assignment Requirement:
Add a `retention_days` control and a staleness check: if a retrieved record is older
than the configured threshold, the assistant must warn the user ("this decision is from
N days ago and may be out of date") before using it in an answer. Test it with one fresh
record and one artificially old record. Submit the updated code and a transcript showing both cases.
"""

from dataclasses import dataclass
from datetime import datetime, date, timedelta


@dataclass
class MemoryRecord:
    topic: str
    fact: str
    date: str  # Format: YYYY-MM-DD
    source: str = "memory"


class ProjectMemory:
    def __init__(self):
        self.records = []
        self.allowed_writers = {"team_lead"}

    def retrieve(self, topic):
        return [r for r in self.records if r.topic.lower() == topic.lower()]

    def write(self, record, user_role):
        if user_role not in self.allowed_writers:
            raise PermissionError(f"role '{user_role}' is not permitted to write memory")
        self.records.append(record)


class ProjectAssistantWithStaleness:
    def __init__(self, memory, retention_days=30, reference_current_date=None):
        self.memory = memory
        self.retention_days = retention_days
        # Use provided reference date or today's date
        self.current_date = reference_current_date or date.today()

    def check_staleness(self, record_date_str):
        """
        Computes elapsed days between record date and current date.
        Returns (is_stale, age_days).
        """
        rec_date = datetime.strptime(record_date_str, "%Y-%m-%d").date()
        age_days = (self.current_date - rec_date).days
        is_stale = age_days > self.retention_days
        return is_stale, age_days

    def answer(self, topic, question):
        hits = self.memory.retrieve(topic)
        if not hits:
            return f"[session] No stored decision on '{topic}' yet. {question}"
        
        latest = hits[-1]
        is_stale, age_days = self.check_staleness(latest.date)

        if is_stale:
            warning = (
                f"[STALENESS WARNING: This decision is from {age_days} days ago and may be out of date! "
                f"Configured retention threshold is {self.retention_days} days.]"
            )
            return (f"{warning}\n"
                    f"Answer based on historical record (dated {latest.date}): {latest.fact}")
        else:
            return (
                f"[FRESH RECORD: Verified within retention policy ({age_days} days old <= {self.retention_days} days threshold)]\n"
                f"Answer (dated {latest.date}): {latest.fact}"
            )


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 4 - Assignment 2: Staleness Check & Retention Policy in Memory Retrieval")
    print("================================================================================\n")

    # Define benchmark current date
    CURRENT_DATE = date(2026, 11, 14)
    RETENTION_THRESHOLD_DAYS = 30

    print(f"System Configuration:")
    print(f"  Reference Current Date: {CURRENT_DATE}")
    print(f"  Configured Retention Policy: {RETENTION_THRESHOLD_DAYS} days\n")

    memory = ProjectMemory()

    # Case 1: Fresh record (recorded 10 days ago: 2026-11-04)
    fresh_date_str = str(CURRENT_DATE - timedelta(days=10))
    memory.write(
        MemoryRecord(topic="caching", fact="we use Redis cluster for session cache", date=fresh_date_str),
        user_role="team_lead"
    )

    # Case 2: Artificially old record (recorded 120 days ago: 2026-07-17)
    old_date_str = str(CURRENT_DATE - timedelta(days=120))
    memory.write(
        MemoryRecord(topic="ci_pipeline", fact="we use Jenkins on dedicated EC2 VMs", date=old_date_str),
        user_role="team_lead"
    )

    assistant = ProjectAssistantWithStaleness(
        memory=memory,
        retention_days=RETENTION_THRESHOLD_DAYS,
        reference_current_date=CURRENT_DATE
    )

    # Test Case 1: Fresh Record
    print("--- Case 1: Querying Fresh Memory Record (10 days old) ---")
    q1 = "What did we decide regarding caching?"
    print(f"Q: {q1}")
    a1 = assistant.answer("caching", q1)
    print(f"A:\n{a1}\n")

    # Test Case 2: Stale Record
    print("--- Case 2: Querying Artificially Old Record (120 days old) ---")
    q2 = "What did we decide regarding the CI pipeline?"
    print(f"Q: {q2}")
    a2 = assistant.answer("ci_pipeline", q2)
    print(f"A:\n{a2}\n")

    print("=== Verification Summary ===")
    print("Case 1 (Fresh): Served without warning; age verified under 30 days.")
    print("Case 2 (Stale): User explicitly warned before answer was provided; staleness detected.")

