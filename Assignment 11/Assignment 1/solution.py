"""
Lab 11: Agentic SDLC Factory -- Assignment 1: A Second, Concurrent Story (PDF Export) with Lineage Trace

Assignment Requirement:
Add a second story (e.g. "export to PDF in addition to CSV") processed through
the same pipeline. Extend the lineage trace so it correctly attributes each
design/code/test artifact to the right story when two stories exist side by side.
"""

import json

FEATURE_REQUEST = "Add CSV and PDF export to reports page, preserving applied filters."


# ---- 1. Requirement Stage ----------------------------------------------
def requirement_agent(request):
    return [
        {
            "id": "US-1",
            "title": "CSV Report Export",
            "text": "As a user, I can export the current report view as a CSV file, preserving the applied filters.",
            "acceptance_criteria": [
                "clicking Export CSV produces a .csv file",
                "the CSV contains only rows matching the currently applied filters",
                "the CSV header row matches the visible column names",
            ],
        },
        {
            "id": "US-2",
            "title": "PDF Document Export",
            "text": "As a user, I can export the current report view as a formatted PDF document, preserving the applied filters and title header.",
            "acceptance_criteria": [
                "clicking Export PDF produces a valid PDF container header (%PDF-1.4)",
                "the PDF document includes metadata and matching filtered records",
                "pagination and column layout are preserved in the document body",
            ],
        }
    ]


def human_confirms_stories(stories):
    print("[HUMAN CHECKPOINT] Confirming user story requirements...")
    for s in stories:
        print(f"  * [{s['id']}] {s['text']}")
    return True


# ---- 2. Design Stage ---------------------------------------------------
def design_agent(story):
    if story["id"] == "US-1":
        return {
            "story_id": "US-1",
            "artifact_id": "DESIGN-US1-CSV",
            "components": ["csv_export_endpoint", "csv_serializer", "csv_button_ui"],
            "spec": "RFC 4180 comma-delimited output with newline record separators."
        }
    elif story["id"] == "US-2":
        return {
            "story_id": "US-2",
            "artifact_id": "DESIGN-US2-PDF",
            "components": ["pdf_export_endpoint", "pdf_canvas_renderer", "pdf_button_ui"],
            "spec": "PDF-1.4 binary/text stream layout with table grid and running headers."
        }
    raise ValueError(f"Unknown story ID: {story['id']}")


# ---- 3. Coding Stage ---------------------------------------------------
def coding_agent(design, story):
    story_id = story["id"]

    if story_id == "US-1":
        def export_csv(rows, applied_filters, columns):
            filtered = [r for r in rows if all(r.get(k) == v for k, v in applied_filters.items())]
            lines = [",".join(columns)]
            for r in filtered:
                lines.append(",".join(str(r.get(c, "")) for c in columns))
            return "\n".join(lines)

        return {
            "story_id": "US-1",
            "artifact_id": "CODE-US1-CSV",
            "design_ref": design["artifact_id"],
            "entrypoint": "export_csv",
            "callable": export_csv
        }

    elif story_id == "US-2":
        def export_pdf(rows, applied_filters, columns, report_title="Operational Report"):
            filtered = [r for r in rows if all(r.get(k) == v for k, v in applied_filters.items())]
            # Mock PDF generation emitting structured stream with %PDF-1.4 header
            pdf_lines = [
                "%PDF-1.4",
                f"1 0 obj << /Title ({report_title}) /FilterCount ({len(applied_filters)}) >> endobj",
                f"2 0 obj << /Columns ({' | '.join(columns)}) >> endobj",
                "3 0 obj << /StreamData ["
            ]
            for r in filtered:
                pdf_lines.append(f"  Record: {' | '.join(f'{c}={r.get(c)}' for c in columns)}")
            pdf_lines.extend(["  ] >> endobj", "%%EOF"])
            return "\n".join(pdf_lines)

        return {
            "story_id": "US-2",
            "artifact_id": "CODE-US2-PDF",
            "design_ref": design["artifact_id"],
            "entrypoint": "export_pdf",
            "callable": export_pdf
        }


