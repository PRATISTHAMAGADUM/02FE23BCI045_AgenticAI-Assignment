"""
Lab 1: Agent vs Chatbot -- Assignment 2: Detect a Scheduling Conflict

Assignment Requirement:
Extend `read_existing_schedule` to return a second busy day, then modify `_build_plan`
(or add a check before it) so that if the student's chosen unavailable days do not
actually avoid every busy day returned by the tool, the agent flags the conflict
explicitly to the user before finalizing the plan, rather than silently double-booking.
Submit the updated code and a transcript showing the conflict being detected and reported.
"""

import json

# ---- Simulated inputs ----
SIMULATED_ANSWERS = {
    "subjects": ["Data Structures", "Operating Systems", "AI Agents"],
    "hours_per_day": 2,
    "unavailable_days": ["Sunday"],  # Student only marked Sunday as unavailable
}

# External schedule tool data: returns TWO busy days ("Wednesday" and "Friday")
EXISTING_SCHEDULE_WITH_MULTIPLE_BUSY_DAYS = {
    "busy_days": ["Wednesday", "Friday"],
    "details": {
        "Wednesday": "Lab Exam: 14:00-19:30",
        "Friday": "Department Hackathon Preparation: 16:00-20:00"
    }
}


class StudyPlannerAgentWithConflictDetection:
    def __init__(self, existing_schedule):
        self.goal = {
            "subjects": None,
            "hours_per_day": None,
            "unavailable_days": None,
            "schedule_generated": False,
        }
        self.existing_schedule = existing_schedule
        self.plan = None
        self.conflicts_flagged = []
        self.log = []

    def satisfied(self):
        return self.goal["schedule_generated"] is True

    def next_step(self):
        for field in ("subjects", "hours_per_day", "unavailable_days"):
            if self.goal[field] is None:
                return ("ask", field)
        return ("generate_plan", None)

    # ---- Extended Tool: returns two busy days -----------------------
    def read_existing_schedule(self):
        result = self.existing_schedule
        if "error" in result:
            raise RuntimeError(f"tool error: {result['error']}")
        return result

    # ---- Conflict Detection Guard -----------------------------------
    def detect_conflicts(self, busy_info):
        """
        Validates whether student's chosen unavailable days cover all busy days
        discovered via the calendar tool. Flags any collisions explicitly.
        """
        busy_days = busy_info.get("busy_days", [])
        student_unavailable = set(self.goal.get("unavailable_days") or [])
        unavoided_busy_days = [day for day in busy_days if day not in student_unavailable]
        
        conflicts = []
        for day in unavoided_busy_days:
            detail = busy_info.get("details", {}).get(day, "External existing commitment")
            conflicts.append({
                "day": day,
                "conflict_detail": detail,
                "status": "UNRESOLVED_SCHEDULE_CLASH"
            })
        return conflicts

    # ---- Core loop ----------------------------------------------------
    def run(self):
        while not self.satisfied():
            step, arg = self.next_step()

            if step == "ask":
                answer = SIMULATED_ANSWERS[arg]
                self.goal[arg] = answer
                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": f"ask for {arg}",
                    "action": f"asked user for {arg}",
                    "observed": answer,
                    "stopped": False,
                })

            elif step == "generate_plan":
                # Step 1: Query calendar tool
                busy = self.read_existing_schedule()
                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": "read existing schedule before generating plan",
                    "action": "tool call: read_existing_schedule() -> returned multiple busy days",
                    "observed": busy,
                    "stopped": False,
                })

                # Step 2: Explicit conflict check BEFORE finalizing plan
                detected_conflicts = self.detect_conflicts(busy)
                if detected_conflicts:
                    self.conflicts_flagged = detected_conflicts
                    warning_msg = (
                        f"WARNING: Scheduling conflict detected! Tool reported busy days {busy.get('busy_days')}, "
                        f"but student unavailable days only cover {self.goal['unavailable_days']}. "
                        f"Unavoided busy days: {[c['day'] for c in detected_conflicts]}."
                    )
                    self.log.append({
                        "iteration": len(self.log) + 1,
                        "planned": "check for schedule collisions against tool data",
                        "action": "flag_scheduling_conflicts_to_user",
                        "observed": warning_msg,
                        "stopped": False,
                        "conflicts": detected_conflicts
                    })
                    print(f"\n>>> [AGENT ALERT TO USER] <<<\n{warning_msg}")
                    print("The agent will NOT silently double-book. Flagging conflicts explicitly in schedule output.")

                # Step 3: Build plan and annotate conflicts
                self.plan = self._build_plan(busy, detected_conflicts)
                self.goal["schedule_generated"] = True
                self.log.append({
                    "iteration": len(self.log) + 1,
                    "planned": "generate schedule with transparent conflict annotations",
                    "action": "built weekly plan with flagged conflicts",
                    "observed": self.plan,
                    "stopped": True,
                    "stop_reason": "goal.schedule_generated is True; conflicts flagged to user",
                })
        return self.plan

    def _build_plan(self, busy_slots, conflicts):
        days = [d for d in
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
                if d not in self.goal["unavailable_days"]]
        subjects = self.goal["subjects"]
        conflict_days = {c["day"]: c for c in conflicts}

        plan = {}
        for i, day in enumerate(days):
            subject = subjects[i % len(subjects)]
            slot = "17:00-19:00"
            status = "CONFIRMED"
            note = None

            if day in conflict_days:
                status = "CONFLICT_FLAGGED_NEEDS_REVIEW"
                note = f"ALERT: Overlaps with existing commitment ({conflict_days[day]['conflict_detail']}). Rescheduled to emergency late window 21:00-23:00 pending student confirmation."
                slot = "21:00-23:00 (TENTATIVE - CLASH FLAGGED)"
            
            plan[day] = {
                "subject": subject,
                "time": slot,
                "status": status,
                "note": note
            }
        return plan


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 1 - Assignment 2: Detect & Flag Scheduling Conflicts Before Finalizing")
    print("================================================================================\n")

    print(f"Tool Configuration: read_existing_schedule returns 2 busy days: {EXISTING_SCHEDULE_WITH_MULTIPLE_BUSY_DAYS['busy_days']}\n")
    agent = StudyPlannerAgentWithConflictDetection(EXISTING_SCHEDULE_WITH_MULTIPLE_BUSY_DAYS)

    plan = agent.run()

    print("\n=== Generated Plan with Explicit Conflict Flags ===")
    print(json.dumps(plan, indent=2))

    print("\n=== Flagged Conflicts Summary ===")
    print(json.dumps(agent.conflicts_flagged, indent=2))

    print("\n=== Full Execution Audit Log ===")
    for entry in agent.log:
        print(json.dumps(entry, indent=2))

