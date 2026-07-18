#!/usr/bin/env python3
"""Reference conformance runner: checks the corpus against an agentd binary.

Each fixture is a bare instruction document. The runner wraps it in a minimal
config, asks the binary to validate, and (when valid) reads the introspection
surface for what registered. Any runtime can conform by supplying its own
runner with the same observable checks; the corpus itself is neutral.
"""
import json, os, subprocess, sys, glob, re

AGENTD = os.environ.get("AGENTD_BIN", "agentd")
ROOT = os.path.dirname(os.path.abspath(__file__))

def load_expected(path):
    # Minimal reader, STRICT: a line this subset does not recognize is fatal.
    # A silently-ignored typo in an expectation file is a passing test that
    # asserts nothing — the exact failure mode a conformance corpus exists to
    # prevent (finding: instruction.md review §7.3).
    exp = {"errors": [], "registers": {}}
    for n, line in enumerate(open(path), 1):
        line = line.split("#")[0].rstrip()
        if not line.strip(): continue
        if line.strip() == "registers:": continue
        m = re.match(r"^valid:\s*(true|false)$", line)
        if m: exp["valid"] = m.group(1) == "true"; continue
        m = re.match(r"^errors:\s*\[(.*)\]$", line)
        if m: exp["errors"] = [s.strip().strip('"') for s in m.group(1).split(",") if s.strip()]; continue
        m = re.match(r"^\s+(workflows|mcp_servers):\s*\[(.*)\]$", line)
        if m: exp["registers"][m.group(1)] = [s.strip() for s in m.group(2).split(",") if s.strip()]; continue
        raise SystemExit(f"{path}:{n}: unrecognized expectation line: {line!r}")
    if "valid" not in exp:
        raise SystemExit(f"{path}: missing required `valid:`")
    return exp

def run(doc_path):
    doc = open(doc_path).read()
    cfg = {"config_version": "1",
           "agent": {"name": "conf", "preflight": "never", "instruction": doc},
           "intelligence": {"endpoints": ["http://127.0.0.1:1/v1"], "model": "mock"},
           "store": {"kind": "memory"}}
    cfg_path = doc_path + ".cfg.json"
    open(cfg_path, "w").write(json.dumps(cfg))
    try:
        v = subprocess.run([AGENTD, "-c", cfg_path, "--validate-config"],
                           capture_output=True, text=True, timeout=30)
        valid = v.returncode == 0
        errtext = v.stdout + v.stderr
        caps = {}
        if valid:
            c = subprocess.run([AGENTD, "-c", cfg_path, "--capabilities"],
                               capture_output=True, text=True, timeout=30)
            caps = json.loads(c.stdout) if c.returncode == 0 else {}
        return valid, errtext, caps
    finally:
        os.unlink(cfg_path)

fails = 0
for doc_path in sorted(glob.glob(os.path.join(ROOT, "*", "*.instruction.md"))):
    name = os.path.basename(doc_path).replace(".instruction.md", "")
    exp = load_expected(doc_path.replace(".instruction.md", ".expected.yaml"))
    valid, errtext, caps = run(doc_path)
    problems = []
    if valid != exp.get("valid"):
        problems.append(f"valid={valid}, expected {exp.get('valid')}")
        if not valid: problems.append(f"  said: {errtext.strip()[:200]}")
    for needle in exp["errors"]:
        if needle not in errtext:
            problems.append(f"error text missing {needle!r}")
    if "workflows" in exp["registers"]:
        got = [w.get("name") for w in caps.get("workflows", [])]
        if got != exp["registers"]["workflows"]:
            problems.append(f"workflows={got}, expected {exp['registers']['workflows']}")
    if "mcp_servers" in exp["registers"]:
        if caps.get("mcp_servers", []) != exp["registers"]["mcp_servers"]:
            problems.append(f"mcp_servers={caps.get('mcp_servers')}, expected {exp['registers']['mcp_servers']}")
    status = "ok " if not problems else "FAIL"
    print(f"  {status} {name}")
    for p in problems: print(f"       {p}")
    fails += bool(problems)
print(f"\n{fails} failures")
sys.exit(1 if fails else 0)
