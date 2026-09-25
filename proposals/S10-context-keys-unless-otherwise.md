# S10 — Registered context keys; `unless` and `otherwise`

**Type:** additive (1.x); delivery change for documents that used these names as inert kinds · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

`when` conditions match facts, but the specification never says which facts
exist: `agent` appears only in examples. A misspelt key (`agnet="claude"`) keeps
the content for every reader, silently, because an unknown key keeps content
(§5.2 rule 3). And there is no negation and no fallback: a document with one
`when` for staging and one for production delivers neither to a third
environment.

## Normative text

§5.2 `when`, a paragraph after the matching rules:

> **Context keys.** A reader that knows a fact of the following kinds SHOULD
> supply it under this key: `agent` (the model family: `claude`, `gpt`,
> `gemini`, …), `model` (the model identifier), `host` (the application the
> agent runs in: `claude-code`, `chatgpt`, `cursor`, `agentd`, …),
> `environment`, and `locale` (a BCP 47 tag). Any declared parameter is also a
> key. The list is `x-registry.context-keys`. A key that is neither is still
> evaluated under rule 3, and a validator reports it (Appendix C,
> `when-unknown-key`).

§5.2, two new structural kinds.

> #### `unless`
> Forms: C. Attributes: one or more `key="value"` conditions, as `when`.
> The body is dropped when **every** condition's key is known and matches, and
> kept otherwise — including when any key is unknown, for the reason `when`
> keeps content on an unknown key.
>
> #### `otherwise`
> Forms: C. Attributes: none (any given are ignored and reported).
> An `otherwise` belongs to the **group** of `when` and `unless` blocks that
> immediately precede it in the same parent, separated from it and from each
> other by blank lines only. It is kept when no block of its group was kept. An
> `otherwise` with no group is always kept, and reported.

Both record in the resolution manifest as `when` does, with their own
counters: `unless#1`, `otherwise#1`. Nested variants follow rule 4.

## Example

```markdown
:::when{environment="production"}
Every write is visible to a customer.
:::

:::when{environment="staging"}
This is a rehearsal against copied tickets.
:::

:::otherwise
You are in an environment this document does not know. Do not write anything.
:::

:::unless{host="agentd"}
You are running interactively; ask before any destructive step.
:::
```

## Delivery impact

A document that used `unless` or `otherwise` as an inert bare kind now has them
evaluated. No document becomes invalid.

## Fixture

`conformance/corpus/variants/` (all four outcomes, and a manifest).
