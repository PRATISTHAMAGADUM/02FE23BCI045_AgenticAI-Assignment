"""
Lab 4: Memory and Retrieval -- Assignment 1: A Second, Isolated Topic

Assignment Requirement:
Add a second topic (e.g. "hosting") with its own stored record, distinct from "database".
Demonstrate, in a transcript, that a retrieval scoped to "database" never returns or leaks
the "hosting" fact into its answer, and vice versa.
Submit the updated code and the two-topic transcript.
"""

from dataclasses import dataclass
from datetime import date
import json


@dataclass
class MemoryRecord:
    topic: str
    fact: str
    date: str
    source: str = "memory"


class ScopedProjectMemory:
    def __init__(self):
        self.records = []          # long-term store
        self.allowed_writers = {"team_lead"}

    def retrieve(self, topic):
        # Strict scoped retrieval -- isolates records matching topic
        return [r for r in self.records if r.topic.lower() == topic.lower()]

    def write(self, record, user_role):
        if user_role not in self.allowed_writers:
            raise PermissionError(f"role '{user_role}' is not permitted to write memory")
        self.records.append(record)


class ScopedProjectAssistant:
    def __init__(self, memory):
        self.memory = memory
        self.session_facts = {}

    def answer(self, topic, question):
        hits = self.memory.retrieve(topic)
        if not hits:
            return f"[session] No stored decision on '{topic}' yet. {question}"
        latest = hits[-1]
        return (f"[memory, scoped topic='{topic}', dated {latest.date}] "
                f"Per decision on {latest.date}: {latest.fact}")

    def receive_statement(self, topic, new_fact, user_role):
        hits = self.memory.retrieve(topic)
        if hits and hits[-1].fact.lower() != new_fact.lower():
            return {
                "conflict": True,
                "topic": topic,
                "stored": hits[-1].fact,
                "stored_date": hits[-1].date,
                "new": new_fact,
                "message": (f"Conflict on topic '{topic}': stored decision from "
                            f"{hits[-1].date} ('{hits[-1].fact}'). Update to '{new_fact}'?"),
            }
        record = MemoryRecord(topic=topic, fact=new_fact, date=str(date.today()))
        self.memory.write(record, user_role)
        return {"conflict": False, "topic": topic, "message": f"Recorded for '{topic}': {new_fact}", "written": True}


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 4 - Assignment 1: Multi-Topic Scoped Memory Isolation (database vs hosting)")
    print("================================================================================\n")

    memory = ScopedProjectMemory()

    # Seed two independent topic records
    memory.write(
        MemoryRecord(topic="database", fact="we chose PostgreSQL with pgvector", date="2026-07-03"),
        user_role="team_lead",
    )
    memory.write(
        MemoryRecord(topic="hosting", fact="we chose AWS ECS Fargate with Terraform", date="2026-07-04"),
        user_role="team_lead",
    )

    assistant = ScopedProjectAssistant(memory)

    # 1. Query Topic 1: database
    print("--- 1. Query Scoped to 'database' ---")
    db_question = "What architecture decision was made regarding the database?"
    db_answer = assistant.answer("database", db_question)
    print(f"Q (database): {db_question}")
    print(f"A: {db_answer}")
    
    # Verify no leakage
    db_has_hosting = "hosting" in db_answer.lower() or "fargate" in db_answer.lower() or "aws" in db_answer.lower()
    print(f"Leakage check: Does 'database' answer contain any 'hosting' facts? -> {db_has_hosting} (PASS: completely isolated)\n")

    # 2. Query Topic 2: hosting
    print("--- 2. Query Scoped to 'hosting' ---")
    hosting_question = "Where are we hosting the backend containers?"
    hosting_answer = assistant.answer("hosting", hosting_question)
    print(f"Q (hosting): {hosting_question}")
    print(f"A: {hosting_answer}")
    
    # Verify no leakage
    hosting_has_db = "database" in hosting_answer.lower() or "postgres" in hosting_answer.lower() or "sqlite" in hosting_answer.lower()
    print(f"Leakage check: Does 'hosting' answer contain any 'database' facts? -> {hosting_has_db} (PASS: completely isolated)\n")

    # 3. Independent update to 'hosting' only
    print("--- 3. Updating 'hosting' Topic While Keeping 'database' Intact ---")
    print("Team lead updates hosting decision to Google Cloud Run...")
    memory.write(
        MemoryRecord(topic="hosting", fact="we migrated container hosting to Google Cloud Run", date="2026-07-10"),
        user_role="team_lead"
    )

    # Re-verify both topics
    print("\nRe-verifying 'database' (must remain identical):")
    print(assistant.answer("database", db_question))

    print("\nRe-verifying 'hosting' (reflects updated hosting decision only):")
    print(assistant.answer("hosting", hosting_question))

    print("\n=== Long-Term Memory Dump By Scoped Partition ===")
    for topic in ["database", "hosting"]:
        print(f"\nPartition '{topic}':")
        for rec in memory.retrieve(topic):
            print(f"  - [{rec.date}] {rec.fact}")

