# S27 — End matter, and what belongs in front and end matter

**Type:** additive (1.x), delivery change · **Status:** accepted (owner, 2026-09-26) · **Raised by:** the editor's document-settings work, 2026-09-26

## Motivation

Front matter answers *what this document is and how it is delivered*. A
governed instruction also carries a **record**: who owns it, who approved it,
when it is next reviewed, what changed and why, which policies its rules come
from. Today that record is either missing, kept outside the document (where it
drifts from the text it describes), or written into front matter, where it
crowds the header an author reads first and mixes delivery settings with
bookkeeping.

Books solved the same problem long ago: front matter before the text, back
matter after it. This proposal gives an instruction the same shape — a YAML
block at the **end**, never delivered — and names the keys each block is for,
so editors, registries and reviewers read the same fields.

## Normative text

A new §3.1.1, after §3.1 rule 5:

> ### 3.1.1 End matter
>
> A document MAY end with **end matter**: a YAML block delimited by a line
> `---` and a closing `---` that is the last non-blank line of the document.
> The opening `---`
>
> 1. stands at column 0 and is the last `---` line before the closing one;
> 2. follows a blank line, or begins the body (directly after front matter);
> 3. is outside fenced code, author notes (§3.3 rule 11) and the bodies of
>    inert or verbatim containers — wherever the block scanner would not read a
>    fence; and
> 4. is followed by a line that begins with a YAML mapping key (`name:`).
>
> A block that does not meet all four is prose (a thematic break, or a setext
> heading underline), exactly as before this section existed.
>
> End matter **never reaches the model**. It is not scanned for blocks,
> references, keywords or parameters. It MUST be a YAML mapping; a reader
> refuses end matter that does not parse as one (`end-matter-yaml`). Unknown
> keys are preserved and ignored, as in front matter. End matter ends a
> *document*: the body of a variant or a container is never read for it, and
> an included document keeps its own (removed when it is inlined).

§3.5 step 1 reads: "front matter, end matter (§3.1.1) and author notes
(§3.3 rule 11) are removed".

Appendix B, a new row: end matter does not parse, or is not a mapping —
`end-matter-yaml` — `end matter is not valid YAML: …` /
`end matter is not a YAML mapping — write key: value lines`.

The block tree gains an optional `endMatter` object after `blocks`
(`$defs/endMatter` in the schema).

## What belongs where (informative)

Front matter is read **before** the text: what the document is, how it is
delivered, how it must be handled. End matter is read **after** it: the record
of who, when, why and from what. Neither is delivered. Readers MUST NOT refuse
any of these keys; editors and registries SHOULD offer them by name.

**Front matter** — identity, delivery, handling

| Key | Meaning |
|---|---|
| `spec`, `id`, `version`, `title`, `parameters`, `signature`, `delivery` | as §3.1 |
| `description` | one or two sentences on what the instruction is for (S2) |
| `license` | an SPDX expression (S1) |
| `requires` | families, spec and extensions it needs (S3) |
| `tags` | words to find it by |
| `language` | the BCP 47 tag of the prose, e.g. `en`, `de-CH` |
| `audience` | the agents or clients it is written for, e.g. `[claude-code, support-bot]` |
| `classification` | how the document itself is handled: `public`, `internal`, `confidential`, `restricted` |
| `handles` | the data the agent may meet under it, for reviewers: e.g. `[pii, payment, health, credentials]` |

**End matter** — the record

| Key | Meaning |
|---|---|
| `authors` | who wrote it (a name, or a list) |
| `owners` | who is accountable for it and approves changes |
| `reviewers` | who reviews changes |
| `approved` | `{ by, on }` — the last approval |
| `review` | `{ every, next }` — how often it is reviewed (`90d`) and when next |
| `changelog` | a list of `{ version, date, by, summary }`, newest first |
| `sources` | the policies and documents its rules rest on: `{ title, url }` or a string |
| `contact` | where questions go: an address or a channel |
| `notes` | anything else for reviewers |

A registry that records versions and approvals itself MAY show its own record
beside the document's; the document's end matter is what the author asserts,
the registry's is what happened.

## Example

```markdown
---
spec: "1"
title: Refund desk
description: Answers refund questions and escalates anything over the limit.
classification: internal
handles: [pii, payment]
---

# Refund desk

MUST: quote the refund policy verbatim.

NEVER: approve a refund above 200 EUR yourself.

---
owners: [ana]
approved: { by: ana, on: 2026-09-20 }
review: { every: 90d, next: 2026-12-20 }
changelog:
  - { version: "3", date: 2026-09-20, by: ana, summary: "Limit lowered from 300 to 200 EUR" }
sources:
  - { title: Refund policy, url: "https://example.com/policy/refunds" }
---
```

The agent receives the heading and the two rules; nothing below them.

## Delivery impact

A document that already ends with a thematic break, then `key: value` lines,
then `---` delivered those lines as prose (the closing `---` made the last of
them a setext heading); it now delivers without them. A reader implementing
an earlier 1.x delivers end matter as prose, as it always did: the document
is still valid there, and loses nothing it had before.

YAML is read under the 1.2 core schema (§3.1): `on: 2026-09-20` is the string
`"2026-09-20"`, not a date type, in every reader.

## Fixture

`conformance/corpus/end-matter/` — front matter with the handling keys, a
thematic break and a fenced `---` inside the body (both stay prose), and end
matter with every record key. Passes in the TypeScript, Python and Go readers.

## Revisions

- 2026-09-26: condition 3 names the regions the block scanner does not read
  (author notes, inert and verbatim bodies), and end matter is read only for a
  whole document, never for a variant or container body — both found in review
  of the first implementations, which disagreed on them.
