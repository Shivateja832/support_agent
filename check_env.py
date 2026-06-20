#!/usr/bin/env python3
"""Simple environment checker for required Python packages."""
import importlib
from pathlib import Path

REQUIRED = [
    "streamlit",
    "anthropic",
    "chromadb",
    "pypdf",
    "reportlab",
]


def check():
    missing = []
    for pkg in REQUIRED:
        try:
            importlib.import_module(pkg)
            print(f"OK: {pkg}")
        except Exception as e:
            print(f"MISSING: {pkg} — {e}")
            missing.append(pkg)

    if missing:
        print("\nSome packages are missing. Install with:\n    pip install -r requirements.txt")
        return 1
    print("\nAll required packages appear installed.")
    return 0


if __name__ == '__main__':
    raise SystemExit(check())
