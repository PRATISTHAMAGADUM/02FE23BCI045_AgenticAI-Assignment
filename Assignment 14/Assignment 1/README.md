# Lab 14 - Assignment 1: Add a Second Reusable Skill

## Objective
Expand the Capstone Help-Desk System by integrating a second reusable skill: `password_reset_guidance_skill`, complete with its own operational instructions, security constraints (anti-credential harvesting, mandatory MFA portal routing), and supporting tool. Enhance the intake node graph router to dynamically select between `triage_skill` and `password_reset_guidance_skill` based on incoming query classification.

## Key Implementation Details
1. **Second Skill Package (`password_reset_guidance_skill`)**:
   - Backed by `tool_generate_password_reset_token`.
   - Security constraints: Strictly forbids capturing plain-text passwords or secret answers in chat; provides time-delimited self-service URL (`https://identity.campus.edu/self-service/reset`) requiring 2-Factor Authentication.
2. **Node Graph Routing Logic**:
   - Inspects issue semantics: Credential/password-related requests route directly to `password_reset_guidance_skill`.
   - Standard inquiries route to `triage_skill` (FAQ DB lookup or ticketing).
3. **Multi-Skill Execution Verification**:
   - Query 1 ("wifi"): Handled by `triage_skill` -> FAQ match.
   - Query 2 ("forgot password"): Handled by `password_reset_guidance_skill` -> Secure guidance issued.
   - Query 3 ("projector bulb"): Handled by `triage_skill` -> IT Support ticket generated.
   - All interactions audited and recorded in `CapstoneMemory`.

## How to Run
```bash
python solution.py
```
Outputs and routing traces are captured in `output.txt`.

