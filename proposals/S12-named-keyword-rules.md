# S12 — Named one-line rules: `MUST[name]:`

**Type:** additive (1.x) · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

Keyword rules are anonymous (§4.5 rule 5): a review can only point at them by
position, a diff cannot say "this rule changed", and nothing can reference
them. Naming one means switching to a three-line container.

## Normative text

§3.2 grammar:

```
keyword := "**"? KEYWORD ("[" name "]")? condition? ":" "**"? SP text
condition := SP "(if" SP [^()]+ ")"                     ; S15
```

§4.5 rule 5, replaced:

> 5. A keyword block is anonymous unless its keyword carries a name in
>    brackets: `MUST[tests-before-pr]: …`. A named keyword block has identity
>    exactly as a container with `name` does (§3.3 rule 9) — `must/tests-before-pr`
>    — and may be referenced. The name is not delivered.

## Example

```markdown
NEVER[refund-ceiling]: promise a refund above ${plan_limit} without approval.
The approval rule is [[never/refund-ceiling]].
```

Delivered: `**NEVER:** promise a refund above 500 USD without approval.`

## Fixture

`conformance/corpus/named-rules/`, and a refusal for a duplicate named keyword.
