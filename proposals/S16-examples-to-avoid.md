# S16 — Examples of what to avoid

**Type:** additive (1.x) · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

A good example beside a bad one is the most effective way to show a model
what is wanted. The format has only the good half.

## Normative text

§5.1 `example`: attributes `name`, `title`, and the flag `avoid`. An example
with `avoid` is delivered under `**EXAMPLE (avoid) — T:**` (or
`**EXAMPLE (avoid):**` without a title); its body is quoted material as for any
example.

## Example

```markdown
:::example{title="A good closing"}
I've refunded the charge; it will reach your card within five working days.
:::

:::example{title="A closing that hands the work back" avoid}
Let us know if you have any other questions!
:::
```

## Fixture

`conformance/corpus/examples-avoid/`.
