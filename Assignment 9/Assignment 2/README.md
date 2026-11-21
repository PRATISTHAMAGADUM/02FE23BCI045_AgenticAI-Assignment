# Lab 9 - Assignment 2: Weight Sources by Quality

## Objective
Establish a formal source-quality hierarchy (Tier 1: Peer-Reviewed Publications > Tier 2: Independent Third-Party Benchmarks > Tier 3: Vendor Engineering Blogs). In the event of conflicting empirical claims, `synthesize()` must determine which claim to lean toward using tier weighting, while explicitly disclosing that the lower-tier claim was down-weighted rather than discarded.

## Key Implementation Details
1. **Tier Taxonomy & Weighting**:
   - `tier_1_peer_reviewed`: Weight = 1.0 (Formal peer review, reproducible public baselines).
   - `tier_2_independent_benchmark`: Weight = 0.75 (Standardized neutral testbeds).
   - `tier_3_vendor_blog`: Weight = 0.4 (Internal, non-replicated, commercial context).
2. **Empirical Conflict Evaluated**:
   - S2 (Vendor) claimed 98% accuracy and total elimination of hallucinations.
   - S1 (Peer-reviewed) observed a 41% reduction; S4 (Independent benchmark) observed 8–12% reduction on complex cases.
3. **Transparent Synthesis Decision**:
   - The synthesis leans decisively toward S1 and S4, concluding that practical hallucination reduction ranges from 8% to 41%.
   - Explicit disclosure: *"The claim by [S2] (Tier 3 Vendor Blog, Weight: 0.4) was DOWN-WEIGHTED due to lack of open reproducible baselines and commercial incentive, but NOT DISCARDED. It is retained as indicative evidence that in narrow, highly-curated single-turn customer support workflows... RAG can reach high practical accuracy."*

## How to Run
```bash
python solution.py
```
Outputs and tier-weighted synthesis decisions are captured in `output.txt`.

