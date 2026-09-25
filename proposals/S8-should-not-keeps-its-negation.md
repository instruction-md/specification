# S8 — `SHOULD NOT:` keeps its negation

**Type:** erratum (1.x) · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

§4.5 rule 2 says "`SHOULD NOT:` is classified as `should`; the text carries the
negation". The text does not carry it: the keyword does. Every implementation
followed the letter of the rule and delivered

```
SHOULD NOT: store customer data in the workspace.
```

as `**SHOULD:** store customer data in the workspace.` — the rule inverted, in the
one place (the model's input) nobody reads. This is a defect in the
specification's text, not in one reader.

## Normative text

§4.5 rule 2, replaced:

> 2. `MUST NOT:` is an alias of `NEVER:`. `INFO:` is an alias of `NOTE:`.
>    `SHOULD NOT:` is a `should` block with the **`not` flag**, and delivers as
>    `**SHOULD NOT:**`. The container spelling is `:::should{not}`.

§5.1, normativity attributes: `should` gains the flag `not`.

Appendix A, a row: `SHOULD NOT: …` / `:::should{not}` → `**SHOULD NOT:** …`.

The registry carries the delivered label of every normativity kind in
`x-registry.labels` (and the flag's label in `x-registry.negated-labels`), so no
reader hard-codes the table this defect came from.

## Delivery impact

Every document containing `SHOULD NOT:` delivers differently — correctly. The
change is not a version bump: no conforming reader could have intended the
inverted text.

## Fixture

`conformance/corpus/should-not/`: keyword and container forms, delivered.
