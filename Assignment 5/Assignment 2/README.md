# Lab 5 - Assignment 2: Scope read_file to a Safe Directory

## Objective
Establish a second security permission boundary on `MCPServer.read_file` restricting resource reads exclusively to paths within a designated safe directory (`/safe/`). Implement an adversarial test suite attempting to read unauthorized system paths and path-traversal payloads, verifying that the server rejects every out-of-boundary attempt with structured JSON errors rather than exposing file content.

## Key Implementation Details
1. **Path Normalization & Confinement**:
   ```python
   norm_path = posixpath.normpath(path)
   if not norm_path.startswith(self.safe_prefix):
       return {
           "error": "AccessDeniedError: path violates security boundary",
           "status": "FORBIDDEN",
           "attempted_path": path,
           "normalized_path": norm_path,
           "safe_boundary": self.safe_prefix,
           "message": f"Access to '{path}' blocked..."
       }
   ```
2. **Adversarial Test Cases**:
   - **Case 1 (Direct System Path)**: `/etc/shadow` -> Blocked (`FORBIDDEN`).
   - **Case 2 (Confidential Secrets Path)**: `/var/secrets/api_keys.env` -> Blocked (`FORBIDDEN`).
   - **Case 3 (Directory Traversal Attack)**: `/safe/../etc/shadow` -> Normalized to `/etc/shadow` and blocked (`FORBIDDEN`).
3. **Legitimate Case**:
   - `/safe/app_config.json` -> Permitted and returned (`status: "SUCCESS"`).

## How to Run
```bash
python solution.py
```
Outputs and structured rejection responses are recorded in `output.txt`.

