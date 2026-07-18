# Conformance corpus

**License: Apache-2.0** (see [LICENSE](LICENSE)) — deliberately not the CC BY
4.0 of the spec text. This directory is software: a multi-vendor test suite
needs a patent grant, and Apache-2.0 flows one-way into GPL-3.0/AGPL-3.0 so
copyleft implementations can vendor it.

Copyright © 2026 TSOK Inc.

## The format

A fixture is a **(document, expected-outcome) pair** over *observable*
behaviour — never implementation internals:

```
core/012-nested-is-text.instruction.md     the document
core/012-nested-is-text.expected.yaml      what any conforming reader must do with it
```

Expectations split by role, because a runtime and a control plane observe
different things:

- `expected.runtime` — valid / invalid, error substrings, what registered.
- `expected.document` — the block tree, per-kind dispositions, and the
  **delivered text**. The delivered-text assertion is what mechanically
  enforces the degradation contract (SPEC.md §3.2 rule 6); without it the
  contract is a promise rather than a test.

A fixture pins the `spec:` version it is written against, so dialect-boundary
cases — which fixture `012` exists to capture — are expressible.

## Running it

Each implementation supplies its own runner; the corpus is neutral.
`run-agentd.py` is the reference runner for the agentd runtime and shows the
shape: wrap each document minimally, ask the implementation to validate, read
its introspection surface, compare.

Runners MUST be **strict readers** — an unrecognized expectation line is fatal.
A lenient runner silently passes typo'd fixtures, which is the exact failure a
conformance suite exists to prevent.

## Authoring fixtures

Machinery blocks carry a `!` sigil, which triggers history expansion in
interactive `bash`/`zsh`. Author fixtures as files, or with quoted heredocs
(`<<'EOF'`) or single-quoted strings — never inside double quotes at an
interactive prompt, or `:::!workflow` will be silently corrupted.

## Current results — read this before trusting a "green" claim

Run against `agentd 2.2.0` (`/usr/local/bin/agentd`, the only agentd on this
machine), **6 of 7 fixtures fail**, and the 7th passes vacuously:

```
  driving agentd with config_version=2, specs=1
  FAIL 001-core-happy            workflows=[], expected ['drain']
  FAIL 010-unknown-kind          valid=True, expected False
  FAIL 011-unclosed-fence        valid=True, expected False
  ok   012-nested-is-text        (asserts workflows: [] — trivially true when nothing extracts)
  FAIL 013-mcp-needs-name        valid=True, expected False
  FAIL 014-attr-name-wins        workflows=[], expected ['renamed']
  FAIL 015-duplicate-name-refused valid=True, expected False
```

One cause explains all of it: **2.2.0 does not extract directives from
instruction text.** Verified directly, outside the runner — `:::banana{name=x}`
validates clean at exit 0 instead of failing closed on an unknown kind, and
`:::workflow{name=drain}` registers no workflow, via `--instruction-file` and
via config alike. The v2 config schema has no extraction gate: the only
matching properties are `agent.instruction` (a plain string) and
`intelligence.dialect` (unrelated — an LLM API dialect).

These fixtures encode the specification, so they are left as they are. A binary
that does not implement the spec is a finding about the binary.

The reference implementation's own gate reports green against a build it
describes as 1.6.0, which is not the binary here. That divergence is the point:
**the two sides were running different binaries and neither could see it.**
Pin the version you claim conformance for.

## `registry/kinds.json`

The per-version block-kind registry required by SPEC.md §3.2 rule 3. The
reserved-bare set is scoped to **the document's declared spec version**, not the
reader's — otherwise registry growth would retroactively invalidate documents
that legally used a bare name as prose before it became machinery.
