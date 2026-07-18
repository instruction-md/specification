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

## Naming the binary is part of the claim

A conformance claim MUST carry the implementation version it was made against.
This is not bookkeeping — it is the rule the corpus learned the hard way.

Two true statements, made simultaneously, that appeared to contradict:

- the reference implementation's gate: **0 failures**;
- this repository's first run: **6 of 7 failed**, the 7th passing vacuously
  (it asserts `workflows: []`, trivially true when nothing extracts).

Both were correct. They ran different binaries, and neither statement said so.

The cause, verified from the implementation's history rather than assumed:
directive extraction (`directives.rs`, RFC 0034) entered that tree in commit
`97f34865` on **2026-08-23**. The agentd installed at `/usr/local/bin/agentd`
is dated **2026-08-18** — five days *older than the feature*. It reports
version `2.2.0`, which outranks the current `1.6.0` only because the project
reset its numbering to `v1.0.0` on 2026-08-23. So the higher version number is
the older software, and a stale install silently looks like a newer one.

Current state, both verified here:

| binary | probed `config_version` | result |
|---|---|---|
| `agentd 1.6.0` | 1 | **7/7 pass** |
| `agentd 2.2.0` (`/usr/local/bin`, predates the feature) | 2 | cannot extract; 6 fail |

Both runners now print the version first and diagnose a pre-feature binary once
by name, rather than emitting six opaque fixture failures. Point `AGENTD_BIN`
at a 1.x build.

The `config_version` probe exists for the same reason: that key is
implementation surface and it moved between those two builds (1.6 takes `"1"`,
2.2 requires `"2"`), so a hardcoded value made every fixture fail for reasons
unrelated to any fixture. A neutral corpus whose runner embeds a versioned
config schema has a coupling nothing pins. It is probed now, not embedded.

## `registry/kinds.json`

The per-version block-kind registry required by SPEC.md §3.2 rule 3. The
reserved-bare set is scoped to **the document's declared spec version**, not the
reader's — otherwise registry growth would retroactively invalidate documents
that legally used a bare name as prose before it became machinery.
