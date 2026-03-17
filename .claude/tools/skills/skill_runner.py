import argparse
import json
from .ollama_briefing import ollama_briefing

SKILLS = {
    'ollama_briefing': ollama_briefing,
}

def main():
    parser = argparse.ArgumentParser(description='Run a skill')
    parser.add_argument('--skill', required=True, help='Name of the skill to run')
    parser.add_argument('--request_json_file', required=True, help='Path to JSON request file')
    args = parser.parse_args()

    try:
        with open(args.request_json_file, 'r') as f:
            request_data = json.load(f)
    except FileNotFoundError:
        print(f"Error: Request JSON file '{args.request_json_file}' not found.")
        return 1
    except json.JSONDecodeError:
        print(f"Error: Could not parse JSON from file '{args.request_json_file}'.")
        return 1

    try:
        skill = SKILLS[args.skill]
    except KeyError:
        print(f"Error: Skill '{args.skill}' not found.")
        return 1

    try:
        result = skill.run(request_data)
        print(json.dumps(result, indent=2))
    except Exception as e:
        print(f"Error running skill '{args.skill}': {str(e)}")
        return 1

if __name__ == '__main__':
    main()
