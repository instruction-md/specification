# The Instruction Document Specification

An open specification, published by **instruction.md**, for the **instruction
document**: one Markdown file that fully defines an AI agent — the prose that
instructs it, and the machinery that equips it.

**Status: draft-1.** Content-complete; not yet stable.
Read the specification: [SPECIFICATION.md](SPECIFICATION.md).

## What an instruction document is

A document is plain Markdown. Any prose file is already a valid one. On top of
prose it adds **blocks** — fenced regions that carry meaning — and every block
has a **kind** (`must`, `human`, `workflow`) with one of three dispositions:

| disposition | what happens at delivery | unknown name |
|---|---|---|
| **prose** | degrades into text the model reads — `:::must` becomes `**MUST:** …` | inert; the prose survives |
| **machinery** | stripped, folds into the runtime's configuration; the model gets one acknowledgement line | refused, naming the known set |
| **structural** | resolved away — variants selected, includes inlined, parameters substituted | refused |

Machinery carries a `!` sigil — `:::!workflow`, `:::!human` — so that a
renderer that knows nothing of this specification still shows the fence, and
configuration never masquerades as text. Prose kinds are bare. The whole
design rests on one contract: **paste the document into a plain Markdown
viewer and it must still read as correct, complete guidance.**

## The forms

A kind is a unit of meaning; a form is a way of writing one. The container
fence is general but heavy for things that are small, bodiless, numerous, or
long. The specification defines the others:

```markdown
:::!human{name=oncall role=approver}         container — one instance, with a body
reach: { channel: "@channel/ops" }
:::

::!human{name=lead role=reviewer}            leaf — one instance, one line

:::!human[]                                  set — many instances, as a table
| name | role     | channel      |           (or a definition list, for bodied ones)
|------|----------|--------------|
| sre  | operator | @channel/ops |
:::

## !skill support-tone                       section — a long entity, as a heading
Warm, concise, specific…

MUST: run the test suite before a PR.        keyword — a rule, in one line
```

Inside prose, references are chips: `[@On-call](principal://…)` for people,
`[&Ticketing](server://…)` for capabilities, `[#Standards](instruction://…)`
for other documents, `[[function/lint]]` for a block in this one, `${env}`
for a parameter. Unrendered, each is a link or a word.

## Two roles, equally first-class

- A **runtime** extracts the machinery and *becomes* the agent.
- A **control plane** stores, versions, diffs, resolves, serves, signs and
  revokes documents *without executing them*.

Every rule is written so both can implement it.

## Trust

A document that declares code, files, listeners and people is a program.
Capability is **granted by the operator, never claimed by the document**:
machinery families sit behind independent grants — `material`, `knowledge`,
`interface`, `identity`, `compute`, `infra`, `compose` — each with its blast
radius stated, fail-closed, restart-only. A document served over a network
carries two signatures — an offline author signature and an online delivery
signature over a **resolution manifest** — and a signature only ever *caps*
what the operator granted. Authorization is separate from authenticity: the
serving index is the revocation channel, and a signed document stops being
usable the moment it stops being sanctioned.

## Versioning

A document declares the specification version it is written against; absent
a declaration it is version 1, the only version. A reader refuses what it
does not implement, and refuses the lexical markers of a newer version rather
than parsing them as prose — silence is the failure mode the format is built
to prevent.

## License

Specification text: [CC BY 4.0](LICENSE).

Copyright © 2026 instruction.md
