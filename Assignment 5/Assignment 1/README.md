# Lab 5 - Assignment 1: Add a Fourth, Discoverable Capability

## Objective
Add a fourth capability, `list_files` (of kind `"resource"`), to the server manifest. The `MCPClient` must discover and invoke this capability dynamically through reflection and manifest discovery without having any hard-coded references to the string `"list_files"` inside `MCPClient`.

## Key Implementation Details
1. **Manifest Extension (`CAPABILITIES`)**:
   ```python
   {"name": "list_files", "kind": "resource", "input": {}, "output": {"files": "list"}}
   ```
2. **Server Handler (`MCPServer.list_files`)**: Returns all available resource filenames and total count from `MOCK_FILES`.
3. **Decoupled Client (`MCPClient`)**:
   - `MCPClient` uses purely dynamic dispatch:
     ```python
     method = getattr(self.server, capability_name)
     ```
   - No string literal or special case for `list_files` exists inside the client class.
4. **Execution Flow**:
   - Client calls `discover()` to inspect available capabilities.
   - Discovers `list_files` and invokes it to enumerate all available server files.
   - Iterates through the discovered files and reads each using `read_file`.

## How to Run
```bash
python solution.py
```
Outputs and discovery transcripts are captured in `output.txt`.