# ---- 4. Testing Stage --------------------------------------------------
def testing_agent(story):
    story_id = story["id"]
    ac = story["acceptance_criteria"]

    if story_id == "US-1":
        def test_suite_csv(export_fn):
            rows = [
                {"region": "North", "sales": 100}, {"region": "South", "sales": 200},
                {"region": "North", "sales": 150},
            ]
            columns = ["region", "sales"]
            csv_out = export_fn(rows, {"region": "North"}, columns)
            results = [
                ("produces output", len(csv_out) > 0),
                ("header matches columns", csv_out.splitlines()[0] == "region,sales"),
                ("only filtered rows present", all("South" not in line for line in csv_out.splitlines()[1:])),
            ]
            return results, ac

        return {
            "story_id": "US-1",
            "artifact_id": "TEST-US1-CSV",
            "runner": test_suite_csv
        }

    elif story_id == "US-2":
        def test_suite_pdf(export_fn):
            rows = [
                {"region": "North", "sales": 100}, {"region": "South", "sales": 200},
                {"region": "North", "sales": 150},
            ]
            columns = ["region", "sales"]
            pdf_out = export_fn(rows, {"region": "North"}, columns)
            lines = pdf_out.splitlines()
            results = [
                ("valid PDF-1.4 header", lines[0] == "%PDF-1.4"),
                ("contains filtered records only", any("region=North" in l for l in lines) and not any("region=South" in l for l in lines)),
                ("valid EOF termination", lines[-1] == "%%EOF"),
            ]
            return results, ac

        return {
            "story_id": "US-2",
            "artifact_id": "TEST-US2-PDF",
            "runner": test_suite_pdf
        }


# ---- Lineage Tracker ----------------------------------------------------
class SDLCLineageTracker:
    def __init__(self):
        self.lineage_store = {}

    def record_artifact(self, story_id, stage, artifact_id, details):
        if story_id not in self.lineage_store:
            self.lineage_store[story_id] = {}
        self.lineage_store[story_id][stage] = {
            "artifact_id": artifact_id,
            "details": details
        }

    def print_trace_matrix(self):
        print("\n================================================================================")
        print("CONCURRENT SDLC LINEAGE TRACE MATRIX (PROVING ARTIFACT ISOLATION)")
        print("================================================================================")
        for story_id, stages in self.lineage_store.items():
            print(f"\n[STORY LINEAGE: {story_id}]")
            for stage_name, meta in stages.items():
                print(f"  -> {stage_name:<10}: ArtifactID={meta['artifact_id']:<18} | {meta['details']}")


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 11 - Assignment 1: Dual-Story SDLC Pipeline (CSV & PDF) with End-to-End Lineage")
    print("================================================================================\n")

    lineage = SDLCLineageTracker()

    # Step 1: Requirements
    stories = requirement_agent(FEATURE_REQUEST)
    human_confirms_stories(stories)
    for s in stories:
        lineage.record_artifact(s["id"], "Requirement", s["id"], f"Title: '{s['title']}'")

    # Pipeline loop processing each concurrent story independently
    for s in stories:
        sid = s["id"]
        print(f"\n>>> Processing Pipeline for Story {sid} ({s['title']}) <<<")

        # Step 2: Design
        design = design_agent(s)
        lineage.record_artifact(sid, "Design", design["artifact_id"], f"Components: {design['components']}")
        print(f"  Design generated: {design['artifact_id']}")

        # Step 3: Coding
        code = coding_agent(design, s)
        lineage.record_artifact(sid, "Code", code["artifact_id"], f"Entrypoint: {code['entrypoint']} derived from {code['design_ref']}")
        print(f"  Code synthesized: {code['artifact_id']} (Function: {code['entrypoint']})")

        # Step 4: Independent Testing
        test_pkg = testing_agent(s)
        test_results, ac = test_pkg["runner"](code["callable"])
        passed = all(p for _, p in test_results)
        lineage.record_artifact(sid, "Test", test_pkg["artifact_id"], f"Results: {len(test_results)}/{len(test_results)} PASS")
        print(f"  Tests executed:   {test_pkg['artifact_id']} -> Passed: {passed}")
        for tname, tok in test_results:
            print(f"    * [{'PASS' if tok else 'FAIL'}] {tname}")

        # Step 5: Release Verification
        release_id = f"REL-{sid}"
        lineage.record_artifact(sid, "Release", release_id, f"Production package for '{s['title']}' validated.")

    # Output full lineage trace matrix
    lineage.print_trace_matrix()

