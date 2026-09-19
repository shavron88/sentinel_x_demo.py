#!/usr/bin/env bash
# Run SentinelX with the real Python install (bypasses MS Store python.exe alias)
exec "/c/Users/haroon traders/AppData/Local/Programs/Python/Python313/python.exe" "$(dirname "$0")/app.py" "$@"
