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

A conformance claim MUST carry the implementation version it was made against,
and a runner MUST confirm by probe that the binary implements the surface being
tested. This is not bookkeeping — it is the rule the corpus learned the hard
way.

**A version number does not establish a binary's age or its capability.** A
stale install can outrank a current release numerically while predating a
feature it is being tested for — release numbering gets reset, branches diverge,
packages linger. The number tells you what the build calls itself, not what it
implements.

The failure this produces is quiet and looks like a disagreement. Two true
statements, made simultaneously, that appeared to contradict:

- the reference implementation's own gate: **0 failures**;
- this repository's first run: **6 of 7 failed**, the 7th passing vacuously
  (it asserts `workflows: []`, trivially true when nothing extracts).

Both were correct. They ran different binaries, and neither statement said so.
The corpus was never wrong and the fixtures never changed; the claim was
under-specified.

So: the runners print the implementation version before the first fixture, and
probe extraction with one known-good document. A binary that validates that
document clean but registers nothing from it **predates the directive surface**
and is reported once, by name, instead of emitting a screenful of opaque
fixture failures. Point `AGENTD_BIN` at a build that implements it; the corpus
then passes **7/7**.

The `config_version` probe exists for the same reason. That key is
implementation surface and it moves between releases, so a hardcoded value made
every fixture fail for reasons unrelated to any fixture. A neutral corpus whose
runner embeds a versioned config schema has a coupling nothing pins — it is
probed now, not embedded, and `AGENTD_CONFIG_VERSION` overrides.

## `registry/kinds.json`

The per-version block-kind registry required by SPEC.md §3.2 rule 3. The
reserved-bare set is scoped to **the document's declared spec version**, not the
reader's — otherwise registry growth would retroactively invalidate documents
that legally used a bare name as prose before it became machinery.
