import sys
import json
import os
from pathlib import Path

# Add parent directory to path for relative imports
sys.path.insert(0, str(Path(__file__).parent))

from ollama_briefing import run as briefing_run


SKILLS = {
    'ollama_briefing': briefing_run
}


def main():
    if len(sys.argv) < 3:
        print(json.dumps({"error": "Usage: skill_runner.py <skill_name> <request_json_file>"}))
        sys.exit(1)

    skill_name = sys.argv[1]
    request_file = sys.argv[2]

    try:
        with open(request_file, 'r') as f:
            request = json.load(f)

        if skill_name not in SKILLS:
            print(json.dumps({"error": f"Skill not found: {skill_name}"}))
            sys.exit(1)

        result = SKILLS[skill_name](request)
        print(json.dumps(result))

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)


if __name__ == '__main__':
    main()
