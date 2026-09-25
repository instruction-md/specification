# S24 — Rule strength and `overrides`

**Type:** additive (1.x); delivery drops overridden rules · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

An included house style says "SHOULD: keep replies under five sentences"; a
support document says "MUST: include every step". The model receives both and
guesses. Nothing says which wins, and nothing lets the writer say it.

## Normative text

§5.1, after the normativity kinds:

> **Strength.** `guardrail` > `never` = `must` = `always` > `should` = `avoid`
> > `may`. Notes, tips, warnings, cautions, importants and examples are not
> rules and have no strength. The table is `x-registry.strengths`.
>
> **Overrides.** A normativity container may carry
> `overrides="kind/name"` (a comma-separated list; the value is *not* an
> `@`-reference, because its target may live in an included document). At
> delivery, each target is looked up in this document, then in the documents
> it includes, in include order, depth first. A target found is **not
> delivered** — nor its reason — and the manifest records it in `overridden`.
>
> - A local target that is a `guardrail` is refused (`override-guardrail`); one
>   found in an included document is kept.
> - A rule may not override a stronger one: locally refused
>   (`override-stronger`), in an included document kept.
> - A target not in this document is reported (`overrides-external`); one
>   found nowhere is recorded in the manifest's `unresolved`.

The manifest's `overridden` key is present only when non-empty, so every
existing manifest is byte-identical.

## Example

```markdown
::include{id="ins_house-style"}

:::must{name=full-steps overrides="should/brevity"}
Include every step of the procedure, however long the reply becomes.
:::
```

## Fixture

`conformance/corpus/overrides/` with an included document.
