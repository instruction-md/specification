# S17 — `output` — the response contract

**Type:** additive (1.x) · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

What an agent must return — format, shape, length, language — is written today
as ordinary prose, so nothing can answer "what does this agent return?", and no
runtime can check it.

## Normative text

§5.1, a new prose kind.

> #### `output`
> Forms: C. Attributes: `name`, `title`, `format` (free text: `json`,
> `markdown`, `text`, …), `schema` (a qualified reference, usually to a
> `!data` block holding a JSON Schema).
>
> The body describes the response, in prose. Delivered under
> `**OUTPUT (format) — T:**` — each part present when its attribute is — then
> the body. The schema is not delivered (`!data` never leaves the document); a
> runtime MAY validate the agent's response against it, and a control plane
> MAY show it. A `schema` that does not resolve is a dangling reference.

## Example

```markdown
:::!data{name=reply format=yaml}
type: object
required: [summary, next_step]
:::

:::output{format=json schema=@data/reply title="Reply"}
One object. `summary` is one sentence; `next_step` is what happens next and when.
:::
```

## Fixture

`conformance/corpus/output/`.
