"""
Lab 8: Parallel Swarm -- Assignment 2: Distributed Critique

Assignment Requirement:
Replace the single central `critique()` function with a design where each of the
four (or five) roles critiques the merged draft independently against its own
constraints, and the conflict log records which specific role raised each objection.
Submit the updated code and a transcript showing at least two different roles
independently raising objections.
"""

from concurrent.futures import ThreadPoolExecutor
import json


# ---- 1. Role Proposal Generators (First Swarm Phase) -------------------
def research_agent(goal):
    return {
        "role": "research",
        "output": {
            "format": "24-hour overnight hackathon with multi-track hardware and software themes",
            "participant_target": 250,
            "min_setup_hours": 6
        }
    }


def logistics_agent(goal):
    return {
        "role": "logistics",
        "output": {
            "venue": "Grand Hall",
            "venue_cost": 45000,
            "date": "Saturday 09:00 to 21:00 (single daytime shift)",
            "capacity": 150,
            "overnight_allowed": False
        }
    }


def budget_agent(goal):
    return {
        "role": "budget",
        "output": {"total_cap": 30000}
    }


def judging_agent(goal):
    return {
        "role": "judging",
        "output": {
            "criteria": "Judge on innovation, technical depth, and demo quality",
            "required_demo_hours": 4
        }
    }


ROLES = {
    "research": research_agent,
    "logistics": logistics_agent,
    "budget": budget_agent,
    "judging": judging_agent,
}


def run_swarm(goal):
    with ThreadPoolExecutor(max_workers=len(ROLES)) as pool:
        futures = {name: pool.submit(fn, goal) for name, fn in ROLES.items()}
        outputs = {name: f.result() for name, f in futures.items()}
    return outputs


def merge(outputs):
    return {
        "format": outputs["research"]["output"]["format"],
        "target_participants": outputs["research"]["output"]["participant_target"],
        "venue": outputs["logistics"]["output"]["venue"],
        "venue_cost": outputs["logistics"]["output"]["venue_cost"],
        "venue_capacity": outputs["logistics"]["output"]["capacity"],
        "venue_overnight": outputs["logistics"]["output"]["overnight_allowed"],
        "schedule": outputs["logistics"]["output"]["date"],
        "budget_cap": outputs["budget"]["output"]["total_cap"],
        "judging_criteria": outputs["judging"]["output"]["criteria"],
        "required_demo_hours": outputs["judging"]["output"]["required_demo_hours"],
    }


# ---- 2. Distributed Independent Role Critiques (Second Swarm Phase) ----
def critique_budget(draft):
    """Budget agent independently audits fiscal constraints."""
    objections = []
    if draft["venue_cost"] > draft["budget_cap"]:
        objections.append({
            "objecting_role": "budget",
            "severity": "CRITICAL",
            "target": "venue_cost",
            "observed_value": draft["venue_cost"],
            "threshold": draft["budget_cap"],
            "objection": (
                f"Proposed venue cost ({draft['venue_cost']}) exceeds total available "
                f"budget cap of {draft['budget_cap']}. Unacceptable fiscal deficit."
            ),
            "recommendation": "Negotiate academic discount or relocate to campus auditorium."
        })
    return objections


def critique_research(draft):
    """Research agent independently audits participant experience & format constraints."""
    objections = []
    if draft["target_participants"] > draft["venue_capacity"]:
        objections.append({
            "objecting_role": "research",
            "severity": "HIGH",
            "target": "venue_capacity",
            "observed_value": draft["venue_capacity"],
            "threshold": draft["target_participants"],
            "objection": (
                f"Venue capacity ({draft['venue_capacity']}) cannot accommodate target "
                f"participants ({draft['target_participants']}) derived from benchmark data."
            ),
            "recommendation": "Increase venue capacity or institute strict registration caps."
        })
    if "24-hour" in draft["format"] and not draft["venue_overnight"]:
        objections.append({
            "objecting_role": "research",
            "severity": "CRITICAL",
            "target": "venue_overnight",
            "observed_value": "overnight_allowed=False",
            "threshold": "24-hour overnight format required",
            "objection": (
                "Proposed format requires 24-hour overnight access, but selected venue "
                "prohibits overnight occupation."
            ),
            "recommendation": "Select 24/7 accessible engineering lab facility."
        })
    return objections


def critique_judging(draft):
    """Judging coordinator independently audits evaluation feasibility."""
    objections = []
    if "09:00 to 21:00" in draft["schedule"] and draft["required_demo_hours"] > 3:
        objections.append({
            "objecting_role": "judging",
            "severity": "MEDIUM",
            "target": "schedule",
            "observed_value": draft["schedule"],
            "threshold": f"{draft['required_demo_hours']} hours demo window",
            "objection": (
                f"Schedule ending at 21:00 does not allocate the mandatory "
                f"{draft['required_demo_hours']} hours for live project deliberations."
            ),
            "recommendation": "Extend checkout window to 23:00."
        })
    return objections


def critique_logistics(draft):
    """Logistics agent reviews merged plan for setup feasibility."""
    return []  # No internal conflict from logistics perspective


CRITIQUE_ROLES = {
    "budget": critique_budget,
    "research": critique_research,
    "judging": critique_judging,
    "logistics": critique_logistics,
}


def run_distributed_critique(draft):
    """
    Executes distributed critique concurrently across all roles.
    Each agent independently audits the shared draft against its own domain rules.
    """
    distributed_conflict_log = []
    with ThreadPoolExecutor(max_workers=len(CRITIQUE_ROLES)) as pool:
        futures = {role: pool.submit(fn, draft) for role, fn in CRITIQUE_ROLES.items()}
        for role, future in futures.items():
            role_objections = future.result()
            distributed_conflict_log.extend(role_objections)
    return distributed_conflict_log


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 8 - Assignment 2: Distributed Multi-Agent Critique Architecture")
    print("================================================================================\n")

    # Phase 1: Parallel proposals
    print("--- 1. Generating Parallel Swarm Proposals ---")
    outputs = run_swarm(goal="Plan college AI hackathon")
    draft = merge(outputs)
    print("Consolidated Initial Draft:")
    print(json.dumps(draft, indent=2))

    # Phase 2: Distributed Critique
    print("\n--- 2. Executing Distributed Critique (Independent Agent Review) ---")
    conflict_log = run_distributed_critique(draft)

    print(f"\nTotal Independent Objections Raised: {len(conflict_log)}\n")
    for i, obj in enumerate(conflict_log, 1):
        print(f"[{i}] OBJECTING ROLE: <{obj['objecting_role'].upper()}> (Severity: {obj['severity']})")
        print(f"    Target Component: {obj['target']}")
        print(f"    Objection:        {obj['objection']}")
        print(f"    Recommendation:   {obj['recommendation']}\n")

    # Verification of multi-role objections
    roles_raising_objections = sorted(list(set(o["objecting_role"] for o in conflict_log)))
    print("=== Verification of Assignment Criteria ===")
    print(f"Distinct roles independently raising objections: {roles_raising_objections}")
    assert len(roles_raising_objections) >= 2, "Expected at least 2 distinct roles to raise objections"
    print(f"SUCCESS: {len(roles_raising_objections)} distinct roles independently raised objections against the merged draft.")

