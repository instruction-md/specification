# S15 — Situational conditions: `MUST (if …):`

**Type:** additive (1.x) · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

"Under this condition" is the most common shape of a real rule, and it has no
form: the writer buries it in the sentence. It must not be confused with
`when`, which a reader decides before delivery.

## Normative text

§4.5, a new rule 8:

> 8. **Conditions.** A keyword may carry a condition in parentheses after its
>    name, if any: `MUST (if the refund exceeds ${plan_limit}): …`. A container
>    gives it as `{if="…"}`. The condition is text for the model: it is never
>    evaluated by a reader, and is delivered in the label —
>    `**MUST (if the refund exceeds 500 USD):**`. It may contain parameters and
>    references; it may not contain parentheses. `when` is decided by the
>    reader before delivery; `if` is decided by the model during the task.

## Fixture

`conformance/corpus/conditions/`.
