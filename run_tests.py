"""
Simple test runner to execute pytest programmatically.
Run locally before pushing: `python -m venv .venv && .venv\Scripts\pip install -r requirements.txt && python run_tests.py`
"""
import sys
import subprocess

def main():
    cmd = [sys.executable, '-m', 'pytest', '-q', 'tests']
    return subprocess.call(cmd)

if __name__ == '__main__':
    raise SystemExit(main())
