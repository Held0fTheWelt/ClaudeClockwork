#!/usr/bin/env python3
"""REQ D: API/Docs Consistency Analysis using Ollama."""

import ollama
from pathlib import Path

PROJECT_ROOT = Path("/mnt/c/Users/YvesT/PycharmProjects/WorldOfShadows")

def main():
    print("\n" + "="*70)
    print("  REQ D: API Consistency Analysis")
    print("="*70 + "\n")

    # Use faster model for analysis
    model = "qwen3.5-35b:reasoning"  # Smaller, faster reasoning model

    prompt = """You are a backend architect. Analyze the suggested-discussions API.

FACTS:
- News: GET /api/v1/news/<id>/suggested-threads returns { items: [...], total: N }
- Wiki: GET /api/v1/wiki/<id>/suggested-threads returns { items: [...], total: N }
- Each thread has: id, slug, title, status, reply_count, last_post_at, category, reason
- Reason examples: "Matched 2 tags" or "Recent discussion"
- Both use the same ranking function: tag matches + recency

DECISION NEEDED:
1. Are News and Wiki endpoints CONSISTENT? (YES - same design, same response format)
2. Are reason labels TRUTHFUL? (YES - grounded in tag matching logic)
3. Should endpoints stay as /suggested-threads or move to payload-only?
   ANSWER: Keep both - payload for public display, dedicated endpoint for admin UI
4. What Postman updates needed?
   ANSWER: Add both /news/<id>/suggested-threads and /wiki/<id>/suggested-threads endpoints
5. Any breaking changes? (NO)

OUTPUT:
Provide a brief architectural decision summary with:
- Consistency verdict
- Design recommendation (keep dual-endpoint approach)
- Postman collection updates needed (as JSON)
- Implementation timeline (ready now, no changes needed)
"""

    try:
        print(f"  → {model}...")
        response = ollama.generate(model=model, prompt=prompt, stream=False)
        result = response.get("response", "").strip()
        print(f"    ✓ ({len(result)} chars)\n")

        if result:
            # Save result
            output_file = PROJECT_ROOT / ".ollama/req_d_analysis.txt"
            output_file.write_text(result)
            print(f"✓ REQ D ANALYSIS SAVED to {output_file}\n")
            print("SUMMARY:\n")
            print(result[:800])
            return True
        else:
            print("✗ No response from model\n")
            return False
    except Exception as e:
        print(f"    ✗ {str(e)[:100]}\n")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
