# Lab 3 - Assignment 1: Handle a Multi-Claim Source

## Objective
Extend `apply_research_summary_skill` to process documents presenting multiple unrelated claims (e.g., cost reduction vs. code synthesis accuracy). The skill must evaluate competing claims, select the one with the strongest empirical supporting evidence, and explicitly record in the output contract why that specific claim was chosen rather than blindly defaulting to the first sentence.

## Key Implementation Details
1. **Multi-Claim Evaluation**: Added `ARTICLE_C` with two distinct claims:
   - Claim 1 (Cost): Quantization reduced inference costs by 38% across 50 clusters, sustained over 90 days.
   - Claim 2 (Accuracy): Code synthesis accuracy improved on internal test sets (asserted without metrics).
2. **Empirical Evidence Scoring**: Implemented `evaluate_evidence_score()` to quantify evidence presence (percentages, benchmarks, durations, clusters, dollars).
3. **Transparent Selection Field**: Added `selection_rationale` to the output schema. For `ARTICLE_C`, it records:
   `Multi-claim source detected (2 competing claims). Selected primary claim 'Adopting 4-bit model quantization...' (Evidence score: 10) over secondary claim 'In addition, autonomous code synthesis...' (Evidence score: 0) due to verified empirical measurements.`
4. **Backward Compatibility**: Single-claim articles (`ARTICLE_A`) continue to pass reusability checks cleanly.

## How to Run
```bash
python solution.py
```
Output results are captured in `output.txt`.

