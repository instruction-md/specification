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

## `registry/kinds.json`

The per-version block-kind registry required by SPEC.md §3.2 rule 3. The
reserved-bare set is scoped to **the document's declared spec version**, not the
reader's — otherwise registry growth would retroactively invalidate documents
that legally used a bare name as prose before it became machinery.
