"""
Lab 1: Agent vs Chatbot -- Assignment 1: Two Rounds of Feedback

Assignment Requirement:
Extend the reference agent to accept a second, independent round of feedback
after the first revision (e.g. "also make Friday's session shorter, only one hour").
Both revisions must mutate the same plan object -- the log must show two separate
revise iterations, neither of which regenerates the plan from scratch.
Submit the updated code and the full iteration log covering both rounds.
"""

import json

# ---- Simulated inputs (stand in for what a real user would type) ----
SIMULATED_ANSWERS = {
    "subjects": ["Data Structures", "Operating Systems", "AI Agents"],
    "hours_per_day": 2,
    "unavailable_days": ["Sunday"],
}

ROUND_1_FEEDBACK = "Move Tuesday's session to the evening."
ROUND_2_FEEDBACK = "Also make Friday's session shorter, only one hour."


class StudyPlannerAgent:
    def __init__(self, existing_schedule):
        # Goal modeled as data -- a checkable predicate, not prose.
        self.goal = {
            "subjects": None,
            "hours_per_day": None,
            "unavailable_days": None,
            "schedule_generated": False,
        }
        self.existing_schedule = existing_schedule
        self.plan = None
        self.log = []

    # ---- Goal check -------------------------------------------------
    def satisfied(self):
        return self.goal["schedule_generated"] is True

    # ---- Planner: decide the next step ------------------------------
    def next_step(self):
        for field in ("subjects", "hours_per_day", "unavailable_days"):
            if self.goal[field] is None:
                return ("ask", field)
        return ("generate_plan", None)

    # ---- Tool: read existing schedule (Act) -------------------------
    def read_existing_schedule(self):
        result = self.existing_schedule
        if "error" in result:
            raise RuntimeError(f"tool error: {result['error']}")
        return result

    # ---- Core loop ----------------------------------------------------
    def run(self):
        while not self.satisfied():
            step, arg = self.next_step()

            if step == "ask":
                answer = SIMULATED_ANSWERS[arg]      # Act: ask only what's missing
                self.goal[arg] = answer               # Observe: record the real answer
                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": f"ask for {arg}",
                    "action": f"asked user for {arg}",
                    "observed": answer,
                    "stopped": False,
                })

            elif step == "generate_plan":
                busy = self.read_existing_schedule()          # Act: tool call
                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": "read existing schedule before generating plan",
                    "action": "tool call: read_existing_schedule()",
                    "observed": busy,
                    "stopped": False,
                })
                self.plan = self._build_plan(busy)             # Revise/build
                self.goal["schedule_generated"] = True
                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": "generate schedule from gathered requirements",
                    "action": "built weekly plan",
                    "observed": self.plan,
                    "stopped": True,
                    "stop_reason": "goal.schedule_generated is now True",
                })
        return self.plan

    # ---- Build the actual plan object -------------------------------
    def _build_plan(self, busy_slots):
        days = [d for d in
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                if d not in self.goal["unavailable_days"]]
        subjects = self.goal["subjects"]
        plan = {}
        for i, day in enumerate(days):
            subject = subjects[i % len(subjects)]
            slot = "17:00-19:00"
            if day in busy_slots.get("busy_days", []):
                slot = "20:00-22:00"   # avoid the clash observed from the tool
            plan[day] = {"subject": subject, "time": slot, "duration_hours": self.goal["hours_per_day"]}
        return plan

    # ---- Revise on user feedback (mutate, don't restart) ------------
    def revise(self, feedback, round_num=1):
        self.log.append({
            "iteration": len(self.log) + 1,
            "planned": f"apply user feedback round {round_num} to existing plan",
            "action": f"feedback received (round {round_num}): '{feedback}'",
            "observed": None,
            "stopped": False,
        })
        
        # Rule-based simulated LLM revision parser mutating self.plan
        fb_lower = feedback.lower()
        if "tuesday" in fb_lower and "evening" in fb_lower:
            if "Tuesday" in self.plan:
                self.plan["Tuesday"]["time"] = "20:00-22:00"
        
        if "friday" in fb_lower and ("shorter" in fb_lower or "one hour" in fb_lower):
            if "Friday" in self.plan:
                # Shorten from 2 hours to 1 hour (17:00-18:00)
                self.plan["Friday"]["time"] = "17:00-18:00"
                self.plan["Friday"]["duration_hours"] = 1
                self.plan["Friday"]["note"] = "shortened to 1 hour per user feedback"

        self.log.append({
            "iteration": len(self.log) + 1,
            "planned": f"confirm revised plan after round {round_num}",
            "action": f"mutated existing plan in place for round {round_num} (no regeneration from scratch)",
            "observed": json.loads(json.dumps(self.plan)),  # snapshot of mutated plan
            "stopped": True,
            "stop_reason": f"round {round_num} revision applied without restarting loop",
        })
        return self.plan


if __name__ == "__main__":
    existing_schedule = {"busy_days": ["Wednesday"]}
    agent = StudyPlannerAgent(existing_schedule)

    print("================================================================================")
    print("Lab 1 - Assignment 1: Two Rounds of Feedback Mutating the Same Plan Object")
    print("================================================================================\n")

    print("Stopping condition (declared before the loop runs):")
    print("  goal['schedule_generated'] is True\n")

    # Initial Run
    initial_plan = agent.run()
    plan_obj_id = id(agent.plan)
    print("=== Initial Plan ===")
    print(json.dumps(initial_plan, indent=2))
    print(f"Plan object memory ID: {plan_obj_id}\n")

    # Round 1 Feedback
    print(f"--- Applying Round 1 Feedback: \"{ROUND_1_FEEDBACK}\" ---")
    revised_round_1 = agent.revise(ROUND_1_FEEDBACK, round_num=1)
    print("=== Plan After Round 1 Revision ===")
    print(json.dumps(revised_round_1, indent=2))
    print(f"Plan object memory ID (unchanged): {id(agent.plan)} (Same instance: {id(agent.plan) == plan_obj_id})\n")

    # Round 2 Feedback
    print(f"--- Applying Round 2 Feedback: \"{ROUND_2_FEEDBACK}\" ---")
    revised_round_2 = agent.revise(ROUND_2_FEEDBACK, round_num=2)
    print("=== Plan After Round 2 Revision ===")
    print(json.dumps(revised_round_2, indent=2))
    print(f"Plan object memory ID (unchanged): {id(agent.plan)} (Same instance: {id(agent.plan) == plan_obj_id})\n")

    # Verification and Full Log
    print("=== Full Iteration Log (Showing Both Revision Rounds) ===")
    for entry in agent.log:
        print(json.dumps(entry, indent=2))

