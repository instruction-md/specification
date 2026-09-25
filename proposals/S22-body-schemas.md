# S22 — Reference body schemas per machinery kind

**Type:** informative · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

A machinery body's schema is "published by the runtime" (§5.3), so a writer
gets no completion and no validation inside a `!workflow` or `!mcp` until
something runs it.

## Normative text

§9.3: a kind MAY carry `x-body-schema`, the URI of a JSON Schema for its body,
or an inline schema. It is informative: a runtime MAY publish a stricter one,
and a reader MUST NOT refuse a document because its body fails a reference
schema. Editors SHOULD use it for completion and hover. `!workflow` and
`!config` point at agentd's published schemas; the others carry inline schemas
of the keys the specification's own examples use, open to additions.
