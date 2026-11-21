"""
Lab 6: OpenCLA/OpenClaw Runtime -- Assignment 1: Add Per-User Rate Limiting

Assignment Requirement:
Add a new control: each user may run at most 3 tasks per session. Implement this
as a check inside `receive_task` (or a thin wrapper around it) without changing
`run_task`'s core loop signature or its skill-dispatch logic. Submit the updated
code and a transcript showing a 4th task being rejected.
"""

from datetime import datetime
from collections import defaultdict


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


# ---- Audit -------------------------------------------------------------
class Audit:
    def __init__(self):
        self.entries = []

    def log(self, task, skill_name, tool_calls, result=None, error=None):
        self.entries.append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "task": task, "skill": skill_name, "tool_calls": tool_calls,
            "result": result, "error": error,
        })


# ---- Skills --------------------------------------------------------------
class SummarizeNotesSkill:
    def __init__(self, memory_scope):
        self.memory_scope = memory_scope
        self.tool_calls = []

    def execute(self, task):
        text = task.get("text", "")
        wc = TOOLS["word_count"](text)
        self.tool_calls.append({"tool": "word_count", "output": wc})
        self.memory_scope["last_note_length"] = wc["count"]
        return f"Summary stub: note has {wc['count']} words."


class DraftEmailSkill:
    CONTACTS = {"Dr. Meena": {"email": "meena@example.edu"}}

    def __init__(self, memory_scope):
        self.memory_scope = memory_scope
        self.tool_calls = []

    def execute(self, task):
        contact = TOOLS["lookup_contact"](task["to"], self.CONTACTS)
        self.tool_calls.append({"tool": "lookup_contact", "output": contact})
        if "error" in contact:
            raise RuntimeError(contact["error"])
        return f"Draft email to {contact['email']}: '{task['subject']}'"


class TranslateTextSkill:
    def __init__(self, memory_scope):
        self.memory_scope = memory_scope
        self.tool_calls = []

    def execute(self, task):
        return f"[translated to {task['target_lang']}] {task['text']}"


SKILL_REGISTRY = {
    "summarize_notes": SummarizeNotesSkill,
    "draft_email": DraftEmailSkill,
    "translate_text": TranslateTextSkill,
}


# ---- Runtime core loop: UNCHANGED ---------------------------------------
def select_skill(task):
    return task["skill"]


def run_task(task, user, memory, audit):
    skill_name = select_skill(task)
    skill_cls = SKILL_REGISTRY[skill_name]
    skill = skill_cls(memory.scope(user))
    try:
        result = skill.execute(task)
        audit.log(task, skill_name, skill.tool_calls, result=result)
        return result
    except Exception as e:
        audit.log(task, skill_name, skill.tool_calls, error=str(e))
        raise


# ---- Rate Limiter State -------------------------------------------------
USER_TASK_COUNTS = defaultdict(int)
MAX_TASKS_PER_USER = 3


# ---- Interface: Entry point with rate-limiting guard --------------------
def receive_task(task, user, memory, audit):
    """
    Enforces per-user session rate limit (max 3 tasks per user).
    Core run_task signature and execution logic remain untouched.
    """
    if USER_TASK_COUNTS[user] >= MAX_TASKS_PER_USER:
        err_msg = (
            f"RateLimitExceeded: User '{user}' has reached the maximum allowed limit "
            f"of {MAX_TASKS_PER_USER} tasks per session."
        )
        audit.log(task, task.get("skill", "unknown"), [], error=err_msg)
        raise RuntimeError(err_msg)

    USER_TASK_COUNTS[user] += 1
    return run_task(task, user, memory, audit)


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 6 - Assignment 1: Per-User Session Rate Limiting (Max 3 Tasks per User)")
    print("================================================================================\n")

    memory, audit = Memory(), Audit()
    test_user = "uday"

    print(f"Submitting tasks for user: '{test_user}' (Max limit: {MAX_TASKS_PER_USER})...\n")

    # Task 1
    print("--- Submitting Task 1 ---")
    t1 = receive_task(
        {"skill": "summarize_notes", "text": "Agent architectures provide autonomy and modularity."},
        user=test_user, memory=memory, audit=audit
    )
    print(f"Task 1 Result: {t1} (User count: {USER_TASK_COUNTS[test_user]}/{MAX_TASKS_PER_USER})\n")

    # Task 2
    print("--- Submitting Task 2 ---")
    t2 = receive_task(
        {"skill": "draft_email", "to": "Dr. Meena", "subject": "Reviewing Lab 6 submission"},
        user=test_user, memory=memory, audit=audit
    )
    print(f"Task 2 Result: {t2} (User count: {USER_TASK_COUNTS[test_user]}/{MAX_TASKS_PER_USER})\n")

    # Task 3
    print("--- Submitting Task 3 ---")
    t3 = receive_task(
        {"skill": "translate_text", "text": "Good morning", "target_lang": "Kannada"},
        user=test_user, memory=memory, audit=audit
    )
    print(f"Task 3 Result: {t3} (User count: {USER_TASK_COUNTS[test_user]}/{MAX_TASKS_PER_USER})\n")

    # Task 4 (Should be rejected)
    print("--- Submitting Task 4 (Exceeds Limit) ---")
    try:
        receive_task(
            {"skill": "summarize_notes", "text": "This task should be rejected by the rate limiter."},
            user=test_user, memory=memory, audit=audit
        )
    except RuntimeError as e:
        print(f">>> REJECTION CAUGHT: {e}\n")

    # Verify second user can still submit
    print("--- Verifying Isolated Quota for Another User ('priya') ---")
    t_other = receive_task(
        {"skill": "summarize_notes", "text": "Priya notes on distributed systems"},
        user="priya", memory=memory, audit=audit
    )
    print(f"Priya Task 1 Result: {t_other} (User count: {USER_TASK_COUNTS['priya']}/{MAX_TASKS_PER_USER})\n")

    print("=== Complete Audit Log ===")
    for idx, e in enumerate(audit.entries, 1):
        status = "ERROR" if e["error"] else "SUCCESS"
        print(f"[{idx}] {e['timestamp']} | User: {e['task'].get('to', e['task'].get('target_lang', 'task'))} | Status: {status} | Error: {e['error']}")

