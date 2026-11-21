"""
Lab 6: OpenCLA/OpenClaw Runtime -- Assignment 2: Escalate After Two Failures

Assignment Requirement:
Add a rule: if the same skill fails twice in one session for the same user, the
third attempt must escalate to a human instead of retrying the skill again.
Implement this using the existing audit log (count prior error entries for that
user/skill pair) rather than adding new hidden state. Submit the updated code and
a transcript showing two failures followed by an escalation instead of a third attempt.
"""

from datetime import datetime


# ---- Tools ------------------------------------------------------------
def tool_word_count(text):
    return {"count": len(text.split())}


def tool_lookup_contact(name, contacts_db):
    return contacts_db.get(name, {"error": f"no contact found for {name}"})


TOOLS = {"word_count": tool_word_count, "lookup_contact": tool_lookup_contact}


# ---- Memory, scoped per user -------------------------------------------
class Memory:
    def __init__(self):
        self._store = {}

    def scope(self, user):
        return self._store.setdefault(user, {})


# ---- Audit Log: Central source of truth (no hidden state) --------------
class Audit:
    def __init__(self):
        self.entries = []

    def log(self, task, skill_name, tool_calls, user=None, result=None, error=None, escalated=False):
        self.entries.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "user": user,
            "task": task,
            "skill": skill_name,
            "tool_calls": tool_calls,
            "result": result,
            "error": error,
            "escalated": escalated,
        })

    def count_failures(self, user, skill_name):
        """
        Inspects existing audit entries to determine how many times
        this (user, skill_name) pair has failed.
        """
        count = 0
        for entry in self.entries:
            if entry.get("user") == user and entry.get("skill") == skill_name and entry.get("error") is not None:
                count += 1
        return count


# ---- Skills --------------------------------------------------------------
class FlakyDatabaseQuerySkill:
    """A skill simulating an external connection that fails due to bad credentials or broken endpoint."""
    def __init__(self, memory_scope):
        self.memory_scope = memory_scope
        self.tool_calls = []

    def execute(self, task):
        endpoint = task.get("endpoint", "")
        self.tool_calls.append({"tool": "network_call", "endpoint": endpoint})
        # Deliberately fails when given bad endpoint
        if "bad_host" in endpoint:
            raise ConnectionError(f"Database connection timeout at '{endpoint}'")
        return f"Query returned 200 records from {endpoint}"


SKILL_REGISTRY = {
    "flaky_db_query": FlakyDatabaseQuerySkill,
}


def select_skill(task):
    return task["skill"]


# ---- Core Runtime Loop with Audit-Driven Escalation ---------------------
def run_task(task, user, memory, audit):
    skill_name = select_skill(task)

    # RULE: Count prior errors for (user, skill_name) directly from the audit log
    prior_errors = audit.count_failures(user, skill_name)

    if prior_errors >= 2:
        escalation_note = (
            f"HUMAN ESCALATION TRIGGERED: Skill '{skill_name}' has previously failed {prior_errors} times "
            f"for user '{user}'. Halting automated execution; escalating to On-Call Support Engineer."
        )
        audit.log(task, skill_name, [], user=user, result=None, error=None, escalated=True)
        return {
            "status": "ESCALATED_TO_HUMAN",
            "skill": skill_name,
            "prior_failures_found_in_audit": prior_errors,
            "escalation_message": escalation_note
        }

    skill_cls = SKILL_REGISTRY[skill_name]
    skill = skill_cls(memory.scope(user))
    try:
        result = skill.execute(task)
        audit.log(task, skill_name, skill.tool_calls, user=user, result=result)
        return {"status": "SUCCESS", "result": result}
    except Exception as e:
        audit.log(task, skill_name, skill.tool_calls, user=user, error=str(e))
        return {"status": "FAILED", "error": str(e)}


def receive_task(task, user, memory, audit):
    return run_task(task, user, memory, audit)


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 6 - Assignment 2: Escalate to Human After Two Failures (Audit-Driven)")
    print("================================================================================\n")

    memory, audit = Memory(), Audit()
    user = "uday"
    failing_task = {"skill": "flaky_db_query", "endpoint": "bad_host.internal.net:5432"}

    # Attempt 1: Expect Failure
    print("--- Attempt 1: Invoking failing skill ---")
    res1 = receive_task(failing_task, user=user, memory=memory, audit=audit)
    print(f"Result: {res1['status']} | Error: {res1.get('error')}")
    print(f"Audit log failure count for ({user}, flaky_db_query): {audit.count_failures(user, 'flaky_db_query')}\n")

    # Attempt 2: Expect Failure
    print("--- Attempt 2: Retrying same failing skill ---")
    res2 = receive_task(failing_task, user=user, memory=memory, audit=audit)
    print(f"Result: {res2['status']} | Error: {res2.get('error')}")
    print(f"Audit log failure count for ({user}, flaky_db_query): {audit.count_failures(user, 'flaky_db_query')}\n")

    # Attempt 3: Expect Automatic Escalation to Human without retrying skill
    print("--- Attempt 3: Third invocation of failing skill (Should Escalate) ---")
    res3 = receive_task(failing_task, user=user, memory=memory, audit=audit)
    print(f"Result: {res3['status']}")
    print(f"Escalation Details: {res3.get('escalation_message')}\n")

    print("=== Complete Audit Log Inspection (Zero Hidden State Used) ===")
    for idx, e in enumerate(audit.entries, 1):
        status = "ESCALATED" if e.get("escalated") else ("FAILED" if e.get("error") else "SUCCESS")
        print(f"[{idx}] User='{e['user']}' | Skill='{e['skill']}' | Status={status} | Err={e.get('error')}")

