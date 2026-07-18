#!/usr/bin/env python3
"""Reference conformance runner: checks the corpus against an agentd binary.

Each fixture is a bare instruction document. The runner wraps it in a minimal
config, asks the binary to validate, and (when valid) reads the introspection
surface for what registered. Any runtime can conform by supplying its own
runner with the same observable checks; the corpus itself is neutral.
"""
import json, os, subprocess, sys, glob, re

AGENTD = os.environ.get("AGENTD_BIN", "agentd")
# Spec dialects the driven binary speaks. A fixture pinned to anything else is
# skipped, never failed (SPEC.md §7): the corpus may lead the implementation.
SPECS = set(os.environ.get("AGENTD_SPECS", "1").split(","))


def detect_config_version():
    """The config schema the driven binary accepts.

    The corpus is neutral over observable BEHAVIOUR, but a runner must still
    hand the binary a config, and that schema is implementation surface that
    moves between releases — agentd 1.6 takes `config_version: "1"`, 2.2
    rejects it as mixing v1 keys with v2 sections. Hardcoding either version
    makes every fixture fail against the other, for reasons that have nothing
    to do with the fixtures. So probe once with a directive-free document and
    use whatever validates.
    """
    forced = os.environ.get("AGENTD_CONFIG_VERSION")
    if forced:
        return forced
    for cv in ("2", "1"):
        cfg = {"config_version": cv,
               "agent": {"name": "probe", "preflight": "never", "instruction": "hello"},
               "intelligence": {"endpoints": ["http://127.0.0.1:1/v1"], "model": "mock"},
               "store": {"kind": "memory"}}
        path = os.path.join(ROOT, ".probe.json")
        open(path, "w").write(json.dumps(cfg))
        try:
            r = subprocess.run([AGENTD, "-c", path, "--validate-config"],
                               capture_output=True, text=True, timeout=30)
        finally:
            os.unlink(path)
        if r.returncode == 0:
            return cv
    raise SystemExit(
        f"{AGENTD}: no probed config_version validates; set AGENTD_CONFIG_VERSION")
ROOT = os.path.dirname(os.path.abspath(__file__))

def load_expected(path):
    # Minimal reader, STRICT: a line this subset does not recognize is fatal.
    # A silently-ignored typo in an expectation file is a passing test that
    # asserts nothing — the exact failure mode a conformance corpus exists to
    # prevent (finding: instruction.md review §7.3).
    exp = {"errors": [], "registers": {}, "spec": "1", "grants": []}
    for n, line in enumerate(open(path), 1):
        line = line.split("#")[0].rstrip()
        if not line.strip(): continue
        if line.strip() == "registers:": continue
        m = re.match(r"""^spec:\s*["']?([0-9]+)["']?$""", line)
        if m: exp["spec"] = m.group(1); continue
        m = re.match(r"^valid:\s*(true|false)$", line)
        if m: exp["valid"] = m.group(1) == "true"; continue
        m = re.match(r"^grants:\s*\[(.*)\]$", line)
        if m: exp["grants"] = [t.strip() for t in m.group(1).split(",") if t.strip()]; continue
        m = re.match(r"^errors:\s*\[(.*)\]$", line)
        if m: exp["errors"] = [s.strip().strip('"') for s in m.group(1).split(",") if s.strip()]; continue
        m = re.match(r"^\s+(workflows|mcp_servers):\s*\[(.*)\]$", line)
        if m: exp["registers"][m.group(1)] = [s.strip() for s in m.group(2).split(",") if s.strip()]; continue
        raise SystemExit(f"{path}:{n}: unrecognized expectation line: {line!r}")
    if "valid" not in exp:
        raise SystemExit(f"{path}: missing required `valid:`")
    return exp

def run(doc_path, grants):
    doc = open(doc_path).read()
    cfg = {"config_version": CONFIG_VERSION,
           # Grants are per fixture and default to NONE, so the trust ladder stays
           # testable: a fixture that needs `compute` says so, and a fixture that
           # asserts refusal-without-grant simply omits it (SPEC.md §5).
           "agent": {"name": "conf", "preflight": "never", "instruction": doc,
                     "document_capabilities": grants},
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

CONFIG_VERSION = detect_config_version()
print(f"  driving {AGENTD} with config_version={CONFIG_VERSION}, specs={'/'.join(sorted(SPECS))}")

fails = 0
for doc_path in sorted(glob.glob(os.path.join(ROOT, "*", "*.instruction.md"))):
    name = os.path.basename(doc_path).replace(".instruction.md", "")
    exp = load_expected(doc_path.replace(".instruction.md", ".expected.yaml"))
    if exp["spec"] not in SPECS:
        print(f"  skip {name} (spec {exp['spec']}; this runtime speaks {'/'.join(sorted(SPECS))})")
        continue
    valid, errtext, caps = run(doc_path, exp["grants"])
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
