"""
Lab 5: MCP-Style Connector -- Assignment 2: Scope read_file to a Safe Directory

Assignment Requirement:
Add a second permission boundary: `read_file` may only read paths inside a declared
safe directory (e.g. paths starting with `/safe/`). Write an adversarial test that
attempts to read a path outside that directory and confirm the server rejects it with
a structured error rather than reading it. Submit the updated code and the adversarial
test's result.
"""

import posixpath
import json

SAFE_DIRECTORY = "/safe/"

# Server file store with files inside and outside the boundary
MOCK_FILES = {
    "/safe/app_config.json": '{"env": "sandbox", "debug": false, "name": "agent_service"}',
    "/safe/readme.txt": "Safe documentation inside /safe/ directory.",
    "/etc/shadow": "root:$6$salthex$adversarial_shadow_hash:19000:0:99999:7:::",
    "/var/secrets/api_keys.env": "AWS_SECRET_KEY=AKIA_TOP_SECRET_PRODUCTION_KEY",
}


class GuardedMCPServer:
    def __init__(self, safe_prefix=SAFE_DIRECTORY):
        self.safe_prefix = safe_prefix

    def list_capabilities(self):
        return [
            {"name": "read_file", "kind": "resource",
             "input": {"path": "str"}, "output": {"content": "str"},
             "security_boundary": f"Path must start with {self.safe_prefix}"}
        ]

    def read_file(self, path):
        # Normalize path to defeat directory traversal attacks like /safe/../etc/shadow
        norm_path = posixpath.normpath(path)

        # Enforce safe directory permission boundary
        if not norm_path.startswith(self.safe_prefix):
            return {
                "error": "AccessDeniedError: path violates security boundary",
                "status": "FORBIDDEN",
                "attempted_path": path,
                "normalized_path": norm_path,
                "safe_boundary": self.safe_prefix,
                "message": f"Access to '{path}' blocked. Resource reads are strictly confined to '{self.safe_prefix}'."
            }

        # Check file existence within safe directory
        if norm_path not in MOCK_FILES:
            return {"error": f"FileNotFoundError: '{norm_path}' not found in safe store"}

        return {
            "status": "SUCCESS",
            "path": norm_path,
            "content": MOCK_FILES[norm_path]
        }


class MCPClient:
    def __init__(self, server, caller_name="planning_agent"):
        self.server = server
        self.caller_name = caller_name

    def call(self, capability_name, **kwargs):
        method = getattr(self.server, capability_name)
        return method(**kwargs)


if __name__ == "__main__":
    print("================================================================================")
    print("Lab 5 - Assignment 2: Safe Directory Boundary Enforcement for read_file")
    print("================================================================================\n")

    server = GuardedMCPServer()
    client = MCPClient(server)

    # 1. Legitimate Access Test
    print("--- 1. Legitimate Request (Path inside /safe/) ---")
    legit_path = "/safe/app_config.json"
    print(f"Client requesting: '{legit_path}'")
    legit_res = client.call("read_file", path=legit_path)
    print(f"Server response:\n{json.dumps(legit_res, indent=2)}\n")

    # 2. Adversarial Test 1: Direct out-of-boundary access to /etc/shadow
    print("--- 2. Adversarial Test 1: Direct Out-of-Boundary Path (/etc/shadow) ---")
    adv_path_1 = "/etc/shadow"
    print(f"Adversarial client requesting: '{adv_path_1}'")
    res_adv_1 = client.call("read_file", path=adv_path_1)
    print(f"Server structured rejection:\n{json.dumps(res_adv_1, indent=2)}\n")

    # 3. Adversarial Test 2: Accessing secrets outside safe boundary
    print("--- 3. Adversarial Test 2: Sensitive Secrets Path (/var/secrets/api_keys.env) ---")
    adv_path_2 = "/var/secrets/api_keys.env"
    print(f"Adversarial client requesting: '{adv_path_2}'")
    res_adv_2 = client.call("read_file", path=adv_path_2)
    print(f"Server structured rejection:\n{json.dumps(res_adv_2, indent=2)}\n")

    # 4. Adversarial Test 3: Path traversal attempt (/safe/../etc/shadow)
    print("--- 4. Adversarial Test 3: Path Traversal Attack (/safe/../etc/shadow) ---")
    adv_path_3 = "/safe/../etc/shadow"
    print(f"Adversarial client requesting: '{adv_path_3}'")
    res_adv_3 = client.call("read_file", path=adv_path_3)
    print(f"Server structured rejection:\n{json.dumps(res_adv_3, indent=2)}\n")

    # Verification assertions
    print("=== Adversarial Test Suite Verification ===")
    assert res_adv_1["status"] == "FORBIDDEN"
    assert res_adv_2["status"] == "FORBIDDEN"
    assert res_adv_3["status"] == "FORBIDDEN"
    assert legit_res["status"] == "SUCCESS"
    print("ALL ADVERSARIAL TESTS REJECTED: Structured error returned for every out-of-boundary access attempt.")

