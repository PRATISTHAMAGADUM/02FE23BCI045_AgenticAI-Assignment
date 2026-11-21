"""
Lab 7: Agentic Node Graph -- Assignment 2: Add a Retry Limit to the Builder Node

Assignment Requirement:
Modify the graph so the `builder` node is allowed exactly one retry before escalating
to a human. Implement and demonstrate two scenarios:
(a) the builder fails once, retries, and succeeds;
(b) the builder fails twice and correctly escalates instead of retrying a third time.
"""

import json


class Node:
    def __init__(self, name, owner, success_fn, on_success, on_fail):
        self.name = name
        self.owner = owner
        self.success_fn = success_fn
        self.on_success = on_success
        self.on_fail = on_fail


def requirement_node(state):
    state["requirements"] = ["user login", "event listing", "RSVP button"]
    return state


def planner_node(state):
    state["tasks"] = {req: f"task_for({req})" for req in state["requirements"]}
    return state


# Builder node with retry counter and max 1 retry policy
MAX_BUILDER_RETRIES = 1  # 1 initial attempt + 1 retry = max 2 attempts


def builder_node_with_retry(state):
    """
    Executes builder stage with retry tracking.
    state['builder_failure_mode']:
      - 'fail_once_then_succeed': fails on attempt 1, succeeds on attempt 2
      - 'fail_twice': fails on attempt 1 and attempt 2
      - 'always_succeed': succeeds on attempt 1
    """
    state["builder_attempts"] = state.get("builder_attempts", 0) + 1
    attempt = state["builder_attempts"]
    mode = state.get("builder_failure_mode", "always_succeed")

    if mode == "fail_once_then_succeed":
        if attempt == 1:
            state["build_ok"] = False
            state["build_error"] = "Attempt 1 failed: Missing dependency 'fastapi' in generated environment."
        else:
            state["build_ok"] = True
            state["code"] = "app.py generated successfully on retry #1."
            state["build_error"] = None
    elif mode == "fail_twice":
        state["build_ok"] = False
        state["build_error"] = f"Attempt {attempt} failed: Syntax/compiler error in generated AST."
    else:
        state["build_ok"] = True
        state["code"] = "app.py generated on first pass."

    return state


def tester_node(state):
    state["tests_passed"] = state.get("build_ok", False)
    return state


def reviewer_node(state):
    state["review_clean"] = state.get("tests_passed", False)
    return state


def human_gate_node(state):
    state["human_signoff"] = state.get("review_clean", False)
    return state


def run_graph_with_builder_retry(failure_mode):
    state = {
        "builder_failure_mode": failure_mode,
        "builder_attempts": 0,
    }
    trace = []

    # Sequential execution loop with explicit retry loop for builder
    nodes = [
        ("requirement", "requirement_agent", lambda s: len(s.get("requirements", [])) >= 3, requirement_node, "escalate_to_human('goal too vague')"),
        ("planner", "planner_agent", lambda s: all(r in s.get("tasks", {}) for r in s.get("requirements", [])), planner_node, "return_to('requirement')"),
        ("builder", "builder_agent", lambda s: s.get("build_ok", False), builder_node_with_retry, "escalate_to_human('builder exceeded 1 retry limit')"),
        ("tester", "tester_agent", lambda s: s.get("tests_passed", False), tester_node, "route_back_to('builder')"),
        ("reviewer", "reviewer_agent", lambda s: s.get("review_clean", False), reviewer_node, "route_back_to('builder')"),
        ("human_gate", "human", lambda s: s.get("human_signoff", False), human_gate_node, "return_to('planner')"),
    ]

    for name, owner, success_fn, on_success, on_fail in nodes:
        if name == "builder":
            # Builder loop allowing exactly 1 retry
            while True:
                state = on_success(state)
                ok = success_fn(state)
                attempt_num = state["builder_attempts"]

                trace.append({
                    "node": "builder",
                    "owner": owner,
                    "attempt": attempt_num,
                    "success": ok,
                    "error": state.get("build_error"),
                    "code_present": "code" in state
                })

                if ok:
                    break  # Builder succeeded, move to tester
                else:
                    if attempt_num <= MAX_BUILDER_RETRIES:
                        trace.append({
                            "node": "builder",
                            "action": f"Retry permitted (attempt {attempt_num} <= max {MAX_BUILDER_RETRIES} retry). Initiating retry 1..."
                        })
                        continue  # Try again
                    else:
                        trace.append({
                            "node": "builder",
                            "action": f"NO MORE RETRIES: Attempt {attempt_num} exceeded 1 retry limit. Triggering failure behavior: {on_fail}"
                        })
                        return trace  # Pipeline halts and escalates to human
        else:
            state = on_success(state)
            ok = success_fn(state)
            trace.append({
                "node": name,
                "owner": owner,
                "success": ok,
                "summary": f"Completed stage '{name}' successfully."
            })
            if not ok:
                trace.append({"node": name, "failure_behavior_triggered": on_fail})
                break

    return trace


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 7 - Assignment 2: Retry Limit on Builder Node (Max 1 Retry -> Escalate)")
    print("================================================================================\n")

    print("=== SCENARIO A: Builder Fails Once, Retries, and SUCSTEEDS ===")
    trace_a = run_graph_with_builder_retry(failure_mode="fail_once_then_succeed")
    for step in trace_a:
        print(json.dumps(step, indent=2))

    print("\n================================================================================")
    print("=== SCENARIO B: Builder Fails Twice, Exceeds 1-Retry Limit, and ESCALATES ===")
    print("================================================================================\n")
    trace_b = run_graph_with_builder_retry(failure_mode="fail_twice")
    for step in trace_b:
        print(json.dumps(step, indent=2))

