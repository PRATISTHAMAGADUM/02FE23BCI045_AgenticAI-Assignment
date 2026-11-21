# Lab 9 - Assignment 1: Add a Directly Contradicting Source

## Objective
Introduce a fourth evidence source (`S4`) that directly contradicts `S1`'s reported 41% hallucination reduction by finding no statistically significant improvement. Update `compare()` and `synthesize()` to classify this finding as a genuine empirical conflict (rather than a benign performance gap or silent omission) and detail plausible root causes for the divergence across methodology, scale, and reasoning complexity.

## Key Implementation Details
1. **Contradicting Evidence Source (`S4`)**:
   - `id`: `"S4"`, multi-center clinical evaluation (dated 2026-06).
   - Claim: RAG produces no statistically significant reduction in hallucination rates (< 1.5% delta, p=0.42) on complex multi-hop clinical diagnostic questions.
2. **Conflict vs Gap Distinction**:
   - Gaps (e.g., latency in S3) describe unmeasured operational dimensions.
   - Conflicts (S1 vs S4) describe direct empirical disagreement on the same metric (hallucination reduction).
3. **Plausible Disagreement Drivers**:
   - **Evaluation Complexity**: Single-hop factual queries (S1) benefit from chunk retrieval, while multi-hop reasoning (S4) suffers from context fragmentation and distractor chunks.
   - **Sample Size**: Small test set (200 questions in S1) vs. large-scale multi-hospital cohort (1,200 cases in S4).
   - **Domain Realism**: Curated reference knowledge vs. complex clinical differential diagnosis.

## How to Run
```bash
python solution.py
```
Outputs and briefing summaries are stored in `output.txt`.

