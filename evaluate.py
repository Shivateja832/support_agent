"""Evaluate persona detection accuracy on labeled test cases.
Run: python evaluate.py
"""
import json
from pathlib import Path
from src.agent import PersonaDetector

DATA = Path(__file__).parent / "data" / "test_cases.jsonl"


def load_cases(path: Path):
    cases = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            cases.append(json.loads(line))
    return cases


def main():
    cases = load_cases(DATA)
    # Use PersonaDetector without an LLM client to rely on rule-based detection for deterministic testing
    detector = PersonaDetector(client=None)

    correct = 0
    total = len(cases)
    details = []

    for c in cases:
        pid = c.get("id")
        query = c.get("query")
        expected = c.get("expected_persona")
        persona, conf, reason = detector.detect(query, history=None)
        ok = persona == expected
        if ok:
            correct += 1
        details.append({"id": pid, "query": query, "expected": expected, "predicted": persona, "confidence": conf, "correct": ok, "reason": reason})

    accuracy = correct / total * 100
    result = {"total": total, "correct": correct, "accuracy_pct": round(accuracy, 2), "details": details}

    print(json.dumps(result, indent=2))

    # Save results
    out = Path(__file__).parent / "data" / "persona_eval_results.json"
    out.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(f"Results saved to {out}")


if __name__ == '__main__':
    main()
