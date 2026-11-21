"""
Lab 11: Agentic SDLC Factory -- Assignment 2: Prove Test Independence With a Deliberate Bug

Assignment Requirement:
Introduce a deliberate bug into `coding_agent`'s filter logic (e.g. an off-by-one
or inverted comparison) without changing `testing_agent`. Run the pipeline and
confirm the independently-generated tests catch the regression -- submit the
failing test output as evidence that the tests were not simply validating whatever
the code happened to do.
"""

import json

FEATURE_REQUEST = "Add CSV export to the reports page, preserving applied filters."


def requirement_agent(request):
    return [{
        "id": "US-1",
        "text": "As a user, I can export the current report view as a CSV file, preserving the applied filters.",
        "acceptance_criteria": [
            "clicking Export produces a .csv file",
            "the CSV contains only rows matching the currently applied filters",
            "the CSV header row matches the visible column names",
        ],
    }]


def design_agent(stories):
    return {
        "story_id": stories[0]["id"],
        "components": ["export_endpoint", "csv_serializer", "export_button (UI)"],
    }


# ---- Coding Agent with DELIBERATE BUG -----------------------------------
def coding_agent_with_deliberate_bug(design, stories):
    """
    Simulates a flawed coding agent that introduces an inverted filter condition:
    uses '!=' instead of '==', exporting non-matching rows instead of matching rows.
    """
    def buggy_export_endpoint(rows, applied_filters, columns):
        # DELIBERATE BUG: Inverted comparison condition!
        # Instead of `all(r.get(k) == v)`, developer wrote `any(r.get(k) != v)`
        filtered = [r for r in rows if any(r.get(k) != v for k, v in applied_filters.items())]
        
        lines = [",".join(columns)]
        for r in filtered:
            lines.append(",".join(str(r.get(c, "")) for c in columns))
        return "\n".join(lines)

    return {
        "design_ref": design["components"],
        "export_endpoint": buggy_export_endpoint,
        "bug_introduced": "Inverted filter logic: filters out matching records instead of preserving them."
    }


# ---- Testing Agent: COMPLETELY UNTOUCHED --------------------------------
def testing_agent(stories):
    """
    Generates tests from the STORY's acceptance criteria ONLY.
    Completely independent from coding agent implementation.
    """
    ac = stories[0]["acceptance_criteria"]

    def test_suite(export_fn):
        rows = [
            {"region": "North", "sales": 100},
            {"region": "South", "sales": 200},
            {"region": "North", "sales": 150},
        ]
        columns = ["region", "sales"]
        csv_out = export_fn(rows, {"region": "North"}, columns)
        lines = csv_out.splitlines()

        results = []
        # AC 1: Produces output
        results.append(("produces output", len(csv_out) > 0))
        
        # AC 3: Header matches visible columns
        results.append(("header matches columns", lines[0] == "region,sales" if lines else False))
        
        # AC 2: Only rows matching filter ('North') present; 'South' must NOT appear
        filter_check_passed = (
            len(lines) > 1 and
            all("South" not in line for line in lines[1:]) and
            all("North" in line for line in lines[1:])
        )
        results.append(("only filtered rows present (AC: matching filters preserved)", filter_check_passed))

        return results, ac, csv_out

    return test_suite


def review_agent(design, code, test_results):
    issues = []
    if len(code["design_ref"]) < 2:
        issues.append("design under-specified: fewer than 2 components")
    failed_tests = [name for name, passed in test_results if not passed]
    if failed_tests:
        issues.append(f"regression caught by tests: {failed_tests}")
    return {"issues": issues, "clean": len(issues) == 0}


def human_final_decision(review):
    print("\n[HUMAN CHECKPOINT] Evaluating review report and test findings...")
    if not review["clean"]:
        print("  DECISION: REJECT PULL REQUEST! Code failed independent acceptance test criteria.")
        return "reject"
    return "accept"


def release_agent(decision, stories):
    if decision != "accept":
        return {
            "released": False,
            "status": "BLOCKED_FROM_RELEASE",
            "reason": "Independent tests detected acceptance criteria violation. Release halted."
        }
    return {"released": True}


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 11 - Assignment 2: Test Independence Verification via Deliberate Bug Injection")
    print("================================================================================\n")

    stories = requirement_agent(FEATURE_REQUEST)
    design = design_agent(stories)

    # 1. Synthesize buggy code
    print("--- 1. Coding Agent Generates Implementation with Deliberate Filter Inversion ---")
    code = coding_agent_with_deliberate_bug(design, stories)
    print(f"Deliberate Bug: {code['bug_introduced']}\n")

    # 2. Run untouched independent test suite
    print("--- 2. Executing Untouched Independent Test Suite ---")
    test_suite = testing_agent(stories)
    test_results, acceptance_criteria, raw_output = test_suite(code["export_endpoint"])

    print("Raw CSV Output Generated by Buggy Code:")
    print("---------------------------------------")
    print(raw_output)
    print("---------------------------------------\n")

    print("=== Test Execution Results ===")
    for name, passed in test_results:
        status_tag = "PASS" if passed else "FAIL (REGRESSION CAUGHT)"
        print(f"  [{status_tag}] {name}")

    # 3. Review and Gate
    review = review_agent(design, code, test_results)
    print(f"\nReview Agent Report: {review}")

    decision = human_final_decision(review)
    release = release_agent(decision, stories)
    print(f"\nRelease Gate Verdict:\n{json.dumps(release, indent=2)}")

    # Verification Assertion
    assert any(not passed for _, passed in test_results), "Independent test suite MUST catch the deliberate bug!"
    assert release["released"] is False
    print("\nSUCCESS: Independent tests caught the regression. Proves tests evaluate specifications, not implementation quirks.")

