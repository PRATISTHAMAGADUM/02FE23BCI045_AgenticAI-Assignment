"""
Lab 7: Agentic Node Graph -- Assignment 1: Add a Security-Scan Node

Assignment Requirement:
Insert a new `security_scan` node between `builder` and `tester`, with its own
input, output, owner, success criteria, and failure behavior. Update both the
success-path and failure-path simulations to include it, and produce a case where
the security scan itself is the node that fails. Submit the updated code and a
transcript showing both the success path and the security scan failure path.
"""

import json


class Node:
    def __init__(self, name, owner, success_fn, on_success, on_fail):
        self.name = name
        self.owner = owner
        self.success_fn = success_fn      # state -> bool
        self.on_success = on_success       # state -> state (next stage's input)
        self.on_fail = on_fail             # description of failure behavior


def requirement_node(state):
    state["requirements"] = ["user login", "event listing", "RSVP button"]
    return state


def planner_node(state):
    state["tasks"] = {req: f"task_for({req})" for req in state["requirements"]}
    return state


def builder_node(state):
    if state.get("force_build_fail"):
        state["build_ok"] = False
        return state
    state["build_ok"] = True
    state["code"] = "app.py generated (with auth and rsvp endpoints)"
    return state


# ---- Newly Added Security-Scan Node (Between builder and tester) --------
def security_scan_node(state):
    """
    Security Scan Node:
    Input: state['code']
    Output: state['security_clean'] (bool), state['vulnerabilities'] (list)
    """
    if state.get("force_security_fail"):
        state["security_clean"] = False
        state["vulnerabilities"] = [
            "CWE-89: Potential SQL Injection pattern detected in query params",
            "CWE-798: Hardcoded test credential found in comment"
        ]
        return state

    # Normal success path
    state["security_clean"] = True
    state["vulnerabilities"] = []
    state["security_scan_report"] = "SAST scan clean: 0 vulnerabilities found."
    return state


def tester_node(state):
    # Tester only passes if previous stages (builder and security) succeeded
    state["tests_passed"] = state.get("build_ok", False) and state.get("security_clean", False)
    return state


def reviewer_node(state):
    state["review_clean"] = state.get("tests_passed", False)
    return state


def human_gate_node(state):
    state["human_signoff"] = state.get("review_clean", False)
    return state


# ---- Extended Node Graph with Security Scan -----------------------------
GRAPH = [
    Node("requirement", "requirement_agent",
         lambda s: len(s.get("requirements", [])) >= 3,
         requirement_node,
         "escalate_to_human('goal too vague to extract 3+ requirements')"),
    Node("planner", "planner_agent",
         lambda s: all(r in s.get("tasks", {}) for r in s.get("requirements", [])),
         planner_node,
         "return_to('requirement')"),
    Node("builder", "builder_agent",
         lambda s: s.get("build_ok", False),
         builder_node,
         "retry_build_or_escalate"),
    # New Node inserted between builder and tester
    Node("security_scan", "security_agent",
         lambda s: s.get("security_clean", False),
         security_scan_node,
         "quarantine_build_and_alert_security_team('Vulnerability detected in generated code')"),
    Node("tester", "tester_agent",
         lambda s: s.get("tests_passed", False),
         tester_node,
         "route_back_to('builder')"),
    Node("reviewer", "reviewer_agent",
         lambda s: s.get("review_clean", False),
         reviewer_node,
         "route_back_to('builder')"),
    Node("human_gate", "human",
         lambda s: s.get("human_signoff", False),
         human_gate_node,
         "return_to('planner', reason=human.notes)"),
]


def simulate(force_build_fail=False, force_security_fail=False):
    state = {
        "force_build_fail": force_build_fail,
        "force_security_fail": force_security_fail,
    }
    trace = []
    for node in GRAPH:
        state = node.on_success(state)
        ok = node.success_fn(state)
        trace.append({
            "node": node.name,
            "owner": node.owner,
            "success": ok,
            "state_after": {k: v for k, v in state.items() if not k.startswith("force_")}
        })
        if not ok:
            trace.append({
                "node": node.name,
                "failure_behavior_triggered": node.on_fail
            })
            break
    return trace


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 7 - Assignment 1: Insert Security-Scan Node into Agentic Node Graph")
    print("================================================================================\n")

    print("=== PATH 1: COMPLETE SUCCESS PATH (All Nodes Pass) ===")
    for step in simulate(force_build_fail=False, force_security_fail=False):
        print(json.dumps(step, indent=2))

    print("\n=== PATH 2: SECURITY SCAN FAILURE PATH (Security Node Fails) ===")
    for step in simulate(force_build_fail=False, force_security_fail=True):
        print(json.dumps(step, indent=2))

    print("\n=== PATH 3: BUILDER FAILURE PATH (Builder Fails Before Security) ===")
    for step in simulate(force_build_fail=True, force_security_fail=False):
        print(json.dumps(step, indent=2))

