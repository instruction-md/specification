# S14 — `BECAUSE:` — a rule's reason

**Type:** additive (1.x) · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

Rules without reasons are followed literally and fail at the edges; a reviewer
cannot tell a load-bearing rule from a stale one. The format has nowhere to put
the reason except inside the sentence.

## Normative text

§4.5, a new rule 7:

> 7. **Reasons.** A paragraph or list item beginning `BECAUSE:` (the same
>    recognition as a keyword), or a line beginning `BECAUSE:` that follows a
>    keyword block's text directly, is the **reason** of the normativity block
>    immediately before it in the same parent, when only blank lines separate
>    them. A container gives its reason as `{because="…"}`. A rule has at most
>    one reason: an attribute and a `BECAUSE:` paragraph together are refused
>    (`because-repeated`). A `BECAUSE:` that follows no rule is prose, and is
>    reported (`orphan-because`).

The reason is part of the rule: it moves, is attributed, and is dropped (S24)
with it. It is delivered on its own line after the rule's text:
`**BECAUSE:** …`, keeping a list item's marker when it was written as one.

## Example

```markdown
MUST: confirm the plan before quoting any limit.
BECAUSE: limits differ by plan and a wrong quote is binding.
```

Delivered:

```
**MUST:** confirm the plan before quoting any limit.
**BECAUSE:** limits differ by plan and a wrong quote is binding.
```

## Fixture

`conformance/corpus/reasons/`, refusal `because-repeated`.
