"""
Lab 14: Capstone Project Studio -- Assignment 1: Add a Second Reusable Skill (Password-Reset Guidance)

Assignment Requirement:
Add a genuine second skill (e.g. "password-reset guidance") with its own
instructions and constraints, alongside the existing `triage_skill`.
Extend the node graph so the triage stage correctly routes between the two
skills based on the issue text, and demonstrate both skills firing correctly
on different inputs. Submit updated code and output.
"""

from datetime import datetime
import json

# ---- Tools (4 Tools) ---------------------------------------------------
FAQ_DB = {
    "wifi": "Connect to 'Campus-Secure' and log in with your student ID.",
    "library": "Library hours during finals are 24/7 with active student ID badge access.",
}
TICKET_DB = []


def tool_search_faq(query):
    for k, v in FAQ_DB.items():
        if k in query.lower():
            return {"found": True, "answer": v}
    return {"found": False}


def tool_create_ticket(issue, category="general"):
    ticket_id = f"T-{len(TICKET_DB) + 1:03d}"
    record = {"id": ticket_id, "issue": issue, "category": category, "status": "open"}
    TICKET_DB.append(record)
    return {"ticket_id": ticket_id, "category": category}


def tool_generate_password_reset_token(user_identifier):
    """Secure tool providing a time-limited one-time reset link."""
    return {
        "portal_url": "https://identity.campus.edu/self-service/reset",
        "token_valid_minutes": 15,
        "mfa_required": True
    }


def tool_check_ticket_status(ticket_id):
    for t in TICKET_DB:
        if t["id"] == ticket_id:
            return t
    return {"error": "not found"}


# ---- Skill 1: Triage-and-Respond ----------------------------------------
def triage_skill(issue_text):
    """
    Skill 1: General Help-Desk Triage
    Instructions: Search FAQ first; only escalate to ticket if no match.
    Constraint: Never fabricate an answer; maintain ticket lineage.
    """
    faq_result = tool_search_faq(issue_text)
    if faq_result["found"]:
        return {
            "skill_used": "triage_skill",
            "resolution": "faq",
            "answer": faq_result["answer"]
        }
    ticket = tool_create_ticket(issue_text, category="it_support")
    return {
        "skill_used": "triage_skill",
        "resolution": "escalated",
        "ticket_id": ticket["ticket_id"]
    }


# ---- Skill 2 (NEW): Password-Reset Guidance Skill -----------------------
def password_reset_guidance_skill(issue_text, user):
    """
    Skill 2: Password-Reset Guidance
    Instructions:
      1. Issue official secure self-service portal link with expiry limits.
      2. Instruct user to complete biometric/MFA challenge.
    Constraints:
      1. NEVER prompt for, collect, or log plain-text passwords or security answers.
      2. Always explicitly mandate official identity portal verification.
    """
    reset_data = tool_generate_password_reset_token(user)
    guidance_text = (
        f"To reset your campus credentials safely:\n"
        f"1. Navigate to the official identity portal: {reset_data['portal_url']}\n"
        f"2. Authenticate using your 2-Factor Authentication (Duo Push / SMS code).\n"
        f"3. Establish a new password meeting campus complexity policies (min 14 chars).\n"
        f"Security Warning: Reset session expires in {reset_data['token_valid_minutes']} minutes. "
        f"Campus IT staff will NEVER ask for your password via chat or email."
    )
    return {
        "skill_used": "password_reset_guidance_skill",
        "resolution": "password_reset_guidance",
        "portal": reset_data["portal_url"],
        "instructions": guidance_text,
        "security_compliant": True
    }


# ---- Memory -------------------------------------------------------------
class CapstoneMemory:
    def __init__(self):
        self.session = {}
        self.history = []

    def record(self, user, issue, outcome):
        entry = {
            "user": user,
            "issue": issue,
            "skill": outcome.get("skill_used"),
            "resolution": outcome.get("resolution"),
            "date": datetime.now().isoformat(timespec="seconds")
        }
        self.history.append(entry)
        self.session["last_issue"] = issue


