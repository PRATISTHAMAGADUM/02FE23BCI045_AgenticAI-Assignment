# Lab 3 - Assignment 2: Test Against a Low-Evidence Input

## Objective
Evaluate the skill against a promotional marketing whitepaper (`ARTICLE_D`) that asserts an expansive claim but offers no empirical supporting evidence or limitation. Confirm that the skill's constraint layer reliably populates `"not stated in source"` for missing fields rather than fabricating or hallucinating plausible-sounding evidence.

## Key Implementation Details
1. **Low-Evidence Text Definition**:
   - `ARTICLE_D`: *"Autonomous AI agents will revolutionize all enterprise business operations by 2030 and boost global worker productivity exponentially. Every organization will seamlessly achieve total workflow transformation."*
2. **Constraint Enforcement**:
   - Evaluates text against empirical indicators (metrics, baselines, benchmarks).
   - Because no indicators are present, `evidence` is set to `"not stated in source"`.
   - Because no hedges/caveats are present, `limitation` is set to `"not stated in source"`.
   - The undergraduate takeaway marks the claim as an unsupported assertion requiring empirical verification.
3. **Anti-Fabrication Confirmation**:
   - Programmatic verification confirms both fields returned `"not stated in source"`.
   - Explicit confirmation statement: *"The skill's constraint enforcement successfully returned 'not stated in source' for both the evidence and limitation fields on ARTICLE_D without fabricating or hallucinating any plausible-sounding content."*

## How to Run
```bash
python solution.py
```
Output results are captured in `output.txt`.

