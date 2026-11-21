"""
Lab 9: Deep Research Agent -- Assignment 1: Add a Directly Contradicting Source

Assignment Requirement:
Add a fourth source, S4, whose claim directly contradicts S1's hallucination-reduction
figure (e.g. reporting no measurable improvement in a different evaluation).
Update `compare()` and `synthesize()` to report this as a genuine conflict -- not a gap --
and to state a plausible reason for the disagreement (different evaluation methodology,
different domain, different dataset size).
"""

import json

QUESTION = (
    "What are the demonstrated benefits and limitations of retrieval-augmented "
    "generation (RAG) for domain-specific question answering, as of the last year?"
)

# Extended sources including S4 which directly contradicts S1
SOURCES = [
    {
        "id": "S1",
        "type": "peer-reviewed paper",
        "date": "2026-02",
        "claim": "RAG reduces hallucination rate by 41% on domain QA vs a non-retrieval baseline.",
        "evidence": "200 held-out questions from a medical knowledge base.",
        "limitation": "Small, single-domain evaluation set; single-hop factual questions only."
    },
    {
        "id": "S2",
        "type": "vendor engineering blog",
        "date": "2026-04",
        "claim": "RAG improves answer accuracy by 35% in an internal support-ticket QA system.",
        "evidence": "Internal A/B test over 10,000 tickets.",
        "limitation": "Funded/internal evaluation; no independent replication reported."
    },
    {
        "id": "S3",
        "type": "independent benchmark report",
        "date": "2026-05",
        "claim": "RAG introduces a measurable latency overhead of 200-400ms per query.",
        "evidence": "Benchmarked across 5 open-source RAG pipelines.",
        "limitation": "Latency depends heavily on retrieval index size; not tested at scale."
    },
    # Newly added 4th source contradicting S1
    {
        "id": "S4",
        "type": "multi-center clinical benchmark",
        "date": "2026-06",
        "claim": "RAG yields no statistically significant reduction in hallucination rates (< 1.5% delta, p=0.42) on multi-hop clinical diagnostic queries.",
        "evidence": "1,200 multi-hop reasoning clinical cases evaluated across 4 hospital networks.",
        "limitation": "Tested only on complex multi-hop queries where retrieved passage fragments diluted reasoning context."
    },
]


def compare(sources):
    agreements, direct_conflicts, performance_gaps = [], [], []

    # Check for genuine contradiction between S1 and S4
    s1 = next((s for s in sources if s["id"] == "S1"), None)
    s4 = next((s for s in sources if s["id"] == "S4"), None)

    if s1 and s4:
        direct_conflicts.append({
            "type": "GENUINE_EMPIRICAL_CONTRADICTION",
            "sources": ["S1", "S4"],
            "claim_a (S1)": s1["claim"],
            "claim_b (S4)": s4["claim"],
            "conflict_description": (
                "S1 claims RAG achieves a 41% reduction in hallucinations, whereas S4 reports "
                "no measurable reduction (< 1.5% variance) in clinical hallucination rates."
            ),
            "reasons_for_disagreement": [
                "Evaluation Methodology: S1 tested single-hop factual lookup where retrieved chunks directly answer queries; S4 tested multi-hop diagnostic reasoning where fragmented context chunks introduced distractor noise.",
                "Dataset Scale: S1 evaluated a small sample of 200 questions, whereas S4 evaluated a large cohort of 1,200 cases across 4 hospital systems.",
                "Domain Specificity: S1 utilized general medical knowledge-base articles; S4 tested specialized real-world clinical differential diagnoses."
            ]
        })

    # Cross-source agreements
    agreements.append(
        "S1 and S2 agree that standard single-domain factual queries benefit from retrieval augmentation (35-41% accuracy/hallucination gains)."
    )

    # Latency gap
    performance_gaps.append(
        "S3 identifies a 200-400ms latency penalty. This represents an operational trade-off/gap unaddressed by accuracy-focused sources S1 and S2."
    )

    return {
        "agreements": agreements,
        "direct_conflicts": direct_conflicts,
        "performance_gaps": performance_gaps,
    }


def synthesize(evidence_table, comparison):
    lines = []
    lines.append("=== EXECUTIVE BRIEFING ON RAG EFFECTIVENESS ===")
    for row in evidence_table:
        lines.append(f"[{row['id']}] ({row['type']}, {row['date']}): {row['claim']}")

    lines.append("\n--- Cross-Source Consensus ---")
    for a in comparison["agreements"]:
        lines.append(f"[Consensus] {a}")

    lines.append("\n--- Genuine Conflicts & Contradictions (Critical Finding) ---")
    for c in comparison["direct_conflicts"]:
        lines.append(f"[{','.join(c['sources'])}] {c['conflict_description']}")
        lines.append("  Plausible Disagreement Drivers:")
        for r in c["reasons_for_disagreement"]:
            lines.append(f"    * {r}")

    lines.append("\n--- Operational Trade-Offs & Gaps ---")
    for g in comparison["performance_gaps"]:
        lines.append(f"[Operational Trade-Off] {g}")

    return lines


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 9 - Assignment 1: Deep Research Agent with Direct Contradiction Analysis")
    print("================================================================================\n")

    print(f"Research Question: {QUESTION}\n")

    comparison = compare(SOURCES)
    summary_lines = synthesize(SOURCES, comparison)

    for line in summary_lines:
        print(line)

