"""Smoke test script for CloudSync support app backend.

Runs a few example queries through `SupportAgent` to validate backend behaviour.
"""
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

# Ensure repo root is on path
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

load_dotenv(dotenv_path=ROOT / ".env")

from src.agent import SupportAgent

API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not API_KEY:
    print("ANTHROPIC_API_KEY not set in environment or .env. Aborting smoke test.")
    raise SystemExit(1)

agent = SupportAgent(api_key=API_KEY)

examples = [
    "I've been trying to reset my password for hours and NOTHING works!! The reset email never arrives and I'm completely locked out of my account. This is ridiculous!",
    "Can you explain the OAuth 2.0 authentication flow and what causes 401 vs 403 errors in the API?",
]

for q in examples:
    print("\n-----\nQuery:\n", q)
    try:
        r = agent.chat(q)
        print("Response:\n", r.get("response", "<no response>"))
        print("Persona:", r.get("persona_label"), "(", r.get("persona_confidence"), ")")
    except Exception as e:
        print("Error during chat:", e)

print("\nSmoke test completed.")
