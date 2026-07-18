# The Instruction Document Specification

An open specification for **the instruction document**: one Markdown file that
defines an AI agent — its prose instruction and the machinery it carries
(workflows, tools, code, files, runtimes, knowledge, endpoints, people,
identity) — readable top to bottom by a person, loadable by a runtime, and
governable by a control plane.

**Status: `draft-1-rc`.** Content-complete and reconciled; not yet stable. See
[SPEC.md](SPEC.md).

## Two roles, equally first-class

The spec is written so that both consumers can implement every rule:

- a **runtime** extracts blocks and *becomes* the agent;
- a **control plane** stores, versions, diffs, reviews, resolves, serves,
  signs and revokes documents *without executing them*.

A construct only a runtime can check does not belong in the format.

## The idea that makes it one spec

Two independent designs converged on the same `:::` block syntax with opposite
meanings — one where blocks *degrade into* the delivered prompt, one where they
are *stripped from* it and fold into configuration. The spec's foundation is
that this is not a conflict but a missing concept: every kind declares a
**disposition**.

| disposition | at delivery | unknown-name policy |
|---|---|---|
| `prose` | degrades to labeled text the model reads | fail **open** — inert punctuation, prose preserved |
| `machinery` | stripped; folds into configuration | fail **closed** — name the known set |
| `structural` | resolved away | fail closed |

Machinery is lexically namespaced (`:::!workflow`) so both unknown-name policies
can coexist. That sigil was chosen on evidence: `:::!workflow` does not parse as
a directive in existing Markdown tooling, so the fence survives into rendered
output and machinery announces itself; a prefix that *does* parse gets its
markers consumed and renders configuration as though it were prose.

## Layout

```
SPEC.md                        the specification
conformance/                   the conformance corpus (Apache-2.0)
  core/                        (document, expected) fixture pairs
  registry/kinds.json          per-version block-kind + reserved-name registry (§3.2 rule 3)
  run-agentd.py                reference runner for one implementation
```

## Governance

The corpus is the arbiter. A change that breaks it is a major version. Spec
documents are versioned; a document declares the version it is written against
and a reader refuses what it does not implement, so the same bytes mean the
same thing to every reader.

Both known implementations run the corpus in CI and neither owns it:

- **instruction.md** — spec owner; control-plane reference (versioning,
  resolution, signing, revocation).
- **agentd** — runtime reference implementation.

## Licensing

Deliberately split:

- **Spec text** (`SPEC.md`, this README) — [CC BY 4.0](LICENSE).
- **Conformance corpus** (`conformance/`) — [Apache-2.0](conformance/LICENSE).

Creative Commons licenses are not appropriate for software and carry no patent
grant; a conformance suite that multiple vendors run in CI needs one.
Apache-2.0 is one-way compatible into GPL-3.0/AGPL-3.0, so an AGPL
implementation can vendor the corpus cleanly.

Copyright © 2026 TSOK Inc.

## Known open items at `draft-1-rc`

- The per-kind **lifecycle** table (§4.1) is drafted but unratified.
- Conformance **profiles** beyond Core are unwritten.
- The `!` sigil lexeme is settled but revisitable on repo review.
- `expected.document` (the control-plane observables, including delivered
  text) has no schema yet.
- A conformance claim must name the implementation version it was made
  against; the corpus passes 7/7 against `agentd 1.6.0` and cannot run against
  a build predating the feature. See
  [`conformance/README.md`](conformance/README.md) — including why the stale
  install reporting `2.2.0` is *older* than `1.6.0`.
