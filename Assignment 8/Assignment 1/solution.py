"""
Lab 8: Parallel Swarm -- Assignment 1: Add a Fifth Role: Marketing

Assignment Requirement:
Add a `marketing_agent` role proposing a publicity plan with its own cost.
Extend `critique()` to detect a new conflict between the marketing budget and
the same overall budget cap, and resolve it with the same `budget_over_preference`
rule. Submit the updated code and the extended conflict log.
"""

from concurrent.futures import ThreadPoolExecutor
import json


# ---- Parallel Agents ----------------------------------------------------
def research_agent(goal):
    return {"role": "research", "output": "Past events favored a 24-hour format with themed tracks."}


def logistics_agent(goal):
    return {"role": "logistics", "output": {"venue": "Grand Hall", "venue_cost": 45000, "date": "Saturday"}}


def budget_agent(goal):
    return {"role": "budget", "output": {"total_cap": 30000}}


def judging_agent(goal):
    return {"role": "judging", "output": "Judge on innovation, technical depth, and demo quality."}


# Fifth Role: Marketing Agent
def marketing_agent(goal):
    return {
        "role": "marketing",
        "output": {
            "campaign": "Multi-tier social blitz, custom swag, campus billboards",
            "marketing_cost": 12000,
            "target_reach": 5000
        }
    }


ROLES = {
    "research": research_agent,
    "logistics": logistics_agent,
    "budget": budget_agent,
    "judging": judging_agent,
    "marketing": marketing_agent,  # Added 5th role
}


def run_swarm(goal):
    with ThreadPoolExecutor(max_workers=len(ROLES)) as pool:
        futures = {name: pool.submit(fn, goal) for name, fn in ROLES.items()}
        outputs = {name: f.result() for name, f in futures.items()}
    return outputs


def merge(outputs):
    return {
        "format_notes": outputs["research"]["output"],
        "venue": outputs["logistics"]["output"]["venue"],
        "venue_cost": outputs["logistics"]["output"]["venue_cost"],
        "date": outputs["logistics"]["output"]["date"],
        "budget_cap": outputs["budget"]["output"]["total_cap"],
        "judging_criteria": outputs["judging"]["output"],
        "marketing_campaign": outputs["marketing"]["output"]["campaign"],
        "marketing_cost": outputs["marketing"]["output"]["marketing_cost"],
        "total_requested_spend": (
            outputs["logistics"]["output"]["venue_cost"] +
            outputs["marketing"]["output"]["marketing_cost"]
        ),
    }


def critique(draft):
    conflicts = []
    budget_cap = draft["budget_cap"]

    # Conflict 1: Venue cost exceeds budget cap
    if draft["venue_cost"] > budget_cap:
        conflicts.append({
            "conflict": "venue_cost exceeds budget_cap",
            "roles_involved": ["logistics", "budget"],
            "requested_value": draft["venue_cost"],
            "budget_cap": budget_cap,
            "severity": "CRITICAL",
        })

    # Conflict 2: Marketing cost creates deficit against budget cap
    if draft["marketing_cost"] > (budget_cap * 0.25):  # Marketing exceeding 25% allocation limit
        conflicts.append({
            "conflict": "marketing_cost exceeds allocated marketing ceiling",
            "roles_involved": ["marketing", "budget"],
            "requested_value": draft["marketing_cost"],
            "budget_cap": budget_cap,
            "severity": "HIGH",
        })

    # Conflict 3: Combined total requested spend exceeds budget cap
    if draft["total_requested_spend"] > budget_cap:
        conflicts.append({
            "conflict": "combined requested spending exceeds total budget_cap",
            "roles_involved": ["logistics", "marketing", "budget"],
            "requested_value": draft["total_requested_spend"],
            "budget_cap": budget_cap,
            "severity": "FATAL",
        })

    return conflicts


def resolve(conflict, priority_rule="budget_over_preference"):
    c_type = conflict["conflict"]

    if c_type == "venue_cost exceeds budget_cap":
        return {
            "rule_applied": priority_rule,
            "resolution": (
                f"Reject venue at {conflict['requested_value']}; request logistics propose an "
                f"on-campus auditorium alternative under {int(conflict['budget_cap'] * 0.65)}."
            ),
        }

    if c_type == "marketing_cost exceeds allocated marketing ceiling":
        return {
            "rule_applied": priority_rule,
            "resolution": (
                f"Reject marketing spend of {conflict['requested_value']}; enforce {priority_rule} "
                f"by capping marketing at 3000 (10% of total budget) and utilizing student ambassador networks."
            ),
        }

    if c_type == "combined requested spending exceeds total budget_cap":
        return {
            "rule_applied": priority_rule,
            "resolution": (
                f"Enforce hard ceiling of {conflict['budget_cap']}; total spend of {conflict['requested_value']} "
                f"must be trimmed across both logistics and marketing before finalizing approvals."
            ),
        }

    return {"rule_applied": priority_rule, "resolution": "no rule matched"}


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 8 - Assignment 1: Parallel Swarm with 5th Role (Marketing) & Conflict Log")
    print("================================================================================\n")

    outputs = run_swarm(goal="Plan a college AI hackathon")
    print("=== 1. Parallel Role Outputs (5 Roles) ===")
    for name, out in outputs.items():
        print(f"  [{name.upper()}]: {out['output']}")

    draft = merge(outputs)
    print("\n=== 2. Merged Draft Plan ===")
    print(json.dumps(draft, indent=2))

    conflicts = critique(draft)
    print(f"\n=== 3. Swarm Critique ({len(conflicts)} Conflicts Detected) ===")
    conflict_log = []
    for c in conflicts:
        res = resolve(c)
        entry = {**c, **res}
        conflict_log.append(entry)
        print(f"\nConflict: [{c['severity']}] {c['conflict']}")
        print(f"  Roles:      {c['roles_involved']}")
        print(f"  Requested:  {c['requested_value']} vs Cap: {c['budget_cap']}")
        print(f"  Resolution: {res['resolution']}")

    print("\n=== 4. Final Extended Conflict Log (Artifact) ===")
    print(json.dumps(conflict_log, indent=2))

