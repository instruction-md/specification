# S9 — Author notes: block HTML comments are never delivered

**Type:** additive (1.x), delivery change · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

Delivery keeps "every other line unchanged" (§3.5), so a reviewer's note, a
TODO or a "do not tell the agent this" written as an HTML comment reaches the
model and costs tokens. Worse, a fence inside a comment is parsed: commenting
out a machinery block does not disable it.

## Normative text

§3.3, a new rule 11:

> **11. Author notes.** A line that begins at column 0 with `<!--`, outside
> fenced code, opens an **author note**, which ends at the end of the first line
> that contains `-->` (the opening line itself, for a one-line note). An author
> note is not scanned for blocks, references, keywords or parameters, and is
> never delivered. A comment that begins mid-line is inline HTML and is prose.
> Inside a YAML or code body, `<!--` is body content. Inside a `verbatim`
> container it is quoted material and is delivered.

§3.5 step 1 reads: "front matter and author notes are removed".

Appendix A: `<!-- … -->` at column 0 → nothing.

## Example

```markdown
<!-- legal asked for this wording on 2026-09-20; do not soften -->
MUST: quote the refund policy verbatim.

<!--
:::!workflow{name=old-refund}      ← commented out: not parsed, not loaded
steps: …
:::
-->
```

## Delivery impact

Documents with column-0 comments deliver without them. A document whose
comment contained a fence no longer loads that block — the intended meaning of
commenting it out.

## Fixture

`conformance/corpus/author-notes/`.
