# Curated Report Redaction Rules

**Purpose:** Ensure all curated markdown content in `.report/` is share-safe by detecting and blocking absolute host paths and secret-like strings.

**Scope:** All markdown files (*.md) in `.report/**/*.md` directory tree.

**Rationale:**
- Curated reports may be shared with external stakeholders, teams, or documentation systems
- Absolute file paths reveal system architecture, directory structure, and potential security information
- Secret-like strings (API keys, tokens, credentials) must never leak into shared content
- Host identification (Windows drive letters, /home/, /Users/) may expose target environment details

---

## Block Patterns

### 1. Windows Drive Paths
**Pattern:** `^[A-Z]:\\`
**Description:** Detects Windows absolute paths starting with drive letters (e.g., `D:\ClaudeClockwork\`)
**Example violations:**
- `D:\ClaudeClockwork\.claude\config\`
- `C:\Users\username\project\`
- `E:\data\reports\`

**Reasoning:** Drive-letter paths reveal Windows machine configuration and directory structure.

---

### 2. Unix Home Paths
**Pattern:** `/Users/` or `/home/`
**Description:** Detects Unix/macOS home directory paths that may leak usernames
**Example violations:**
- `/Users/alice/projects/clockwork/`
- `/home/bob/.config/`
- `/Users/developer/workspace/`

**Reasoning:** Home paths leak actual usernames and home directory structure.

---

### 3. Generic Absolute Paths
**Pattern:** `^/[a-z_][a-z0-9_.-]*(/[a-z0-9_.-]+)+`
**Description:** Detects absolute paths with known system/project directories
**Known prefixes:**
- `/opt/` — often system installations
- `/srv/` — service data
- `/var/` — variable data
- `/mnt/` — mount points (especially WSL: `/mnt/d/`, `/mnt/c/`)
- `/data/` — data directories
- `/workspace/` — workspace directories
- `/work/` — work directories
- `/project/` — project directories
- `/app/` — application directories

**Example violations:**
- `/mnt/d/ClaudeClockwork/`
- `/opt/claude/`
- `/var/lib/reports/`
- `/workspace/clockwork/data/`

**Reasoning:** Absolute paths reveal infrastructure layout and deployment targets.

---

### 4. Secret Patterns (Optional Tier)
**Patterns:**
- `api[_-]?key\s*[:=]` — API key assignments
- `secret\s*[:=]` — Generic secret assignments
- `token\s*[:=]` — Authentication tokens
- `password\s*[:=]` — Password fields
- `credentials?\s*[:=]` — Credential assignments
- `bearer\s+[A-Za-z0-9._\-]+` — Bearer tokens

**Example violations:**
- `api_key=sk_live_123456789`
- `secret: abc123def456`
- `token="eyJhbGciOiJIUzI1NiIs..."`
- `password=MyP@ssw0rd`

**Reasoning:** Secret-like strings may leak authentication material or credentials that can compromise security.

---

## Testing Approach

### Synthetic Test Cases

**Path leak tests:**
1. Windows drive path in markdown line
2. Unix home path (/Users/) in markdown line
3. WSL mount path (/mnt/d/) in markdown line
4. /opt/ system path in markdown line
5. Multiple paths in same file
6. Paths in code blocks (still flagged)

**Secret leak tests:**
1. API key assignment in plain text
2. Bearer token with valid-looking value
3. Secret keyword with value
4. Multiple secrets in same file
5. Secrets in markdown code blocks

**Clean content tests:**
1. Relative paths (./reports/, ./data/)
2. Placeholder paths (<PROJECT_ROOT>, {WORKSPACE})
3. Generic domain names (example.com)
4. URLs (https://example.com/path)
5. Non-secret keywords (secret_key as variable name without assignment)

---

## Redaction Standards

### Line-by-line Reporting
The gate scans `.report/**/*.md` files line-by-line and reports:
- File path (relative to .report/)
- Line number (1-indexed, best effort)
- Matched pattern name (e.g., "windows_drive_path", "unix_home_path")
- Matched text snippet (first 80 chars)

### Failure Mode
If any violations found:
- Exit code: 1
- Output: CSV/table format with file, line, pattern, snippet
- Summary: "X violations detected in Y files"

### Success Mode
If no violations found:
- Exit code: 0
- Output: "PASS: .report/ is redaction-safe (0 violations)"

---

## Implementation Details

### File: `claudeclockwork/core/gates/report_redaction_gate.py`

**Public API:**
```python
def run_report_redaction_gate(project_root: Path | str | None = None) -> dict:
    """
    Scan .report/**/*.md for path leaks and secrets.

    Returns dict with keys:
    - pass: bool
    - violations: list of dicts with:
        - file: str (relative path)
        - line_number: int
        - pattern: str (pattern name)
        - matched_text: str
        - context: str (surrounding text, up to 80 chars)
    - total_violations: int
    - scanned_files: int
    """
```

### Pattern Registration
Patterns are stored as tuples: `(name, regex, severity)`
- `severity` in ("high", "medium") determines whether violations fail the gate
- "high" severity patterns always cause failure
- "medium" severity patterns log but may be configurable

---

## Related Documentation

- `.claude/governance/file_lifecycle.md` — file ownership and lifecycle
- `.project/MEMORY.md` — cross-session governance context
- `CLAUDE.md` section "Key Governance Rules" — deployment boundary guidance
