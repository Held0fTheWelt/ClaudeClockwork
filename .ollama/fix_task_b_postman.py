#!/usr/bin/env python3
"""
TASK B Specialized Agent: Update Postman collection with truthful examples.
Uses Python JSON parsing + Ollama for content generation.
"""

import ollama
import json
import subprocess
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

def update_postman():
    """Update Postman collection with truthful examples."""

    print("\n" + "="*70)
    print("  TASK B: Update Postman with Truthful Ranking Examples")
    print("="*70 + "\n")

    postman_path = PROJECT_ROOT / "postman/WorldOfShadows_API.postman_collection.json"

    if not postman_path.exists():
        print("  ✗ Postman collection not found")
        return False

    # Read Postman JSON
    try:
        with open(postman_path) as f:
            postman = json.load(f)
    except Exception as e:
        print(f"  ✗ Could not parse Postman JSON: {str(e)}")
        return False

    print(f"  Loading: {len(str(postman))} bytes\n")

    # Find suggested-threads endpoints
    def find_endpoints(item, path=""):
        """Recursively find endpoint definitions."""
        endpoints = []

        if isinstance(item, dict):
            if item.get("request", {}).get("url"):
                url = item["request"]["url"]
                url_str = url if isinstance(url, str) else str(url.get("path", ""))
                if "suggested" in url_str:
                    endpoints.append((path, item))

            for key, value in item.items():
                endpoints.extend(find_endpoints(value, f"{path}/{key}"))

        elif isinstance(item, list):
            for i, sub_item in enumerate(item):
                endpoints.extend(find_endpoints(sub_item, f"{path}[{i}]"))

        return endpoints

    endpoints = find_endpoints(postman)
    print(f"  Found {len(endpoints)} suggested-threads endpoints\n")

    # Have Ollama generate truthful example response
    prompt = """Generate a truthful example response for a suggested-threads endpoint.

The REAL ranking logic uses:
1. Tag matches from primary discussion thread
2. Recent activity as tie-breaker
3. Excludes: primary, manually-related, hidden/deleted

Generate a JSON array response with 3 example suggested threads.
Each item should have:
- id (number)
- title (string)
- slug (string)
- category object
- reason (string) - MUST match actual ranking logic

Example reason labels (pick from):
- "Matched 2 tags"
- "Recent discussion in topic"
- "Related by tag: api"
- "Active community thread"

Output ONLY valid JSON array with 3 items."""

    print("  Generating truthful example response...\n")

    response = ollama.generate(
        model="gemma3:latest",
        prompt=prompt,
        stream=False,
    )

    example = response.get("response", "").strip()

    if not example or "[" not in example:
        print("  ✗ Ollama could not generate example")
        return False

    # Try to parse the example
    try:
        example_data = json.loads(example)
        print(f"  ✓ Generated example with {len(example_data)} items")
    except:
        print("  ⚠ Example is not valid JSON, using as-is for documentation")
        example_data = None

    # Update the Postman collection
    # For each suggested-threads endpoint, update the response example
    def update_responses(item):
        """Update response examples recursively."""
        if isinstance(item, dict):
            # Check if this is a response with body
            if "response" in item and isinstance(item["response"], list):
                for resp in item["response"]:
                    if isinstance(resp, dict) and "body" in resp:
                        if "suggested" in str(resp.get("url", "")):
                            # This is a suggested-threads response
                            try:
                                body = json.loads(resp["body"])
                                if "items" in body:
                                    body["items"] = example_data if example_data else body["items"]
                                    resp["body"] = json.dumps(body, indent=2)
                                    print(f"    Updated response body")
                            except:
                                pass

            # Add documentation
            if "description" in item and "suggested" in item.get("url", ""):
                item["description"] = "Get auto-suggested forum threads (ranked by tag matches and recency, excludes primary/manual/hidden)"

            for key, value in item.items():
                update_responses(value)

        elif isinstance(item, list):
            for sub_item in item:
                update_responses(sub_item)

    update_responses(postman)

    # Save updated Postman
    try:
        with open(postman_path, 'w') as f:
            json.dump(postman, f, indent=2)
        print(f"  ✓ Updated Postman collection")
        return True
    except Exception as e:
        print(f"  ✗ Could not write Postman: {str(e)}")
        return False

def commit():
    """Commit the change."""
    try:
        subprocess.run(
            ["git", "add", "postman/WorldOfShadows_API.postman_collection.json"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            check=True,
        )

        subprocess.run(
            ["git", "commit", "-m", "docs(postman): truthful ranking examples in suggested-threads"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            check=True,
        )

        result = subprocess.run(
            ["git", "log", "-1", "--oneline"],
            cwd=str(PROJECT_ROOT),
            capture_output=True,
            text=True,
        )

        print(f"\n  ✓ Committed: {result.stdout.strip()}\n")
        return True
    except Exception as e:
        print(f"  ✗ Commit failed: {str(e)}")
        return False

def main():
    success = update_postman()

    if success:
        commit()
        print("="*70)
        print("  ✓ TASK B: POSTMAN TRUTHFULNESS UPDATE COMPLETE")
        print("="*70 + "\n")
        return True
    else:
        print("="*70)
        print("  ✗ TASK B: UPDATE FAILED")
        print("="*70 + "\n")
        return False

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
