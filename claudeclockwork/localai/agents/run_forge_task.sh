#!/bin/bash
#
# Generic Forge Pipeline Task Executor
#
# Reusable script for ANY Ollama agent to execute ANY task through the forge pipeline.
# Works with all archetypes (scanner, validator, reporter, transformer, registry_helper).
# No task-specific customization needed.
#
# Usage:
#   ./run_forge_task.sh <archetype> <purpose> <allowed_write_roots> <output_file>
#
# Examples:
#   ./run_forge_task.sh reporter "Generate FORGE_PIPELINE.md documentation" "claudeclockwork/docs" "FORGE_PIPELINE.md"
#   ./run_forge_task.sh transformer "Update CHANGELOG.md with feature summary" "." "CHANGELOG.md"
#   ./run_forge_task.sh validator "Create JSON validator skill" "" "validator_skill.py"
#
# Arguments:
#   $1 = archetype (scanner|validator|reporter|transformer|registry_helper)
#   $2 = purpose/task description
#   $3 = allowed_write_roots (comma-separated paths, or empty for read-only)
#   $4 = output_file (where to write result, relative to current dir)

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Validate arguments
if [[ $# -lt 2 ]]; then
    echo -e "${RED}Error: Insufficient arguments${NC}"
    echo "Usage: $0 <archetype> <purpose> [allowed_write_roots] [output_file]"
    echo ""
    echo "Archetypes: scanner, validator, reporter, transformer, registry_helper"
    exit 1
fi

ARCHETYPE="$1"
PURPOSE="$2"
ALLOWED_ROOTS="${3:-.}"
OUTPUT_FILE="${4:-result.json}"

# Validate archetype
case "$ARCHETYPE" in
    scanner|validator|reporter|transformer|registry_helper)
        ;;
    *)
        echo -e "${RED}Error: Invalid archetype '$ARCHETYPE'${NC}"
        echo "Valid archetypes: scanner, validator, reporter, transformer, registry_helper"
        exit 1
        ;;
esac

# Find the ClaudeClockwork worktree directory
# Try multiple common locations
WORKDIR=""
for candidate in \
    ".worktrees/skill-forge-pipeline" \
    "." \
    "/mnt/d/ClaudeClockwork/.worktrees/skill-forge-pipeline" \
    "/mnt/d/ClaudeClockwork"; do

    if [[ -f "$candidate/claudeclockwork/localai/agents/generic_forge_agent.py" ]]; then
        WORKDIR="$candidate"
        break
    fi
done

if [[ -z "$WORKDIR" ]]; then
    echo -e "${RED}Error: Could not find skill-forge-pipeline directory${NC}"
    echo "Please run this script from ClaudeClockwork or a subdirectory"
    exit 1
fi

cd "$WORKDIR"

echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo -e "${BLUE}Generic Forge Pipeline Task Executor${NC}"
echo -e "${BLUE}═══════════════════════════════════════${NC}"
echo ""
echo -e "${YELLOW}Task Details:${NC}"
echo "  Archetype: $ARCHETYPE"
echo "  Purpose: $PURPOSE"
echo "  Write roots: $ALLOWED_ROOTS"
echo "  Output file: $OUTPUT_FILE"
echo ""

# Convert allowed_roots to JSON array
if [[ -z "$ALLOWED_ROOTS" ]]; then
    ROOTS_JSON="[]"
else
    # Split by comma and convert to JSON array
    ROOTS_JSON="["
    first=true
    for root in $(echo "$ALLOWED_ROOTS" | tr ',' '\n'); do
        if [[ "$first" == false ]]; then
            ROOTS_JSON="$ROOTS_JSON,"
        fi
        ROOTS_JSON="$ROOTS_JSON\"$(echo "$root" | xargs)\""
        first=false
    done
    ROOTS_JSON="$ROOTS_JSON]"
fi

# Build forge request JSON
FORGE_REQUEST=$(cat <<EOF
{
  "task_id": "forge_$(date +%Y%m%d_%H%M%S_%s)",
  "archetype": "$ARCHETYPE",
  "purpose": "$PURPOSE",
  "constraints": {
    "allowed_write_roots": $ROOTS_JSON,
    "forbidden_patterns": ["shell=True", "eval", "exec"],
    "example_input": {},
    "example_output": {}
  },
  "input_schema": {"type": "object"},
  "output_schema": {"type": "object"}
}
EOF
)

echo -e "${YELLOW}Executing forge pipeline...${NC}"
echo ""

# Execute the generic forge agent
TEMP_OUTPUT=$(mktemp)
TEMP_STDERR=$(mktemp)
trap "rm -f $TEMP_OUTPUT $TEMP_STDERR" EXIT

if python -m claudeclockwork.localai.agents.generic_forge_agent "$FORGE_REQUEST" > "$TEMP_OUTPUT" 2>"$TEMP_STDERR"; then
    echo -e "${GREEN}✓ Pipeline executed successfully${NC}"
    echo ""

    # Parse and display results (extract JSON from output, skipping warnings)
    RESULT_JSON=$(cat "$TEMP_OUTPUT" | python3 -c "import sys; lines = sys.stdin.read(); json_start = lines.find('{'); print(lines[json_start:] if json_start >= 0 else '')" 2>/dev/null)
    SUCCESS=$(echo "$RESULT_JSON" | python3 -c "import sys, json; print(str(json.load(sys.stdin).get('success', False)).lower())" 2>/dev/null || echo "false")

    if [[ "$SUCCESS" == "true" ]]; then
        echo -e "${GREEN}✓ Task completed successfully${NC}"
        echo ""

        # Write results to output file
        echo "$RESULT_JSON" | python3 -m json.tool > "$OUTPUT_FILE"
        echo -e "${GREEN}✓ Results written to: $OUTPUT_FILE${NC}"
        echo ""

        # Extract and display generated artifacts if present
        ARTIFACTS=$(echo "$RESULT_JSON" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    result = data.get('result', {})
    if 'forge_result' in result:
        forge = result['forge_result']
        if 'code' in forge:
            print('Generated artifacts:')
            for fname in forge['code'].keys():
                print(f'  - {fname}')
except:
    pass
" 2>/dev/null)

        if [[ -n "$ARTIFACTS" ]]; then
            echo "$ARTIFACTS"
        fi

        exit 0
    else
        echo -e "${RED}✗ Task failed${NC}"
        echo ""
        echo "Error details:"
        echo "$RESULT_JSON" | python3 -m json.tool 2>/dev/null || echo "$RESULT_JSON"
        exit 1
    fi
else
    echo -e "${RED}✗ Pipeline execution failed${NC}"
    cat "$TEMP_OUTPUT"
    exit 1
fi
