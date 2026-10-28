#!/usr/bin/env python3
"""PreToolUse hook: block any tool call that touches secret files.

Exit code 2 blocks the call and returns stderr to Claude.
"""
import json
import re
import sys

SECRET = re.compile(
    r"(^|[\s/\"'=])("
    r"\.env(\.(?!example\b)[\w.-]+)?"       # .env, .env.local (not .env.example)
    r"|[\w.-]+\.(pem|key|p12|pfx)"          # private keys / certificates
    r"|id_(rsa|ed25519|ecdsa)[\w.]*"        # SSH keys
    r"|\.netrc|\.git-credentials"
    r")(?=$|[\s\"'/;|&)])"
)
SECRET_DIR = re.compile(r"(^|[\s/\"'=~])(secrets?|\.ssh|\.aws|\.gnupg)/")

try:
    data = json.load(sys.stdin)
except Exception:
    sys.exit(0)

target = json.dumps(data.get("tool_input", {}), ensure_ascii=False)
target = target.replace("\\\"", " ")
if SECRET.search(target) or SECRET_DIR.search(target):
    print("Blocked: this call touches a secret file (.env / secrets/ / key).",
          file=sys.stderr)
    sys.exit(2)
sys.exit(0)