# ---- Extended Node Graph with Skill Router Node -------------------------
def node_graph_run(user, issue, memory, audit_log, prompt_log):
    prompt_log.append({"stage": "intake", "user": user, "input": issue})

    # Safety Control: Check empty input
    if not issue.strip():
        audit_log.append({"stage": "intake", "result": "rejected: empty input"})
        return {"rejected": True, "reason": "empty issue text"}

    # ROUTER NODE: Dynamically routes issue to appropriate specialized skill
    issue_lower = issue.lower()
    is_password_issue = any(k in issue_lower for k in ["password", "reset", "forgot login", "credentials", "locked out"])

    if is_password_issue:
        selected_skill_name = "password_reset_guidance_skill"
        outcome = password_reset_guidance_skill(issue, user)
        response = outcome["instructions"]
    else:
        selected_skill_name = "triage_skill"
        outcome = triage_skill(issue)
        if outcome["resolution"] == "faq":
            response = outcome["answer"]
        else:
            response = f"Ticket {outcome['ticket_id']} created; IT support team will follow up."

    prompt_log.append({"stage": "skill_execution", "skill": selected_skill_name, "outcome": outcome})
    memory.record(user, issue, outcome)
    audit_log.append({"stage": "complete", "user": user, "skill": selected_skill_name, "resolution": outcome["resolution"]})

    return {
        "rejected": False,
        "skill_invoked": selected_skill_name,
        "response": response,
        "outcome": outcome
    }


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 14 - Assignment 1: Dual Reusable Skills with Intelligent Node Graph Routing")
    print("================================================================================\n")

    memory = CapstoneMemory()
    audit_log, prompt_log = [], []

    # Test Input 1: Triggers triage_skill (FAQ Match)
    print("--- Test 1: General Query -> triage_skill (FAQ Match) ---")
    q1 = "How do I connect to wifi on campus?"
    r1 = node_graph_run("alice", q1, memory, audit_log, prompt_log)
    print(f"User: alice | Issue: \"{q1}\"")
    print(f"Skill Dispatched: {r1['skill_invoked']}")
    print(f"Response: {r1['response']}\n")

    # Test Input 2: Triggers password_reset_guidance_skill
    print("--- Test 2: Account Credential Query -> password_reset_guidance_skill ---")
    q2 = "I forgot my campus password and my account is locked out!"
    r2 = node_graph_run("bob", q2, memory, audit_log, prompt_log)
    print(f"User: bob | Issue: \"{q2}\"")
    print(f"Skill Dispatched: {r2['skill_invoked']}")
    print(f"Response:\n{r2['response']}\n")

    # Test Input 3: Triggers triage_skill (No FAQ match -> Ticket Creation)
    print("--- Test 3: Hardware Support Query -> triage_skill (Ticket Escalation) ---")
    q3 = "The projector in CS Hall Room 201 has a flickering bulb."
    r3 = node_graph_run("charlie", q3, memory, audit_log, prompt_log)
    print(f"User: charlie | Issue: \"{q3}\"")
    print(f"Skill Dispatched: {r3['skill_invoked']}")
    print(f"Response: {r3['response']}\n")

    # Verification assertions
    print("=== Verification of Dual Skill Routing ===")
    assert r1["skill_invoked"] == "triage_skill" and r1["outcome"]["resolution"] == "faq"
    assert r2["skill_invoked"] == "password_reset_guidance_skill" and r2["outcome"]["resolution"] == "password_reset_guidance"
    assert r3["skill_invoked"] == "triage_skill" and r3["outcome"]["resolution"] == "escalated"
    print("SUCCESS: Both skills dispatched accurately according to user issue classification.")

    print("\n=== Long-Term Memory Log (Both Skills Recorded) ===")
    for h in memory.history:
        print(f"  [{h['date']}] User: {h['user']} | Skill: {h['skill']} | Resolution: {h['resolution']}")

