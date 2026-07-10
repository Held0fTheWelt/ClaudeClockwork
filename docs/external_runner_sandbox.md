# External Runner Sandbox (Phase 34)

- **Structured argv only:** no shell strings; list of arguments.
- **Allowlisted binaries:** e.g. python, python3, node, ollama, pip.
- **Working directory:** must be set to runtime root (or under it).
- **Timeout and memory:** timeout enforced; memory best-effort per platform.
- Non-allowlisted binary or shell usage is blocked with `policy_denied`.
