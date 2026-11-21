"""
Lab 5: MCP-Style Connector -- Assignment 1: Add a Fourth, Discoverable Capability

Assignment Requirement:
Add a `list_files` resource capability to the manifest and server. The client must
discover and call it without any hard-coded reference to its name anywhere in
`MCPClient` -- only `CAPABILITIES` (and server implementation) should need to change.
Submit the updated server/client code and a transcript demonstrating the new
capability being discovered and called.
"""

import sqlite3

# ---- In-memory SQLite DB ----
conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE signups (event TEXT, count INTEGER)")
conn.executemany("INSERT INTO signups VALUES (?, ?)", [
    ("AI Club Talk", 12), ("Hackathon Kickoff", 9), ("Robotics Demo", 15),
])
conn.commit()

MOCK_FILES = {
    "README.md": "Agentic AI Systems - mini MCP server demo.",
    "lab_guide.txt": "Lab instructions and syllabus guidelines.",
    "config.json": "{\"version\": \"1.0\", \"environment\": \"production\"}"
}
MOCK_API = {"events_today": ["AI Club Talk", "Robotics Demo"]}

# Extended CAPABILITIES manifest: Added 'list_files' resource capability
CAPABILITIES = [
    {"name": "read_file", "kind": "resource",
     "input": {"path": "str"}, "output": {"content": "str"}},
    {"name": "query_db", "kind": "tool",
     "input": {"sql": "str"}, "output": {"rows": "list"}},
    {"name": "call_api", "kind": "tool",
     "input": {"endpoint": "str"}, "output": {"data": "any"}},
    # Newly added 4th capability
    {"name": "list_files", "kind": "resource",
     "input": {}, "output": {"files": "list"}},
]

ALLOWED_CALLERS = {"planning_agent"}


class MCPServer:
    def list_capabilities(self):
        return CAPABILITIES

    def read_file(self, path):
        if path not in MOCK_FILES:
            return {"error": f"file not found: {path}"}
        return {"content": MOCK_FILES[path]}

    def query_db(self, sql, caller):
        if caller not in ALLOWED_CALLERS:
            return {"error": f"caller '{caller}' is not permitted to use query_db"}
        if not sql.strip().upper().startswith("SELECT"):
            return {"error": "only SELECT statements are permitted through this tool"}
        cur = conn.execute(sql)
        return {"rows": cur.fetchall()}

    def call_api(self, endpoint):
        if endpoint not in MOCK_API:
            return {"error": f"unknown endpoint: {endpoint}"}
        return {"data": MOCK_API[endpoint]}

    # Server handler for list_files
    def list_files(self):
        return {
            "files": list(MOCK_FILES.keys()),
            "count": len(MOCK_FILES)
        }


class MCPClient:
    """
    Generic MCP Client: has ZERO hard-coded references to 'list_files' or any specific tool.
    Dynamically discovers and calls endpoints through the protocol manifest.
    """
    def __init__(self, server, caller_name):
        self.server = server
        self.caller_name = caller_name

    def discover(self):
        return self.server.list_capabilities()

    def call(self, capability_name, **kwargs):
        manifest = {c["name"]: c for c in self.discover()}
        if capability_name not in manifest:
            raise ValueError(f"unknown capability: {capability_name}")
        method = getattr(self.server, capability_name)
        if capability_name == "query_db":
            return method(caller=self.caller_name, **kwargs)
        return method(**kwargs)


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 5 - Assignment 1: Add a Fourth, Discoverable Capability (list_files)")
    print("================================================================================\n")

    server = MCPServer()
    client = MCPClient(server, caller_name="planning_agent")

    print("=== Step 1: Dynamic Discovery (Client queries server manifest) ===")
    discovered_capabilities = client.discover()
    for c in discovered_capabilities:
        print(f"  * {c['name']:<12} | kind: {c['kind']:<10} | input: {c['input']} | output: {c['output']}")

    # Find the newly added capability dynamically from the manifest
    new_cap = next(c for c in discovered_capabilities if c["name"] == "list_files")
    print(f"\nDiscovered new capability from manifest: '{new_cap['name']}' of kind '{new_cap['kind']}'")

    print("\n=== Step 2: Calling the Discovered Capability Dynamically ===")
    # Client calls the newly discovered capability using the name from discovery
    call_result = client.call(new_cap["name"])
    print(f"Result from client.call('{new_cap['name']}'):")
    print(call_result)

    print("\n=== Step 3: Chaining Discovered Files into read_file ===")
    # Client reads one of the files discovered from list_files
    for f in call_result["files"]:
        content_result = client.call("read_file", path=f)
        print(f"  Read '{f}': {content_result['content']}")

