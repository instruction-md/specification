# S26 — Named prose blocks have identity

**Type:** erratum (1.x) · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

§5.1 says a normativity container's `name` "makes the block referenceable",
and the same `name` attribute is offered on `context`, `form`, `tool`,
`glossary` and `example`. The registry marks every prose kind `x-identity:
false`, so a conforming reader never indexes those names, and

```markdown
:::must{name=tests-before-pr}
Run the tests.
:::

See [[must/tests-before-pr]].
```

is refused: `@must/tests-before-pr does not resolve`. The prose promises what
the registry forbids.

## Normative text

§3.3 rule 9 gains a sentence: "A prose kind has identity when its block
carries `name`; an unnamed prose block is anonymous." The registry marks every
prose kind that accepts `name` with `x-identity: true`; `name` stays optional
for them (the `identity-requires-name` rule remains machinery-only).

## Delivery impact

None. References to named prose blocks resolve; two prose blocks of one kind
with the same name are now refused as duplicates.

## Fixture

`conformance/corpus/named-rules/` (shared with S12).
