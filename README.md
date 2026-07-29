# The Instruction Specification

**Status:** Draft 1, release candidate.
**Format version:** 1 (`spec: "1"`).
**Date:** 2026-07-20.
**Publisher:** instruction.md.
**License:** CC BY 4.0 (`LICENSE`).
**Media type:** `text/markdown; variant=instruction` (§11).

### Abstract

An **instruction** is one Markdown file that fully defines an AI agent: the
prose that instructs it and the machinery that equips it. It is readable by a
person, loadable by a runtime, and governable by a control plane. Any plain
Markdown file is already a valid instruction. This specification defines the
document model, the grammar, the forms in which a block may be written, the
registry of block kinds, delivery to a model, lifecycle, the capability grant
model, and signing, serving and revocation. The registry and grammar are also
published as a JSON Schema ([`instruction.schema.json`](instruction.schema.json),
§9), and complete example documents are in [`samples/`](samples/).

### Table of contents

- [1. Introduction](#1-introduction)
  - [1.1 Purpose](#11-purpose)
  - [1.2 Consumer roles](#12-consumer-roles)
  - [1.3 Requirements language](#13-requirements-language)
  - [1.4 Conformance](#14-conformance)
  - [1.5 Notation](#15-notation)
- [2. Terminology](#2-terminology)
- [3. Document model](#3-document-model)
  - [3.1 Front matter](#31-front-matter)
  - [3.2 Grammar](#32-grammar)
  - [3.3 Rules](#33-rules)
  - [3.4 References](#34-references)
  - [3.5 Delivery and degradation](#35-delivery-and-degradation)
  - [3.6 Control-plane and editor duties](#36-control-plane-and-editor-duties)
- [4. Forms — how a block is written](#4-forms--how-a-block-is-written)
  - [4.1 Container — one instance, with a body](#41-container--one-instance-with-a-body)
  - [4.2 Leaf — one instance, no body](#42-leaf--one-instance-no-body)
  - [4.3 Set — many instances](#43-set--many-instances)
  - [4.4 Section — one instance, whose body is a section of the document](#44-section--one-instance-whose-body-is-a-section-of-the-document)
  - [4.5 Keyword — normativity in a single line](#45-keyword--normativity-in-a-single-line)
  - [4.6 Alert — the blockquote spelling](#46-alert--the-blockquote-spelling)
  - [4.7 Inline — chips, tags, parameters, wiki-links](#47-inline--chips-tags-parameters-wiki-links)
  - [4.8 Equivalence across forms, and choosing one](#48-equivalence-across-forms-and-choosing-one)
- [5. Block registry](#5-block-registry)
  - [5.1 Prose kinds (bare)](#51-prose-kinds-bare)
  - [5.2 Structural kinds (bare)](#52-structural-kinds-bare)
  - [5.3 Machinery kinds (sigiled), by family](#53-machinery-kinds-sigiled-by-family)
  - [5.4 Sub-blocks](#54-sub-blocks)
  - [5.5 Lifecycle — what removal means](#55-lifecycle--what-removal-means)
- [6. The trust ladder](#6-the-trust-ladder)
- [7. Signing, serving, revocation](#7-signing-serving-revocation)
  - [7.1 Scope](#71-scope)
  - [7.2 The attestation](#72-the-attestation)
  - [7.3 Two signatures, and why both](#73-two-signatures-and-why-both)
  - [7.4 The resolution manifest](#74-the-resolution-manifest)
  - [7.5 Trust configuration](#75-trust-configuration)
  - [7.6 Verification, in order](#76-verification-in-order)
  - [7.7 Revocation — the half signing cannot do](#77-revocation--the-half-signing-cannot-do)
  - [7.8 Hard floor](#78-hard-floor)
  - [7.9 What this does not protect against](#79-what-this-does-not-protect-against)
- [8. A complete example](#8-a-complete-example)
- [9. Machine-readable schema](#9-machine-readable-schema)
  - [9.1 The block tree](#91-the-block-tree)
  - [9.2 What the schema enforces](#92-what-the-schema-enforces)
  - [9.3 What the schema carries as data](#93-what-the-schema-carries-as-data)
  - [9.4 What the schema cannot express](#94-what-the-schema-cannot-express)
- [10. Security considerations](#10-security-considerations)
- [11. Media type](#11-media-type)
- [12. References](#12-references)
  - [12.1 Normative references](#121-normative-references)
  - [12.2 Informative references](#122-informative-references)
- [Appendix A — Delivery reference](#appendix-a--delivery-reference)
- [Appendix B — Refusals](#appendix-b--refusals)

---

## 1. Introduction

### 1.1 Purpose

An instruction defines an agent end to end: the prose that instructs it, and
the machinery that equips it — workflows, tools, code, files, runtimes,
knowledge, endpoints, people, identity. It is readable top to bottom by a
person, loadable by a runtime, and governable — versioned, diffed, reviewed,
signed, served, revoked — by a control plane.

The format is a strict superset of Markdown prose. A file that contains none
of the constructs defined here is a valid instruction and is delivered
unchanged. A file that contains them loses nothing when shown by a viewer
that has never heard of this specification (§3.3 rule 6).

### 1.2 Consumer roles

Two consumer roles are first-class and equal:

- a **runtime** extracts the machinery and *becomes* the agent;
- a **control plane** stores, versions, diffs, resolves, serves, signs and
  revokes documents *without executing them*.

Every rule in this document is written so that both roles can implement it. A
construct that only a runtime can check does not belong in the format.

### 1.3 Requirements language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD",
"SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this
document are to be interpreted as described in BCP 14 [RFC2119] [RFC8174]
when, and only when, they appear in all capitals, as shown here.

The instruction format itself has a keyword form (§4.5) in which a line such
as `MUST: run the tests` is a block of the `must` kind. In this document that
form appears only inside fenced examples. It is a construct of the format,
addressed to the agent, and is never a requirement on implementers.

### 1.4 Conformance

A **reader** is any consumer that parses an instruction: a runtime, a control
plane, a validator, or an editor. A reader conforms to this specification
when it implements every MUST and MUST NOT that applies to its role:

- a **runtime** implements §3 to §7 in full;
- a **control plane** implements §3, §4, §5.1 to §5.4, §6 and §7, and
  performs the duties of §3.6, without executing machinery;
- a **validator** implements the structural rules of §3 to §6, as enumerated
  in §9.4;
- an **editor** implements §3 and §4 and the editor duties of §3.6.

A **refusal** is a reader declining the whole document. A refusal MUST name
the line, the construct, and what to write instead; Appendix B is the
catalogue. A reader MUST NOT partially load a document it refuses.

### 1.5 Notation

Examples are shown as they are **authored**. Where it matters, the text the
model receives is shown beneath, marked **Delivered:**, and what a Markdown
viewer unaware of this specification shows is marked **Unrendered:**. In
examples, text after `←` is an annotation and is not part of the document.

Section 8 is a complete example. A reader who learns better from a whole than
from parts may read it first.

## 2. Terminology

| Term | Meaning |
|---|---|
| instruction, document | one UTF-8 Markdown file: optional front matter, then interleaved prose and blocks. "Document" is used throughout for the file as a unit of parsing, delivery and governance |
| front matter | leading YAML metadata; always stripped from delivery (§3.1) |
| kind | a named unit of meaning — `must`, `human`, `workflow` — with exactly one disposition |
| block | one occurrence of a kind in a document, written in any of the forms of §4 |
| form | a way of writing a block: container, leaf, set, section, keyword, alert (§4) |
| **disposition** | per kind: **prose** (degrades into delivered text) · **machinery** (stripped; folds into configuration) · **structural** (resolved away) |
| sigil | the `!` that marks a machinery kind wherever its name is written: `:::!workflow`, `::!human`, `## !skill` |
| identity | a block's `name`, unique per kind within a document; `kind/name` is the qualified form (§3.3 rule 9) |
| reference | a claim that a block, document, principal or capability exists, written as `@kind/name`, a link, or a wiki-link (§3.4) |
| set, member | the form that declares many blocks of one kind at once, and one such block (§4.3) |
| sub-block | a bare block valid only inside a specific parent kind, sharing the parent's disposition and grant (§5.4) |
| family | a named group of machinery kinds; the unit of capability granting (§6) |
| grant | operator-side admission of a family; never made in-document |
| reader | any consumer that parses a document (§1.4) |
| refusal | a reader declining the whole document with a diagnostic (§1.4, Appendix B) |
| delivery | the text a model actually receives, after resolution and degradation (§3.5) |
| resolution | substituting parameters, selecting variants, inlining includes — everything that turns the authored bytes into the delivered bytes for one reader |
| degradation | the rule by which a prose block becomes delivered text, and by which it remains readable unrendered (§3.3 rule 6) |
| acknowledgement | the one line a machinery block leaves in the delivered text in place of its body (§3.3 rule 7) |
| operator surface | text the operator authored and the runtime read at startup, or a document admitted under §7 |
| trifecta | untrusted input, sensitive access and egress in one agent — the shape of an exfiltration path; blocks carry these tags and a runtime refuses to assemble all three silently |

**Disposition is the foundation.** The same fence syntax can carry text meant
for the model and configuration meant for the runtime. Disposition makes both
true at once, and it decides what happens to a name nobody recognizes (§3.3).

## 3. Document model

### 3.1 Front matter

Front matter is a YAML block delimited by `---` on the first line of the
document and `---` on a line of its own. It is optional. It never reaches the
model.

```yaml
---
spec: "1"
id: instruction://ins_42
version: ver_01K003
title: Support agent
parameters:
  - { name: environment, type: enum, values: [staging, production], source: workspace, required: true }
  - { name: region, type: string, source: agent_attribute, default: eu-west, description: "Reader's home region" }
---
```

| Key | Meaning | Who sets it |
|---|---|---|
| `spec` | the specification version this document is written against, as a string | the author |
| `id` | the document's stable identity as a URI | the control plane |
| `version` | the immutable version identifier of these bytes | the control plane |
| `title` | a display title; not delivered | the author |
| `parameters` | declared inputs, resolved at delivery; same schema as the `param` kind (§5.2) | the author |
| `signature` | the author signature: a JWS compact serialization on one line (§7.2); excluded from the digest; ignored by readers that do not verify | the control plane |

Rules:

1. **Absent front matter means version 1**, which is presently the only
   version. A document with no front matter, or with front matter that omits
   `spec`, is a version-1 document.
2. **Unknown keys are preserved and ignored.** A reader MUST NOT refuse a
   document for an unrecognized front-matter key, and MUST NOT deliver it.
3. **A reader refuses a version it does not implement** (§3.3 rule 8).
4. `spec` is a string. `spec: 1` (a YAML integer) is accepted and normalized;
   `spec: "1.0"` is refused — versions are integers.
5. The document is a **strict superset of prose**. An unknown bare kind is
   inert punctuation (§3.3 rule 2), so any plain prose file — with or without
   `:::` fences this specification has never heard of — is a valid document
   and loses nothing. Only the `!` sigil and the reserved bare names carry
   obligations. Adoption requires no change to existing files.

### 3.2 Grammar

```
document    := front-matter? (prose | block)*
block       := container | leaf | set | section | keyword | alert     ; §4
container   := open-fence attrs? EOL body close-fence                 ; §4.1
open-fence  := ":"{n} sigil? kind                                     ; n ≥ 3, column 0
close-fence := ":"{m}                                                 ; m ≥ n, alone on its line, column 0
leaf        := "::" sigil? kind attrs?                                ; exactly two colons, column 0; §4.2
set         := ":"{n} sigil? kind "[]" attrs? EOL body close-fence    ; §4.3
section     := "#"{1,6} SP "!" kind SP name attrs?                    ; ATX heading, column 0; §4.4
keyword     := "**"? KEYWORD ":" "**"? SP text                        ; start of a paragraph or list item; §4.5
alert       := "> [!" KEYWORD "]" EOL ("> " text EOL)*                ; §4.6
sigil       := "!"                                                    ; marks machinery
kind        := [A-Za-z][A-Za-z0-9_-]*
name        := [A-Za-z0-9][A-Za-z0-9._-]*
KEYWORD     := "MUST" | "MUST NOT" | "SHOULD" | "SHOULD NOT" | "NEVER" | "GUARDRAIL"
             | "NOTE" | "INFO" | "TIP" | "IMPORTANT" | "WARNING" | "CAUTION" | "EXAMPLE"
body        := (prose | block | code-fence)*                          ; inner blocks use shorter fences
code-fence  := a CommonMark fenced code block; colon fences inside it are not recognized (§3.3 rule 5)
attrs       := "{" (key ("=" value)?)* "}"
key         := [A-Za-z][A-Za-z0-9_.-]*
value       := bare | '"' quoted '"'
bare        := [^ \t"}]+                                              ; runs to whitespace or "}"
quoted      := ( [^"\\] | "\\\"" | "\\\\" )*
prose       := CommonMark text, in which the inline forms of §4.7 are recognized
```

`SP` is one or more spaces or tabs; `EOL` is the end of the line. Prose is
CommonMark [CommonMark] with the table extension of GitHub Flavored Markdown
[GFM] for table bodies; this specification adds the productions above and
changes nothing else.

**Fences are recognized at column 0 only.** An indented fence, a `:::`
mid-line, or a bare run of colons is prose. This is deliberate: a document
that needs to *show* a fence — a tutorial, a quoted example — indents it, and
it is shown rather than parsed.

**Attributes** sit on the opening line, inside one pair of braces, on that
line only:

| Written | Meaning |
|---|---|
| `{name=oncall}` | `name` = `oncall` |
| `{title="On-call engineer"}` | quoted value; may contain spaces and `}` |
| `{note="She said \"no\""}` | `\"` and `\\` are the only escapes |
| `{required}` | a bare key is a flag: `required` = `"true"` |
| `{allow="read, ticket:create"}` | a multi-valued attribute is comma-separated inside one value |
| `{target=@function/lint}` | a reference; bare is fine here, there is no YAML |
| `{}` | valid; no attributes |
| `{Name=x}` | keys are case-insensitive; canonical form is lower-case |
| `{name=a name=b}` | **refused** — a key may not repeat |
| `{name=on call}` | **refused** — `call` is not a key; quote the value |
| `{#oncall .human}` | **refused** — `#id` and `.class` are not part of this grammar |

Identity is the `name` attribute and classification is the kind. Both are
explicit; there are no shorthands for either.

### 3.3 Rules

Each rule is stated, then shown firing.

**1. Machinery is lexically namespaced.** `:::!workflow` is machinery; bare
`:::note` is prose. The sigil was chosen on evidence: `:::!kind` does not
parse as a directive in existing Markdown tooling, so an unaware renderer
shows the fence itself and machinery announces itself as machinery. A prefix
that *does* parse gets its markers consumed and its body rendered as prose —
configuration silently laundered into text, the inverse of the degradation
contract. The property this buys, as a property of the lexeme rather than a
rule anyone has to enforce: **machinery never masquerades as prose in an
unaware renderer.**

```markdown
:::!workflow{name=drain}         ← machinery: stripped, folds into configuration
:::note                          ← prose: delivered as text
```

**2. Unknown-name policy is per disposition.**

- An unknown **sigiled** kind fails **closed**. The document is refused, and
  the message names the known machinery set — so a mistyped `:::!worfklow`
  can never silently become text.
- An unknown **bare** kind fails **open**. It is inert punctuation; the prose
  inside it is preserved and delivered as ordinary text. The degradation
  contract holds.
- A sigiled kind that shadows a known **prose** name fails closed with the
  correction: `:::!must` → "did you mean `:::must`".

```markdown
:::!worfklow{name=x}             ← refused: unknown machinery kind "worfklow" (known: workflow, skill, …)
:::rationale                     ← inert; "Because…" is delivered as prose
Because the queue is shared.
:::
:::!must                         ← refused: "must" is a prose kind — did you mean :::must
```

**3. Reserved-bare guard, version-scoped.** A bare kind that shadows a
machinery name — `:::workflow` without the sigil — fails **closed** with
"did you mean `:::!workflow`". Without this guard, a forgotten sigil would
demote configuration to prose, one character away from the intended
document. The reserved set is the
machinery set of *the document's declared version*, not the reader's: a bare
prose name legal at version 1 stays legal under every later reader, or
registry growth would retroactively invalidate documents. Consequently this
specification lists its machinery names per version (§5.3), and a reader
checks a document against the set for the version it declares.

```markdown
:::workflow{name=drain}          ← refused: "workflow" is a machinery kind — did you mean :::!workflow
::human{name=lead}               ← refused: same guard, leaf form
:::human[]                       ← refused: same guard, set form
## human oncall                  ← a heading. The guard never applies to headings (§4.4).
```

**4. Nesting is fence-length containment.** A block opened with `::::` is
closed only by a run of four or more colons, so it may contain `:::` blocks.
This is the CommonMark code-fence convention: the longer fence contains the
shorter. Depth is unlimited in principle; readers MAY cap it and MUST say so
in the refusal.

```markdown
::::!test{name=lint-works target=@function/lint}
:::case{name=finds-one}
given:  { diff: "+ // TODO" }
expect: { count: 1 }
:::
::::
```

A `verbatim` attribute quotes a body without parsing it — for a block that
must contain literal fence syntax, such as a tutorial:

```markdown
::::context{title="How to declare a human" verbatim}
Write it like this:
:::!human{name=oncall role=approver}
:::
::::
```

**5. Colon-fence scanning is suspended inside fenced code.** A line of colons
inside a ```` ``` ```` block is code, not a fence. A function body, or an
embedded example document, never terminates its container.

**6. Degradation contract** (prose disposition). Paste the document into a
Markdown viewer that knows nothing of this specification and it must still
read as correct, complete guidance. A construct that hides prose when
unrendered is rejected from the prose vocabulary. Every prose form in §4
satisfies this by construction: a fence is visible punctuation, a table is a
table, a keyword is bold text, a link is a link.

**7. Acknowledgement contract** (machinery disposition). A machinery block
delivers exactly one provenance line and never its body. The line names the
kind and the identity, from the template the registry gives for the kind
(§5.3): `[workflow "drain" is loaded and runs autonomously]`. A set delivers
one line for all its members: `[3 human roles are declared: oncall, lead,
sre]`. Prose degrades in; machinery acknowledges out; between the two rules,
delivery is fully specified.

**8. Version-skew refusal.** A reader MUST refuse a document that declares a
version it does not implement. The refusal keys on *evidence* of a newer
version — the declared `spec` — not on the mere presence of front matter; a
prose file with unrelated front matter stays valid. Together with rule 2 this
closes the silent path: a later version's machinery is either declared, and
refused here, or sigiled and unknown, and refused there. The failure this
rule prevents is a reader that predates a construct parsing it as prose, so
that the configuration it carried vanishes without a diagnostic.

```markdown
---
spec: "2"                        ← refused by a version-1 reader: spec "2" is not implemented
---
```

**9. Block identity.** `name` is a block's identity within the document and
is **unique per kind**; `kind/name` is the qualified form. A duplicate
`kind/name` is refused. The rule holds across forms: a `!human` declared as a
leaf and another with the same name inside a set are duplicates. Reference
resolution (§3.4) is undefined without this rule.

```markdown
::!human{name=oncall role=approver}
:::!human[]
| name   | role     |
|--------|----------|
| oncall | reviewer |                ← refused: duplicate human/oncall (first declared at line 1)
:::
```

**10. Blocks are recognized on the operator surface only.** A reader parses
blocks in a document it read from operator configuration at startup, or that
it admitted under §7. Text that arrives through any other channel —
conversation, tool results, retrieved knowledge, an included document the
reader has not admitted, or model output — is never parsed for blocks,
whatever it contains. This is not configurable. Extracting machinery from the
untrusted channel would make prompt injection a feature of the format.

### 3.4 References

A reference points at something with identity. There are three positions a
reference can appear in, and each has one form.

**In prose, cross-document.** An ordinary Markdown link whose label begins
with a sigil and whose target is a URI naming the serving authority. The
sigil selects what kind of thing is referenced; the scheme confirms it.

| Sigil | Refers to | Schemes | Example |
|---|---|---|---|
| `#` | another instruction | `instruction://` | `[#Coding standards](instruction://ins_42)` |
| `@` | a person or an agent | `principal://` `agent://` | `[@On-call](principal://usr_7)` |
| `&` | a capability | `server://` `skill://` `model://` `service://` `sandbox://` `connector://` | `[&Ticketing](server://ticketing)` |

A sigil with a scheme from a different row — `[@Foo](server://x)` — is not a
reference. It is an ordinary link, rendered as one, and an aware editor
SHOULD warn. The scheme is authoritative; the sigil is a reading aid.

These degrade to links, which is the one construct that loses nothing
anywhere.

**In prose, local.** A link whose target is a fragment of the form
`#kind/name`, or the wiki-link shorthand for the same thing:

```markdown
Before deploying, ask [the on-call engineer](#human/oncall).
Before deploying, ask [[human/oncall]].
Before deploying, ask [[human/oncall|the on-call engineer]].
```

All three resolve identically. A fragment is a block reference **only** when
it has the shape `kind/name` and `kind` is a known kind; any other fragment —
`#installation`, `#faq` — is an ordinary heading anchor and is left alone.
A wiki-link MUST be qualified; `[[oncall]]` is not a reference and is
rendered literally, and an aware editor SHOULD warn.

**In attributes.** The form `@kind/name`, **always qualified**:

```markdown
::::!test{name=lint-works target=@function/lint}
```

Resolution MUST NOT depend on the schema of the attribute a reference sits
in. An unqualified `@lint` would mean "whatever kind this attribute
expects", and a diff tool without the registry could not resolve it. The
qualification is what makes references statically analyzable.

**In YAML bodies.** The same `@kind/name`, and it MUST be quoted, because `@`
is a reserved indicator in YAML [YAML] and parsers diverge on the unquoted
form:

```yaml
mounts:
  - { file: "@file/pyproject", at: /work/pyproject.toml }
```

**Quoting of references in bodies is semantically load-bearing; formatters
MUST preserve it.** A round-tripper that unquotes "safe" scalars breaks every
reference.

**Resolution rules.**

1. A local reference that does not resolve is a **refusal** — in attributes,
   in YAML, and in prose alike. A reference is a claim that something exists;
   a dangling one is an error, not a decoration. (This is the one place the
   prose layer is not fail-open: an unknown *kind* is inert, but a known kind
   with an unknown *name* is a broken link.)
2. Local references are **statically acyclic**, checked at load. A cycle is
   refused, naming the cycle.
3. Cross-document references are **cycle-guarded at resolution**, with a depth
   cap and a fan-out cap that a reader MUST publish. Static acyclicity across
   documents you do not hold is not achievable and is not claimed.
4. References inside inline code or fenced code are inert (§3.3 rule 5,
   extended to inline code).
5. In prose, `@` belongs to the person/agent sigil; in attributes it opens a
   block reference. The positions are disjoint. Editors MUST NOT rewrite the
   interior of an attribute list when applying prose transformations.

### 3.5 Delivery and degradation

Delivery is the transformation from authored bytes to the bytes one reader
receives. It runs, in order:

1. front matter is removed;
2. `include`s are inlined (each resolved with its own parameters, §5.2);
3. `when` variants are selected;
4. prose blocks are degraded to their delivered forms (Appendix A);
5. machinery blocks are replaced by their acknowledgement lines;
6. `${parameters}` are substituted.

Substitution runs last so that a parameter value is never re-parsed as
Markdown or as a fence. A resolved value is data: inserted as plain text,
size-capped, never interpreted.

What the model sees is a declared property of each kind — its disposition —
not a table hard-coded in the reader, so that a later version adds a kind by
adding a registry entry (§9).

**Layout is in place.** A block's delivered form replaces exactly the lines
the block occupied, and every other line of the document — prose, headings,
blank lines — is delivered unchanged. The replaced region is: for a
container or set, the opening fence line through the closing fence line;
for a leaf, its line; for a section, the heading through the last non-blank
line of the section; for a keyword, the paragraph or list item; for an
alert, the blockquote. A block that delivers nothing leaves nothing. Runs of
consecutive blank lines that result are collapsed to one, blank lines at
the start and end of the document are removed, and the delivered text ends
with exactly one newline. Inside a delivered block the
body's line breaks are preserved; a keyword label is prefixed to the first
line (`**MUST:** first line`, continuation lines unchanged, `> ` prefixes of
an alert removed); the `EXAMPLE` and `Tool` labels stand on a line of their
own above the body; a glossary delivers one line per term, its continuation
lines joined by single spaces. Two readers given the same document and
context therefore deliver the same bytes, which is what the delivery
signature (§7.3) needs.

**Tables inside data-bearing blocks: cell content is normative, layout is
not.** A formatter that preserves cells preserves semantics; column
alignment, padding and separator length carry no meaning.

### 3.6 Control-plane and editor duties

A conforming **control plane**:

- parses without executing;
- diffs **block-granular for review and attribution, line-granular for
  merge** — a changed workflow is one reviewable unit, but a merge still
  needs to know which line changed;
- attributes every block to an author and a version;
- resolves per reader deterministically and **attests the resolution**
  (§7.4);
- **serves revocation** (§7.7).

A conforming **editor**:

- preserves the quoting of references in YAML bodies (§3.4) and the interior
  of attribute lists (§3.4 rule 5) across every transformation it applies;
- **never silently edits a machinery body.** An assistant's proposed edit to
  a machinery body MUST surface as a separately confirmed diff and MUST NOT
  be bundled into a prose-edit hunk. The property is *no incidental rewrite*,
  not *never*: a user may still ask for the edit deliberately;
- renders inline forms as chips (§4.7) and warns on the near-misses this
  specification marks SHOULD-warn.

## 4. Forms — how a block is written

A **kind** is a unit of meaning. A **form** is a way of writing one. The
container fence is the general form, but it is heavy for entities that are
small, that have no body, that come in tens, or that are naturally a section
of a long document. This section defines the others.

Forms add no kinds and no semantics. Every form maps to the same kind, with
the same disposition, family, grant, attribute schema, identity rule and
lifecycle. **A reader MUST accept every form for every kind it accepts at
all**, except where a form is restricted below. §5 lists, per kind, the forms
that make sense for it; §4.8 says how to choose.

### 4.1 Container — one instance, with a body

```markdown
:::!human{name=oncall role=approver}
reach: { channel: "@channel/ops", escalate_after: 15m }
may: ["@workflow/deploy"]
:::
```

The opening line carries the kind and the attributes. The body is every line
between the fences, verbatim. **Body interpretation belongs to the kind:**

| Kind's body is | Kinds | Notes |
|---|---|---|
| YAML | most machinery: `!workflow` `!mcp` `!config` `!runtime` … | the block's definition; attributes on the fence override same-named keys in the body |
| Markdown | prose kinds, `!skill`, `when` | interpreted as prose; inline forms and keywords are recognized inside it |
| a fenced code block | `!function` | the code; the fence's info string is the language if the block does not declare one |
| a table | `!data`, `!fixture`, and any set (§4.3) | header row = field names; each row = one record |
| a definition list | `glossary`, and any set of bodied instances (§4.3) | term = name; definition = body |
| nothing | `!volume`, `!image`, `!secret-ref`, … | the leaf form (§4.2) is the natural spelling |

Blank lines inside a body are part of the body. A body MAY be empty. The
closing fence is alone on its line; text after it is a refusal.

**Attributes versus body.** When a kind's body is YAML, a key may be given
either on the fence or in the body. If both, **the fence wins** — the
attribute is the more visible of the two and is what a reviewer's eye lands
on. `name` on the fence is the identity; a `name:` in the body that
disagrees is overridden, not refused.

```markdown
:::!workflow{name=renamed}
name: original          ← ignored: the fence says "renamed"
steps: …
:::
```

### 4.2 Leaf — one instance, no body

```markdown
::!human{name=lead role=reviewer channel=@channel/eng escalate_after=1h}
::!image{name=py311 digest=sha256:3f0a… registry=registry.example/acme/py311}
::include{id="ins_42"}
::param{name=environment type=enum values="staging, production" source=prompt required}
```

**Exactly two colons**, at column 0, then the optional sigil, the kind, and
the attributes — all on one line. There is no body and no closing fence.

A leaf is valid for any kind whose body is optional (§5 marks them). A kind
that requires a body refuses the leaf form, naming what is missing:

```markdown
::!workflow{name=drain}         ← refused: workflow requires a body (its steps) — use :::!workflow
::must                          ← refused: must requires text — write "MUST: …" or use :::must
```

Everything the block needs is in its attribute list, so a multi-valued
attribute is written comma-separated and quoted: `allow="read, ticket:create"`.

**Unrendered:** a single visible line beginning `::` — self-marking, like the
container.

### 4.3 Set — many instances

The multiplicity form. A `[]` suffix on the kind declares that the block
defines **a set of instances**, one per entry of its body. The body is a
table or a definition list, chosen by what the entries need.

#### 4.3.1 Table body — instances defined by attributes

```markdown
:::!human[]
| name   | role     | channel        | escalate_after | may                |
|--------|----------|----------------|----------------|--------------------|
| oncall | approver | @channel/ops   | 15m            | @workflow/deploy   |
| lead   | reviewer | @channel/eng   | 1h             |                    |
| sre    | operator | @channel/ops   | 5m             | @workflow/deploy, @workflow/rollback |
:::
```

- The **header row** names the attributes. Header cells are attribute keys,
  case-insensitive. An unknown attribute for the kind is a refusal naming the
  column.
- The **separator row** (`|---|`) is required by the table grammar and
  carries no meaning; alignment markers are ignored.
- Each **body row** is one instance. A kind with identity requires a `name`
  column, and every row must fill it.
- A **cell** is an attribute value under §3.2's grammar. An empty cell means
  the attribute is absent. A cell containing a literal `|` writes it as `\|`.
  A cell that needs leading or trailing spaces, or a literal comma inside a
  single value, is quoted: `"Smith, Jane"`.
- A **multi-valued attribute** (`may`, `tags`, `allow`, `values`, …) is
  comma-separated within the cell. Which attributes are multi-valued is part
  of the kind's schema (§5).
- A cell for an attribute that carries **structured data** — a `case`'s
  `given` and `expect`, a `!stream`'s `retention` — holds a YAML flow value
  written inline: `{ max_age: 7d }`. The format passes the cell's text
  through unchanged; the kind's schema interprets it.
- References are written bare in cells — there is no YAML in a table.

#### 4.3.2 Definition-list body — instances defined by a body

```markdown
:::!skill[]
tone {when="writing to customers"}
:   Warm, concise, specific. No filler phrases.
    Apologize once, then move to resolution.

refunds
:   Never promise above the plan's limit without a human approval.
    See [[human/oncall]] for who can approve.
:::
```

- A **term** line is the instance's `name`, followed by an optional attribute
  list. The name obeys the `name` grammar of §3.2.
- The **definition** begins on the next line with a colon and at least one
  space. Continuation lines are indented to the same column. Multiple
  paragraphs are allowed, each beginning with `:`.
- Entries are separated by a blank line.
- The definition is the instance's body, interpreted as the kind's container
  body would be (Markdown for `!skill`, YAML for a YAML-bodied kind).

#### 4.3.3 Rules for sets

- A set body MUST be entirely a table or entirely a definition list. A body
  that mixes them, or that is neither, is a refusal.
- A set with no entries — a header row alone, or an empty body — is valid and
  declares nothing. The acknowledgement says so.
- **Every instance is a block** in every respect: it has identity, it is
  addressable as `@kind/name`, it is granted per family, and it retires
  individually (§5.5).
- A set carries its instances' shared attributes on the fence: everything
  in `{…}` on the `:::kind[]` line applies to every entry unless the entry
  overrides it. `:::!source[]{tags=untrusted_input}` tags every source.
- Kinds whose container body is *already* a list of entries — `glossary`,
  `form` — do not take the set form; `:::glossary[]` is refused as redundant.
- **Sub-blocks may take the set form inside their parent.** A table of test
  vectors is the most readable way to write ten of them:

```markdown
::::!test{name=lint-works target=@function/lint}
:::case[]
| name        | given                         | expect       |
|-------------|-------------------------------|--------------|
| finds-one   | { diff: "+ // TODO: fix" }    | { count: 1 } |
| ignores-old | { diff: "- // TODO: gone" }   | { count: 0 } |
:::
::::
```

- **Delivery.** A set of machinery delivers **one** acknowledgement line
  naming its members by name: `[3 human roles are declared: oncall, lead,
  sre]`. The noun is the kind's display noun from the registry (`x-nouns`,
  §9.3). A set of a kind that delivers nothing on its own (no
  acknowledgement template — `!peer`, `!secret-ref`, `!source`, …) delivers
  nothing as a set either. A set of prose degrades per entry, each labeled.
  Structural sets (`param[]`) resolve away.
- **Unrendered:** a table, or a definition list — both are among the
  best-degrading constructs Markdown has, and both read correctly with no
  knowledge of this specification.

### 4.4 Section — one instance, whose body is a section of the document

Long entities — a skill with pages of guidance, a persona, a function with
real documentation — are naturally written as sections, not fences. An ATX
heading whose text begins with a **sigiled** kind declares a block whose body
is the section beneath it:

```markdown
## !skill support-tone {when="writing to customers"}

Warm, concise, specific. Apologize once, then move to resolution.

### Escalation

If the customer asks for a human, hand off. Ask [[human/oncall]] and say so
in the reply. NEVER: promise a callback time you cannot see on the roster.

### What not to say

- "As per our policy"
- "Unfortunately"

## Refund rules

Everything above the roster is refunds; this heading ends the skill.
```

Rules:

1. The heading line is `#`s, a space, `!kind`, a space, the `name`, and an
   optional attribute list. Closing `#`s are permitted and ignored. Any
   heading level from 1 to 6 may be used. Setext headings (underlined) are
   not recognized as section blocks.
2. The body extends from the heading to the **earliest** of:
   - the next heading of the same or a shallower level — the same number of
     `#` characters or fewer — or the end of the document;
   - a sigiled heading at any level (rule 3);
   - a sigiled fence, leaf or set at column 0 (rule 4);
   - for a kind whose container body is YAML or code, the closing line of
     its single fenced code block (rule 6).

   Deeper *unsigiled* headings, with more `#` characters, belong to the
   body, as `### Escalation` does above.
3. A **sigiled heading at any level ends the current section and starts a
   new block.** Sections do not nest; containment uses fences.
4. **Bare** fences inside the section are parsed normally and belong to it:
   a `:::case` inside a `## !test` section is that test's case, and a
   `:::example` inside a `## !skill` section is part of the skill's
   guidance. A **sigiled** fence, leaf or set ends the section and returns
   the document to the top level: machinery is never the child of a
   section. To end a Markdown-bodied section before a bare block that
   belongs to the document, write a heading.
5. The section form is **machinery only**. A bare heading is always just a
   heading: `## human oncall` is prose, and the reserved-bare guard never
   applies to headings. Prose kinds with long bodies use the container.
6. **Structured-body kinds in section form.** For a kind whose container
   body is YAML or code (`!workflow`, `!mcp`, `!function`, …), the section's
   body MUST contain exactly one fenced code block, which is the definition,
   and **the section ends at that block's closing fence**. The prose before
   the fence is the block's documentation and is stored as its
   `description`. Whatever follows the fence belongs to the document, not to
   the section. This is the point of the form: the machinery and the
   paragraph that explains it travel together, and the document resumes
   without a heading.

````markdown
## !workflow nightly-digest

Runs at 02:00 in the workspace's timezone and posts a summary to the
engineering channel. It reads only; it never opens tickets.

```yaml
steps:
  wake: { kind: schedule, cron: "0 2 * * *" }
  post: { kind: agent, depends_on: [wake], instruction: "Summarize yesterday's tickets" }
  done: { kind: finish, depends_on: [post] }
```
````

   Where each section ends, shown:

````markdown
## !workflow nightly-digest

Runs at 02:00 and posts a summary.        ← description

```yaml
steps: …
```                                        ← the workflow section ends here (rule 6)

:::context{title="Digest format"}         ← top level
One paragraph, then the numbers that changed.
:::

## !skill summarizing

Lead with the number that changed.

:::example{title="A good summary"}        ← part of the skill: bare, no heading intervened (rule 4)
Refunds rose 12% week on week; two tickets account for the rise.
:::

:::!data{name=thresholds format=table}    ← ends the skill: sigiled (rule 4)
| metric  | alert |
|---------|-------|
| refunds | 10%   |
:::

## Reference                               ← ends nothing new: the skill already ended
````

7. **Delivery.** The acknowledgement line replaces the whole section, heading
   included.
8. **Unrendered:** a heading and its text. It reads exactly as the author
   wrote it, and the `!` in the heading marks what it is.

### 4.5 Keyword — normativity in a single line

The normativity prose kinds — `must`, `should`, `never`, `guardrail`, `note`,
`tip`, `warning`, `caution`, `important`, `example` — degrade at delivery to a
labeled line: `**MUST:** Run the test suite before opening a PR.` That
delivered form is also an **authored** form. A paragraph or list item that
begins with the kind's keyword in capitals, followed by a colon, *is* a block
of that kind:

```markdown
MUST: Run the full test suite before opening a PR.

**NEVER:** push to `main` directly.

- SHOULD: keep functions under forty lines.
- NOTE: the linter runs in the sandbox, not on the host.
- MUST NOT: store customer data in the workspace.
```

Recognition rules:

1. The keyword is recognized at the **start of a paragraph or list item**
   only: optional `**`, the keyword in capitals, `:`, optional `**`, then at
   least one space. `MUST:` mid-sentence, `must:` in lower case, `MUST` with
   no colon, or a keyword in a heading or a table cell, is prose.
2. `MUST NOT:` is an alias of `NEVER:`. `SHOULD NOT:` is classified as
   `should`; the text carries the negation. `INFO:` is an alias of `NOTE:`.
3. The block is the **paragraph** (to the next blank line) or the **list
   item** (its own text, not its nested items). A multi-paragraph rule uses
   the container form.
4. Keywords are recognized wherever Markdown prose is interpreted — in
   document prose, inside `!skill` bodies, inside `context`, inside `when` —
   **except inside `example`**, whose body is quoted material, and never
   inside YAML or code.
5. Keyword blocks are **anonymous**: they have no `name` and cannot be
   referenced. A tool that extracts them addresses them positionally. A rule
   that must be referenceable uses the container form with `name`.
6. There is nothing to degrade. The authored line *is* the delivered line,
   normalized to the bold form: `MUST: x` delivers as `**MUST:** x`.

### 4.6 Alert — the blockquote spelling

The same ten kinds may be written as a blockquote alert, the syntax several
Markdown renderers already style:

```markdown
> [!WARNING]
> The sandbox has no network. Anything that fetches will hang until timeout.

> [!MUST]
> Confirm the environment with the human before any write.
```

The alert type is the kind, case-insensitive. The blockquote's content is the
body, which may span paragraphs. Renderers that know the syntax style the
five common types; those that do not show a quote with a visible `[!MUST]`
label — readable either way. At delivery an alert is normalized to the
keyword form.

### 4.7 Inline — chips, tags, parameters, wiki-links

Inline forms live inside prose. An aware editor renders them as **chips** —
atomic, styled, resolvable, with completion. Unrendered, each is a link, a
word, or a bracketed name: all readable.

| Inline form | Meaning | Resolves | Unrendered |
|---|---|---|---|
| `[#Label](instruction://…)` | another instruction | at delivery, access-checked | a link |
| `[@Label](principal://…)` `[@Label](agent://…)` | a person or an agent | at delivery | a link |
| `[&Label](server://…)` and the other capability schemes | a capability | against the capability registry | a link |
| `[Label](#kind/name)` | a block in this document | at load; dangling is a refusal | a link |
| `[[kind/name]]` `[[kind/name\|Label]]` | the same, shorthand | at load | a bracketed name |
| `${name}` | a declared parameter | at delivery; substituted with its value | the placeholder |
| `#tag` | a free topic label; not a reference | never | a word |

Rules:

1. The **wiki-link** is sugar for the fragment link and MUST resolve
   identically. Without a label it renders as the target block's `name`;
   with `|Label`, as the label. At delivery a local reference degrades to its
   label text, or to `name` if unlabeled.
2. **`${name}`** is a parameter reference only in that exact form. `$name`
   bare is prose. An undeclared `${x}` is left verbatim and reported by the
   resolver; a declared but unresolvable *required* parameter makes the
   document undeliverable as authoritative content (§5.2).
3. **`#tag`** is a word beginning with `#` that follows whitespace, a line
   start, or `(`; `word#x` is not a tag; `# Heading` is a heading, because of
   the space. Tags are labels for search and grouping. They resolve to
   nothing and deliver as written.
4. Inline forms inside inline code or a fenced code block are **inert**.
5. A sigil in a link label whose target is a plain URL — `[@Ana](https://…)`
   — is an ordinary link, not a chip. Only the schemes of §3.4 make a
   reference.
6. **Reserved.** The inline directive syntax `:kind[text]{attrs}` is reserved
   by this specification and defines no kinds at version 1. A reader MUST
   treat it as prose and MUST NOT assign it meaning. It is reserved so that a
   later version can introduce inline definitions without colliding with
   documents written today.

### 4.8 Equivalence across forms, and choosing one

| Form | Multiplicity | Body | Restricted to | Unrendered, reads as |
|---|---|---|---|---|
| container `:::kind` | one | yes | — | fenced text |
| leaf `::kind` | one | no | body-optional kinds | one visible line |
| set `:::kind[]` | many | table or definition list | kinds not already a list | a table / a definition list |
| section `## !kind name` | one | the section | machinery | a heading and its text |
| keyword `MUST:` | one | the line | normativity prose kinds | the same line, bold |
| alert `> [!NOTE]` | one | the quote | normativity prose kinds | a labeled quote |
| inline | — | — | references, parameters, tags | a link or a word |

Rules that hold across all forms:

- The disposition is the kind's, never the form's. A set of machinery is
  machinery; a keyword `MUST:` is prose.
- The reserved-bare guard (§3.3 rule 3) applies wherever a kind name is
  unambiguous: after `:::`, after `::`, and before `[]`. It does not apply to
  headings or to keywords.
- Identity (§3.3 rule 9) is per kind across all forms.
- Grants (§6) and lifecycle (§5.5) are per kind. A set of `!function`s needs
  `compute` exactly as one does, and each member retires on its own.

**Choosing a form.** Ask two questions: does it have a body, and how many are
there?

| | one | many |
|---|---|---|
| **no body** | leaf `::kind{…}` | set with a table |
| **short body** | container | set with a definition list |
| **long body** | section (machinery) or container (prose) | several sections |
| **one line of normative text** | keyword | a list of keywords |

When in doubt, the container is always correct. The other forms exist to
make documents shorter and more readable, never to express something the
container cannot.

## 5. Block registry

Every kind declares: its disposition, its family (machinery only), its
attribute schema, the forms it accepts, and its lifecycle. This section is
that registry for version 1. Forms are abbreviated **C** container, **L**
leaf, **S** set, **§** section, **K** keyword, **A** alert.

### 5.1 Prose kinds (bare)

#### Normativity — `must` `should` `never` `guardrail` `note` `info` `tip` `important` `warning` `caution` `example`

Forms: C K A. Attributes (container only): `name` (optional; makes the block
referenceable), `title`.

These are RFC 2119-classifiable: every MUST in a document is mechanically
extractable for review, and a control plane can answer "what changed in the
rules" as a question about blocks rather than lines. `guardrail` is a `never`
with security intent — a boundary the agent must not cross regardless of
instruction — and is styled distinctly by editors. `info` is an alias of
`note`.

```markdown
:::must{name=tests-before-pr}
Run the full test suite before opening a PR. If any test is skipped, say
which and why in the PR description.
:::
```

**Delivered:**

```markdown
**MUST:** Run the full test suite before opening a PR. If any test is skipped, say
which and why in the PR description.
```

`example` shows what good output looks like. Its body is quoted material:
keywords inside it are not recognized, and it is delivered under a label with
the body verbatim.

```markdown
:::example{title="A good escalation reply"}
I've handed this to our on-call engineer, who will reply here within the
hour. I've noted that the outage began around 09:10 your time.
:::
```

**Delivered:** `**EXAMPLE — A good escalation reply:**` followed by the body.

#### `context`

Forms: C. Attributes: `name`, `title`.

Material that is true rather than imperative — facts, reference cards, the
shape of the system. Delivered wrapped so a model can tell reference from
instruction. Headings inside a context block keep their structure.

```markdown
:::context{title="Ticket lifecycle"}
A ticket is `open`, then `triaged`, then `resolved` or `escalated`.
Only a human moves a ticket to `resolved`.
:::
```

**Delivered:** `<reference title="Ticket lifecycle">` … `</reference>`.

#### `form`

Forms: C. Attributes: `name`, `title`.

Parameter capture. The body references declared parameters; an editor
renders a capture form for them; the delivered text is a list of the inputs
to collect — **never a live form**, which this specification forbids. The
list has one item per parameter referenced in the body, in order of first
reference: `- **name**`, followed — when any apply — by ` — ` and the
parameter's `description`, `required`, `one of: …` (an enum's `values`) and
`default: …`, separated by `; `. The body's own text is not delivered.

```markdown
:::form{title="Before we start"}
Which environment? ${environment}
Which region, if not the default? ${region}
:::
```

**Delivered:**

```markdown
**Inputs to collect — Before we start**
- **environment** — required; one of: staging, production
- **region** — Reader's home region; default: eu-west
```

#### `tool`

Forms: C L. Attributes: `cap` (required; a capability URI), `allow`, `deny`
(multi-valued), `name`.

Pins how a referenced capability may be used, in prose with inline policy. A
control plane validates `cap` against its capability registry at publish and
warns on unknown verbs. The label in the delivered line is the capability's
display name from that registry, or the `cap` URI when the registry does not
know it.

```markdown
:::tool{cap="server://ticketing" allow="read, ticket:create" deny="ticket:delete"}
Open tickets for engineering escalations only; billing has its own queue.
:::
```

**Delivered:**

```markdown
**Tool — Ticketing** (`server://ticketing`) — allowed: read, ticket:create; denied: ticket:delete
Open tickets for engineering escalations only; billing has its own queue.
```

#### `glossary`

Forms: C. Attributes: `name`, `title`.

Terms the agent must use precisely. The body is a definition list: term,
then definition. A glossary is the canonical use of the definition-list body,
and each term is delivered as `**Term** — definition`.

```markdown
:::glossary
Ticket
:   A tracked customer request. Never "issue" — that word is for engineering.

Escalation
:   Handing a ticket to a human. See [[human/oncall]].
:::
```

**Delivered:**

```markdown
**Ticket** — A tracked customer request. Never "issue" — that word is for engineering.
**Escalation** — Handing a ticket to a human. See oncall.
```

### 5.2 Structural kinds (bare)

#### `when`

Forms: C. Attributes: one or more `key="value"` conditions.

Keeps its body only for a delivery context that matches, and drops it
otherwise. Conditions match the same facts that parameters resolve from —
workspace configuration, verified identity attributes, declared parameter
values — so `when` needs no dimension system of its own.

```markdown
:::when{agent="claude"}
Use the `bash` tool for shell commands; do not describe commands you could run.
:::

:::when{agent="gpt" environment="production"}
You are running against production. Confirm every write with the human.
:::
```

Matching rules:

1. All conditions must match (they are ANDed).
2. A value may be a comma-separated set: `agent="claude, gpt"` matches either.
3. **An unknown key keeps the content.** A host that cannot evaluate a
   dimension keeps the guidance, while a host that can, tailors precisely.
   Dropping content on an unknown key would make every new dimension
   retroactively silence old documents.
4. `when` blocks may nest. Inner conditions are evaluated only if the outer
   kept.
5. The resolution manifest records every kept and dropped variant (§7.4), so
   a reader can tell that content was withheld even without seeing it.

**Delivered:** a kept variant is unwrapped — its body appears in place, with
no fence and no label. A dropped one leaves nothing.

**Unrendered:** the fence with its condition, then the body — it reads as
"when agent is claude: …", which is correct guidance for a reader who cannot
evaluate it.

#### `include`

Forms: L only. Attributes: `id` or `uri` (one required).

Transcludes another document at delivery. Composition over the reference
graph.

```markdown
::include{id="ins_42"}
::include{uri="instruction://ins_42"}
```

Rules:

1. The included document is resolved **with its own parameters and its own
   variants**, then inlined, recursively.
2. Access is re-checked against the *reader*. A document the reader may not
   see is not inlined and its existence is not revealed; the include degrades
   to `> _(included instruction not available)_`.
3. Cycles degrade to a visible note rather than looping; depth and total size
   are capped, and the manifest records the caps applied.
4. Included documents appear in the resolution manifest with the version
   resolved for this reader.

**Unrendered:** the single `::include` line — a visible pointer, which is the
right degradation for a reference.

#### `param`

Forms: L S. Attributes: `name` (required), `type`, `values`, `required`,
`default`, `source`, `description`.

Declares a parameter in the body of the document. Equivalent in every way to
an entry in front-matter `parameters`; declaring in the body keeps the
declaration next to the prose that uses it, and a set of parameters is more
readable as a table than as YAML.

```markdown
:::param[]
| name        | type   | values              | source          | required | default  | description                |
|-------------|--------|---------------------|-----------------|----------|----------|----------------------------|
| environment | enum   | staging, production | workspace       | true     |          | Target deployment          |
| region      | string |                     | agent_attribute | false    | eu-west  | Reader's home region       |
| ticket_id   | string |                     | prompt          | true     |          | The ticket being worked on |
:::
```

| Attribute | Meaning |
|---|---|
| `type` | `string` (default), `number`, `boolean`, `enum` (requires `values`) |
| `values` | the allowed values for `enum`; multi-valued |
| `required` | flag; an unresolved required parameter makes the document undeliverable as authoritative content — it is delivered as advisory with the placeholder intact and the name reported, or omitted, never silently blanked |
| `default` | used when the source yields nothing; also the sample value for authoring previews |
| `source` | where the value comes from at delivery, below |
| `description` | shown by capture forms and editors |

| `source` | The value comes from | Trusted because |
|---|---|---|
| `static` | `default` only | the author wrote it |
| `workspace` | the workspace's administered configuration | an administrator set it |
| `agent_attribute` | the reading principal's verified identity attributes | the identity provider asserted it |
| `prompt` | a human, asked before delivery — typically via a `form` block | a person supplied it deliberately |

Resolution reads **trusted sources only**. A value is never taken from
conversation text, model output, or any untrusted channel; a resolved value
is data, inserted as plain text, size-capped, never re-parsed.

`param` blocks resolve away entirely: nothing is delivered, and nothing is
acknowledged.

### 5.3 Machinery kinds (sigiled), by family

Every machinery kind delivers one acknowledgement line and never its body.
Attribute schemas below list the attributes that are part of the kind's
identity and policy; a kind's full definition lives in its YAML body, whose
schema the runtime publishes.

The machinery name set for version 1, which the reserved-bare guard checks
against:

```
workflow skill config mcp stream tools
file data media asset
knowledge retrieval source
endpoint ui human channel
peer policy secret-ref
runtime function test fixture
git volume image
agent
```

`override` is not in this set: it is a sub-block of `!mcp` (§5.4), written
bare inside its parent, and the guard does not apply to sub-blocks.

#### Core — `!workflow` `!skill` `!config` `!mcp` `!stream` `!tools`

What the agent runs, knows, connects to, and may call. Default grant.

| Kind | Forms | Attributes | Body | Acknowledgement |
|---|---|---|---|---|
| `!workflow` | C § | `name`, `armed` | YAML: the workflow's steps | `[workflow "x" is loaded and runs autonomously]` |
| `!skill` | C S § | `name`, `description`, `when` | Markdown: the skill's guidance | `[skill "x" is available — reference it as @skill/x]` |
| `!config` | C | — | YAML: a configuration fragment | `[runtime configuration is applied]` |
| `!mcp` | C L | `name`, `endpoint`, `allow`, `deny` | YAML: the server entry | `[mcp server "x" is connected; its tools are available]` |
| `!stream` | C L S | `name`, `retention` | YAML: retention policy | `[event stream "x" is declared]` |
| `!tools` | C | — | YAML: `disabled`, `overrides` | `[tool policy is applied]` |

```markdown
::!secret-ref{name=ticketing kind=file path=/var/run/secrets/ticketing}

:::!mcp{name=ticketing endpoint=https://mcp.internal.example/ticketing allow="read, ticket:*" deny="ticket:delete"}
auth: { kind: static, token: "@secret-ref/ticketing" }
:::
```

`!skill` is the kind most often written as a section (§4.4), because skills
are prose and are long. `!config` writes against an **allow-list**: grant
keys, security, services, specification version and signing configuration
are unreachable by construction, and the next configuration key added is
unreachable by default. The document cannot grant itself anything.

#### Material — `!file` `!data` `!media` `!asset`

Bytes and values the document materializes. Grant: `material`, except
`!data`, which is default — it never leaves the document.

| Kind | Forms | Attributes | Body | Acknowledgement |
|---|---|---|---|---|
| `!file` | C | `name`, `path` (required), `mode` | the file's content, verbatim | `[file "x" is present at path]` |
| `!data` | C | `name`, `format` | a table, YAML or CSV | `[data "x" is available]` |
| `!media` | C L | `name`, `kind`, `src`, `sha256` | Markdown: alt text and usage notes | `[media "x" is available]` |
| `!asset` | L | `name`, `kind`, `src`, `sha256` | — | `[asset "x" is available]` |

```markdown
:::!file{name=pyproject path=pyproject.toml mode=0644}
[project]
name = "acme-lint"
:::

:::!data{name=slo format=table}
| plan       | first_response | resolution |
|------------|----------------|------------|
| enterprise | 1h             | 8h         |
| team       | 8h             | 3d         |
:::

::!asset{name=model-card kind=pdf src=https://files.example/cards/mc.pdf sha256=9f2c…}
```

- `!file` is path-confined: no `..`, no absolute paths, no symlink targets.
  It refuses to overwrite a file it did not itself write.
- `!data` is constant data addressable by templates and workflows. It is
  the one material kind that needs no grant.
- A remote `src` on `!media` or `!asset` **requires** `sha256`; an unpinned
  remote asset is a mutable reference by another name. Inline base64 is
  permitted below a size cap that the reader publishes.

#### Knowledge — `!knowledge` `!retrieval` `!source`

Retrieval policy and provenance tags; executed by a knowledge service, never
by the reader. Grant: `knowledge`.

| Kind | Forms | Attributes | Body | Acknowledgement |
|---|---|---|---|---|
| `!knowledge` | C L | `name`, `server` | YAML: auto-context policy | `[knowledge base "x" is available; retrieval covers …]` |
| `!retrieval` | C | `name`, `knowledge` | YAML: chunking, embedding, reranking; the `!source` blocks it indexes, by reference | *(folded into the knowledge line)* |
| `!source` | C L S | `name`, `kind`, `server`, `tags` | YAML: kind-specific selection | *(folded into the knowledge line)* |

```markdown
::!knowledge{name=handbook server=kb}

:::!source[]{tags=untrusted_input}
| name     | kind | server | path       |
|----------|------|--------|------------|
| wiki     | mcp  | wiki   | space=ENG  |
| repo     | git  |        | docs/**    |
:::
```

`!source` is where `untrusted_input` most often enters an agent, and
declaring it inline is the point: a reviewer reading "we index the wiki" sees,
on the same screen, that this makes the agent's context attacker-influenced.
The set form with a fence-level `tags` attribute tags every source at once.

#### Interface — `!endpoint` `!ui` `!human` `!channel`

Listeners, render schemas, human roles. Grant: `interface`.

| Kind | Forms | Attributes | Body | Acknowledgement |
|---|---|---|---|---|
| `!endpoint` | C | `name`, `kind`, `path`, `methods` | YAML: auth, routing, rate | `[endpoint "x" listens at path]` |
| `!ui` | C | `name`, `kind` | Markdown, with `schema` and `preview` sub-blocks | *(nothing — it is for the human's client)* |
| `!human` | C L S | `name`, `role`, `channel`, `escalate_after`, `may` | YAML: reachability | `[human role "x" may be asked]`, with ` (may: …)` appended when `may` is set |
| `!channel` | C L S | `name`, `kind`, `server`, `target`, `tags` | YAML: kind-specific | `[channel "x" is available for …]` |

```markdown
::::!ui{name=approval kind=card}
Rendered by a display client when this gate is open.

:::schema
type: object
properties:
  summary: { type: string, title: "What will happen" }
  approve: { type: boolean, title: "Approve this action" }
required: [summary, approve]
:::
:::preview
┌─ Approve deploy? ─────────────────────┐
│ What will happen: ship v1.6.0 to prod │
│ [ ] Approve this action               │
└───────────────────────────────────────┘
:::
::::
```

- `!human` names a **role**, never contact details. Reachability goes
  through a `!channel`, so the document says "oncall" and the deployment
  decides who that is. Its `may` verbs bind to declared references
  (`@workflow/deploy`), never free strings.
- `!ui`'s `preview` is plain text on purpose: reviewable in a diff, and a
  client that cannot render the schema can always show the preview. It is
  normatively non-normative: clients render `schema` first, and tools MAY
  regenerate the preview.

#### Identity — `!peer` `!policy` `!secret-ref`

Principals, egress policy, secret *locations*. Grant: `identity`. Never
admissible over the wire (§7.8).

| Kind | Forms | Attributes | Body | Acknowledgement |
|---|---|---|---|---|
| `!peer` | C L S | `name`, `endpoint` | YAML: auth, grants | *(nothing)* |
| `!policy` | C | `name` | YAML: `mode`, `allow` | *(nothing)* |
| `!secret-ref` | L S | `name`, `kind`, `path` | — | *(nothing)* |

```markdown
::!secret-ref{name=hook kind=file path=/var/run/secrets/hook}
```

`!secret-ref` declares *where a secret comes from*, never its value. A literal
credential anywhere in a document is refused. `!policy` is a document-local
view of the deployment's egress rule; the stricter of the two wins.

#### Compute — `!runtime` `!function` `!test` `!fixture`

Code as declaration plus dispatch target. Grant: `compute`.

| Kind | Forms | Attributes | Body | Acknowledgement |
|---|---|---|---|---|
| `!runtime` | C | `name`, `isolation`, `image`, `network` | YAML: resources, mounts | *(nothing — infrastructure is not context)* |
| `!function` | C § | `name`, `runtime` (required), `lang` | a fenced code block, plus a `signature` sub-block | `[tool "x" is available: <signature>]` |
| `!test` | C § | `name`, `target` (required) | `case` sub-blocks | *(nothing — tests are for CI)* |
| `!fixture` | C | `name` | a table: `path`, `content` | *(nothing)* |

````markdown
:::!runtime{name=py311 isolation=oci image=registry.example/acme/py311@sha256:3f0a… network=none}
resources: { cpu: "1", memory: 512Mi, timeout: 30s }
mounts:
  - { file: "@file/pyproject", at: /work/pyproject.toml }
:::

::::!function{name=lint runtime=@runtime/py311}
Lint a diff and return findings as JSON.

```python
import json
def main(diff: str) -> dict:
    findings = [l for l in diff.splitlines() if l.startswith("+") and "TODO" in l]
    return {"count": len(findings), "lines": findings}
```

:::signature
input:  { diff: string }
output: { count: integer, lines: [string] }
:::
::::
````

- A `!function` is **a declaration bound to a runtime, never an
  interpreter**. The reader dispatches; it does not execute.
- `!runtime` declares a portable **isolation contract** — `isolation: oci |
  process | none` — and a reader refuses levels it does not support. Reader-
  side feature flags are not portable semantics; the document says what it
  needs. `image` is either a reference to a declared `!image`
  (`@image/py311`) or an image reference written in place; in both cases it
  MUST be digest-pinned, and a mutable tag is refused by name. `network: any`
  is refused; the sandbox boundary is the security boundary.
- A `!function` with no `!test` is a **warning**, deliberately: refusal
  would be disproportionate, and silence would repeat a known mistake.

#### Infrastructure — `!git` `!volume` `!image`

Mounted state and images. Grant: `infra`.

| Kind | Forms | Attributes | Body | Acknowledgement |
|---|---|---|---|---|
| `!git` | C L | `name`, `url`, `ref`, `readonly` | YAML: auth, sparse paths | *(nothing)* |
| `!volume` | L | `name`, `kind`, `size` | — | *(nothing)* |
| `!image` | L | `name`, `digest`, `registry` | — | *(nothing)* |

```markdown
::!git{name=handbook url=https://git.example/acme/handbook ref=main readonly}
::!volume{name=work kind=ephemeral size=1Gi}
::!image{name=py311 digest=sha256:3f0a… registry=registry.example/acme/py311}
```

An unpinned digest, a writable clone in a `readonly` context, or an
unverifiable signature where verification is declared, is a refusal at load.

#### Composition — `!agent`

Subagents instantiated from templates. Grant: `compose`. Never admissible
over the wire (§7.8).

| Kind | Forms | Attributes | Body | Acknowledgement |
|---|---|---|---|---|
| `!agent` | C L S | `name`, `template`, `ttl` | YAML: params | `[subagent "x" is available]` |

`!agent` instantiates a subagent from a template. A child may never hold a
grant its parent lacks; the intersection is computed at document load, so
templates must be statically resolvable.

#### `override` — a sub-block of `!mcp`

| Sub-block | Forms | Attributes | Body | Grant | Acknowledgement |
|---|---|---|---|---|---|
| `override` | C | `target` (required) | YAML: `description`, `tags`, `disabled`, `params` | the parent's (default) | *(nothing; folded into the parent's line)* |

`override` is written bare inside a `!mcp` block (§5.4) and adjusts one of
that server's tools. It is **append-only and attributed**: the server's own
description is preserved verbatim, and the override renders as a delimited,
provenance-marked operator annotation beneath it. It may add trifecta tags,
disable a tool, or tighten an enumeration. Description *replacement* and
default changes are behavioural steering, not narrowing, and are refused.

```markdown
::::!mcp{name=ticketing endpoint=https://mcp.internal.example/ticketing}
:::override{target=create_ticket}
description: >
  Use for engineering escalations only — billing has its own queue.
tags: [sensitive]
:::
:::override{target=delete_ticket}
disabled: true
reason: "Deletion is a compliance decision; we tombstone instead."
:::
::::
```

### 5.4 Sub-blocks

Sub-blocks are valid only inside their parent, unsigiled (the parent's fence
and sigil govern them), with the parent's disposition and grant.

| Sub-block | Parent | Body |
|---|---|---|
| `case` | `!test` | YAML: `given`, `expect` — or a `case[]` table |
| `signature` | `!function` | YAML: `input`, `output` |
| `schema` | `!ui` | a JSON Schema in YAML |
| `preview` | `!ui` | plain text |
| `override` | `!mcp` | see §5.3 |

Their names are scoped to the parent and **exempt from rule 9's uniqueness**
— two `!test` blocks may each carry a `case` named `happy` — and therefore
they have no document-level identity and MUST NOT be referenced. A sub-block
outside its parent is refused, naming the parent it needs.

### 5.5 Lifecycle — what removal means

A document changes while the agent it defines is running. This section says
what a reader does when a block that was there is gone. Six general rules,
then the per-kind table.

1. **Dangling references refuse the update.** A live update that removes a
   block still referenced by a surviving block is refused whole — a
   `!runtime` cannot vanish under its `!function`s.
2. **In-flight work keeps what it resolved under**, and under per-reader
   resolution the pin is the **delivered digest**, not the version: one
   authored version has many delivered byte-streams. A running workflow stays
   pinned to its delivered definition; an open ask keeps its resolved channel;
   a dispatched call completes under its runtime.
3. **Removals apply at a quiesce boundary**, and each logs one retirement line
   naming the block. A departure is an event, never a silence.
4. **Trifecta re-computation on update: widening refuses; narrowing applies.**
   Removing an `untrusted_input` source is admissible — but see `!source`:
   removing the declaration does not remove the derived state.
5. **Absence is not unavailability.** Only an affirmative signal moves a block
   through its lifecycle: an explicit revocation, or omission from a
   *successful* read of the effective set. A failed or unreachable read is
   staleness — continue under last-known state until the freshness deadline,
   then refuse new work and leave live work alone.
6. **Security configuration never hot-loosens.** Any block or field that maps
   to security configuration is restart-only in the loosening direction,
   whatever its family.

| Kind | On removal by live update |
|---|---|
| `!workflow` | new starts disarm; live runs stay pinned and run out under the block's drain policy |
| `!skill` | leaves the catalogue; turns in flight keep their loaded copy |
| `!config` | fold recomputed; a removal touching a restart-only path refuses |
| `!mcp` | server disconnects; its tools leave the registry; in-flight calls complete |
| `!stream` | new appends refuse as undeclared; durable events and consumer offsets are retained state, reaped by retention — never deleted by a document edit |
| `!tools`, `override` | registry decoration recomputed; the next turn sees it |
| `!file` | compared against the recorded `(block id, delivered digest at write time)`, never against authored content. Unmodified ⇒ removed. Modified ⇒ left, with the modification attributed where the runtime can and the ambiguity named where it cannot. Re-adding a left-behind path **adopts** it when the new delivered bytes match; otherwise surfaces `file-adoption-required` rather than a generic write refusal |
| `!data` | rule 1: removal with live references refuses |
| `!media` `!asset` | reference forgotten; any fetched cache dropped |
| `!knowledge` `!retrieval` `!source` | **two-phase retraction with an observable state.** Removing the declaration does not narrow the corpus — derived chunks survive in the retrieval store. (1) The source is marked `retracting` and the runtime filters it **at query time**, so retraction is effective on the next query with no dependence on an asynchronous delete. (2) The runtime requests derived-chunk deletion. (3) The lifecycle completes on confirmed deletion or **errors** on deadline expiry. Retraction also runs when revocation is discovered at reconnect. **A control plane revokes documents; a runtime retracts derived state** |
| `!endpoint` | listener unbinds at the quiesce boundary; in-flight requests complete within drain. *Addition* on live update logs loudly and, for a document that arrived over the wire, requires content-bound approval — a boot-time grant admits the family, it does not pre-approve a remote party binding new listeners |
| `!ui` | no runtime state; clients read the new schema on next fetch |
| `!human` `!channel` | rebinding applies to the next ask; open asks keep their resolved channel |
| `!peer` | forgotten for new dials |
| `!policy` | restart-only (rule 6) |
| `!secret-ref` | pointer forgotten; resolution happens at use, so nothing cached needs scrubbing |
| `!runtime` `!image` `!volume` | rule 1 while referenced; unreferenced ⇒ forgotten; a `!volume` with materialized state is restart-only |
| `!function` | tool retires from the registry; calls in flight complete |
| `!test` `!fixture` | no runtime state to retire |
| `!agent` | child drains gracefully, then stops |

A member of a set retires exactly as a standalone block of its kind would.
Removing one row from a `:::!human[]` table retires that one human.

## 6. The trust ladder

A document that declares code, files, listeners and people is a program, and
a program that arrives as a document is precisely the shape of a supply-chain
problem. So capability is **granted by the operator in configuration, never
claimed by the document**, and each grant names its blast radius.

Machinery families above the default require an explicit operator grant,
held outside the document; fail-closed; restart-only; introspectable.
**Grants are an independent set, not cumulative levels:** granting `compute`
grants nothing else, and the table's order is presentational.

| Grant | Families | Blast radius when granted |
|---|---|---|
| *(default)* | prose · structural · core machinery · `!data` · `override` sub-blocks | the prompt, and configuration the runtime already accepted; `!data` never leaves the document |
| `material` | `!file` `!media` `!asset` | bytes materialize into the workspace |
| `interface` | `!endpoint` `!ui` `!human` `!channel` | listeners bind; people become addressable |
| `knowledge` | `!knowledge` `!retrieval` `!source` | **the agent's context window points at a corpus others may influence** — attacker-steered context with tools in reach; feeds the trifecta directly |
| `identity` | `!peer` `!policy` `!secret-ref` | credentials and principals become nameable |
| `compute` | `!runtime` `!function` `!test` `!fixture` | code executes, in declared isolation |
| `infra` | `!git` `!volume` `!image` | state mounts; images pull |
| `compose` | `!agent` | children carry this document's grants; the intersection is computed at document load, so templates must be statically resolvable |

The grant, in operator configuration, is a list of family names:

```yaml
document_capabilities: [material, knowledge, interface]
```

Rules that make the ladder real:

1. **Fail-closed and specific.** A block whose family is not granted is a
   refusal naming the block, the line, the family and the exact grant to add:
   `line 12: :::!runtime needs the "compute" grant — add it to
   document_capabilities`. Not a warning, not a skip.
2. **A grant admits; it does not authorize.** `compute` lets a document
   *declare* a function; whether it may run still passes tool policy, egress
   policy and the trifecta check. Two independent gates, because one gate is
   a single point of failure.
3. **Grants are restart-only.** Widening what a document may do is never a hot
   reload. A capability an operator believes revoked, still live in the
   running process, is the failure this rule exists to prevent.
4. **The document cannot grant itself anything.** `!config` is allow-listed
   (§5.3); a served document is never a source of its own trust configuration
   (§7.5).
5. **Content-driven trifecta widening is refused.** On a live update, if the
   re-resolved document's trifecta computation differs from the loaded one,
   the update MUST NOT apply — refuse-and-keep or refuse-and-stop, the
   operator's choice, never silently widen.

`override` sits on the default rung deliberately. A block that can only
make an agent *more* careful — add a tag, disable a tool, tighten an
enumeration — needs no grant to use, and gating it would push operators
toward the blunter instrument of disabling the server outright.

## 7. Signing, serving, revocation

### 7.1 Scope

A document carrying machinery is code, and a document delivered over a
network is a supply chain. This section specifies what a signature attests,
what it authorizes, and — separately — what keeps it authorized. Signing
establishes **authenticity and a capability ceiling**; it does not establish
**authorization**, which is §7.7. A signature is valid forever; a document
that can execute code must stop being usable the moment it stops being
sanctioned.

### 7.2 The attestation

Signatures are JWS compact serializations [RFC7515] over a JSON claims
object [RFC8259]. Implementations MUST support Ed25519 (`alg: EdDSA`,
[RFC8037]). The JOSE header carries `alg` and `typ` — `author` or
`delivery`, equal to the `typ` claim — and MAY carry `kid` to select among a
publisher's pinned keys. A verifier MUST check the `typ` claim, not only the
header, and MUST refuse a signature whose `typ` is not the one the
verification step expects: a delivery signature never stands in for an
author signature, nor the reverse. Digests are SHA-256 [FIPS180-4], written
`sha256:<hex>` with lower-case hexadecimal.

**Author claims** — over the authored bytes:

```json
{ "spec": "instruction/1",
  "typ": "author",
  "doc": "instruction://ins_42",
  "version": "ver_01K003",
  "digest": "sha256:…",
  "capabilities": ["material", "compute"],
  "pub": "https://instruction.md/pub/acme",
  "iat": 1757000000, "exp": 1788536000 }
```

**Delivery claims** — over the delivered bytes, for one reader:

```json
{ "spec": "instruction/1",
  "typ": "delivery",
  "doc": "instruction://ins_42",
  "version": "ver_01K003",
  "digest": "sha256:…",
  "aud": "principal://usr_7",
  "manifest": { "authored": { "version": "ver_01K003", "digest": "sha256:…" }, "…": "…" },
  "author": "eyJhbGciOiJFZERTQSIsInR5cCI6ImF1dGhvciJ9.…",
  "capabilities": ["material"],
  "pub": "https://instruction.md/pub/acme",
  "iat": 1757000000, "exp": 1757003600 }
```

| Claim | Author signature | Delivery signature |
|---|---|---|
| `spec` | `instruction/1`, the attestation format; REQUIRED | the same |
| `typ` | `author` | `delivery` |
| `doc` | the document's `id` (§3.1) | the same |
| `version` | the authored version attested | the authored version this delivery was resolved from |
| `digest` | the **authored bytes** (below) | the **delivered bytes**, exactly as sent |
| `aud` | — | the reader, as a `principal://` or `agent://` URI; REQUIRED |
| `manifest` | — | the resolution manifest of §7.4, embedded as JSON; REQUIRED |
| `author` | — | the author signature, JWS compact serialization, verbatim; REQUIRED |
| `capabilities` | the ceiling the author stands behind | the ceiling the delivery service attests; MUST be a subset of the author's |
| `pub` | the publisher, matched against trust configuration (§7.5) | the same |
| `iat`, `exp` | seconds since the epoch; long-lived | SHOULD expire within hours: it attests one resolution, not the document |

**What the author digest covers.** The authored bytes are the document as
stored, with one exception: when the front matter carries a `signature` key,
the line that holds it is excluded, so that a signature can travel inside
the document it signs. `signature` MUST therefore be a top-level front-matter
key whose value is the author signature's JWS compact serialization on a
single line, and a verifier removes exactly that line before hashing. A
delivery signature is never carried in the document: it travels in the
delivery envelope beside the delivered bytes — over HTTP, in the
`Instruction-Signature` response header; over other transports, as a
string-valued metadata field named `signature`.

**A signature caps; it MUST NOT grant.** Effective families = operator grant ∩
per-source ceiling ∩ attested `capabilities`. A document attested for
`compute` on a runtime that granted only `material` gets `material`.
`capabilities` is the maximum the publisher stands behind, not what the
document uses; a block outside its attestation refuses the document whole.

### 7.3 Two signatures, and why both

- **Author signature** (`typ: "author"`) — an **offline** key over the
  *authored* version. Attests who wrote it and what they stand behind.
  Survives compromise of the control plane, which is the only reason it
  exists.
- **Delivery signature** (`typ: "delivery"`) — an **online service key**, in
  the serving path, over the *delivered* bytes, the audience, the resolution
  manifest (§7.4) and the author signature itself, embedded. Attests what
  was actually sent, and to whom.

The online key is structurally weaker than the offline one, and this
specification says so rather than letting deployments discover it. A
document that carries `compute` or `infra` blocks MUST be admitted only with
both signatures present and valid; where a deployment can verify only one,
it MUST be the author signature.

The verification chain must be implemented as stated: the delivery signature
covers the manifest; the manifest names the authored version and its digest;
the author signature covers that digest. A verifier that skips the manifest
cannot check authorship at all.

### 7.4 The resolution manifest

Per-reader resolution means the server chooses bytes. Without an attested
account of *how*, that is an unbounded content-injection channel carrying a valid
signature. The manifest is that account:

```yaml
authored:   { version: ver_01K003, digest: "sha256:…" }
parameters: [ { name: environment, source: workspace, value_digest: "sha256:…" } ]
facts:      [ { key: agent, value_digest: "sha256:…" } ]
variants:   { kept: [when#3], dropped: [when#1, when#2] }
includes:   [ { uri: "instruction://ins_7", version: ver_…, digest: "sha256:…" } ]
limits:     { include_depth: 3, include_bytes: 18422 }
```

1. The manifest MUST enumerate **every input that affected the delivered
   bytes**, and a resolver MUST NOT apply an input absent from it.
2. Values appear as **digests, not values** — resolved values are frequently
   identity attributes. A verifier confirms *determinism*: same context, same
   manifest, byte-identical re-read. Only a party holding the values confirms
   *correctness*; an auditor with the resolution context can replay end to
   end.
3. `includes` lists every transcluded document recursively, at the version
   resolved for *this* reader.
4. `limits` reports the caps actually applied; a resolution that hit a cap is
   truncated and the reader is entitled to know.
5. `variants.dropped` is REQUIRED: a reader must be able to tell that content
   was withheld, even without seeing it — otherwise `when` is
   indistinguishable from censorship by a compromised resolver.

### 7.5 Trust configuration

Pinning is by **key and publisher**, never by URI — a URI is a name the server
controls. The shape, in operator configuration:

```yaml
document_capabilities: [material, compute]
instruction_sources:
  - uri: "instruction://ins_42"
    publisher: "https://instruction.md/pub/acme"
    author_keys: [/etc/keys/acme-author.pem]
    delivery_keys: [/etc/keys/delivery.pem]
    max_capabilities: [material]
    freshness: 15m
```

This configuration is operator surface and MUST be unreachable from `!config`.

### 7.6 Verification, in order

1. Read the front-matter version; refuse an unimplemented version (§3.3
   rule 8) and an unknown sigiled kind (§3.3 rule 2).
2. Verify the delivery signature over the received bytes against a pinned
   delivery key: `typ` is `delivery`, `aud` names this reader, `exp` has not
   passed, and the recomputed digest of the received bytes equals `digest`.
   Any mismatch ⇒ refuse.
3. Take the manifest and the embedded author signature from the delivery
   claims. Verify the author signature against a pinned key for its `pub`:
   `typ` is `author`, `doc` and `version` equal the delivery's, `digest`
   equals `manifest.authored.digest`, and `exp` has not passed. An unpinned
   publisher is not a weaker trust level — it is a refusal.
4. Effective families = grant ∩ `max_capabilities` ∩ author-attested ∩
   delivery-attested.
5. Any block whose family exceeds effective ⇒ refuse the document whole. No
   partial load.
6. Apply the §7.8 floor.
7. Check revocation freshness (§7.7); stale past deadline ⇒ no new work.
8. Recompute the trifecta; widening refuses (§6). Apply at a quiesce boundary;
   run §5.5 lifecycle for departed blocks.

Failure at any step is **refuse, never degrade**. A failed signature check
MUST NOT reach any weaker path meant for unsigned advisory content, or an
attacker strips the signature to obtain it.

### 7.7 Revocation — the half signing cannot do

1. **Authorization is current membership in the caller's effective set**,
   re-read on an interval bounded by `freshness`. `compute` and `infra` MUST
   re-check; other classes SHOULD.
2. **Only an affirmative signal changes state** (§5.5 rule 5). A failed read
   is staleness; past the deadline, refuse new work and let live work follow
   §5.5.
3. **On revocation:** no new work; live work follows §5.5; the runtime
   triggers local retraction of derived state. The control plane revokes
   documents; the runtime retracts what they caused.
4. **Offline revocations are honored at reconnect.** A full reconcile
   converges to the current effective set and runs retraction for anything
   that left.
5. Revocation is **per principal**. Absence from one caller's effective set
   says nothing about another's.

### 7.8 Hard floor

`compose` and `identity` are **never admissible in a document that arrived
over the wire**, signed or not. A signature over a remote
privilege-management channel establishes whose fault it was, not that it was
safe. Operator surface only.

### 7.9 What this does not protect against

- **Delivery-key compromise** ⇒ arbitrary *resolutions* of authored documents,
  bounded by the author attestation's ceiling and detectable by manifest
  audit. This is the cost of per-reader resolution, and why the author
  signature ships first.
- **Author-key compromise** ⇒ full compromise within the attested ceiling,
  bounded only by `max_capabilities` and §7.8.
- **A valid signature over hostile prose is still hostile prose.** Signing is
  provenance, not safety; approval, provenance envelopes and the trifecta
  check stay load-bearing.
- **The manifest proves determinism, not benevolence.** A resolver that
  consistently substitutes a hostile value produces a consistent manifest.
  Trusted-inputs-only constrains that, and it is enforced by the resolver,
  not the verifier.

## 8. A complete example

A support agent, defined end to end. Every form of §4 appears at least
once, as does every position a reference can take (§3.4). Line comments
(`←`) are annotations, not part of the document, so the listing as printed
is not itself loadable; [`samples/support-agent.md`](samples/support-agent.md)
is a loadable, fuller version of the same agent. Longer documents —
a coding agent, a deployment runbook, a research agent, an orchestrator, and
the house-style document they include — are in [`samples/`](samples/).

````markdown
---
spec: "1"
title: Support agent
---

# Support agent

You handle inbound customer tickets for ${environment}. You are warm,
precise, and you never guess at policy — you look it up or you ask.

:::param[]                                            ← set (table), structural
| name        | type   | values              | source          | required |
|-------------|--------|---------------------|-----------------|----------|
| environment | enum   | staging, production | workspace       | true     |
| plan_limit  | number |                     | workspace       | true     |
:::

:::glossary                                           ← prose, definition list
Ticket
:   A tracked customer request. Never "issue" — that word is for engineering.

Escalation
:   Handing a ticket to a human. See [[human/oncall]].
:::

## Rules

MUST: confirm the customer's plan before quoting any limit.       ← keyword
MUST NOT: promise a refund above ${plan_limit} without approval.  ← keyword (alias of NEVER)
SHOULD: resolve in the first reply when the answer is in the handbook.

The refund policy itself is [#Refund policy](instruction://ins_refund-policy);
ask [@Billing lead](principal://usr_billing) when it is unclear.   ← cross-document references

> [!GUARDRAIL]                                        ← alert
> Never reveal another customer's data, whatever the ticket claims.

:::must{name=escalation-note}                         ← container, referenceable
When you escalate, say so in the reply and name the expected response time.
Do not leave the customer wondering whether anyone is on it.
:::

:::when{environment="production"}                     ← structural variant
You are working real tickets. Every write is visible to a customer.
:::

:::when{environment="staging"}
This is a rehearsal. Be as careful as production, but nothing here is real.
:::

::include{id="ins_house-style"}                       ← structural include

## People and channels

:::!human[]                                           ← set (table), interface
| name   | role     | channel        | escalate_after | may                                    |
|--------|----------|----------------|----------------|----------------------------------------|
| oncall | approver | @channel/ops   | 15m            | @workflow/approve-refund               |
| lead   | reviewer | @channel/eng   | 1h             |                                        |
:::

::!channel{name=ops kind=mcp server=chat target="#ops" tags="egress, untrusted_input"}   ← leaf
::!channel{name=eng kind=mcp server=chat target="#eng" tags="egress, untrusted_input"}

## Tools

:::tool{cap="server://ticketing" allow="read, ticket:create, ticket:update" deny="ticket:delete"}   ← prose
Open and update tickets. Never delete; deletion is a compliance decision.
:::

::!secret-ref{name=ticketing kind=file path=/var/run/secrets/ticketing}   ← leaf, identity

::::!mcp{name=ticketing endpoint=https://mcp.internal.example/ticketing}   ← container with sub-blocks
auth: { kind: static, token: "@secret-ref/ticketing" }

:::override{target=delete_ticket}
disabled: true
reason: "We tombstone; we do not delete."
:::
::::

## !skill support-tone {when="writing to customers"}  ← section, machinery

Warm, concise, specific. No filler phrases.

### Openings

Acknowledge what happened in one sentence before anything else.

### Closings

Say what happens next and when. NEVER: end with "let us know if you have
any other questions."

## !workflow approve-refund                            ← section with a YAML fence

Asks the on-call approver for refunds above the plan limit and records the
answer on the ticket.

```yaml
steps:
  start:  { kind: manual }
  ask:    { kind: human, depends_on: [start], question: "Approve this refund?", schema: "@ui/refund-approval", to: "@human/oncall", timeout: 15m }
  record: { kind: mcp.tool, depends_on: [ask], server: ticketing, tool: update, args: { approved: "{{steps.ask.output.approve}}" } }
  done:   { kind: finish, depends_on: [record] }
```

::::!ui{name=refund-approval kind=card}               ← container with sub-blocks
:::schema
type: object
properties:
  amount:  { type: number, title: "Refund amount" }
  approve: { type: boolean, title: "Approve" }
required: [amount, approve]
:::
:::preview
┌─ Approve refund? ───────────┐
│ Refund amount: 240          │
│ [ ] Approve                 │
└─────────────────────────────┘
:::
::::

:::context{title="Ticket lifecycle"}                  ← prose reference
A ticket is `open`, then `triaged`, then `resolved` or `escalated`.
Only a human moves a ticket to `resolved`.
:::

:::example{title="A good escalation reply"}           ← prose example
I've handed this to our on-call engineer, who will reply here within
fifteen minutes. I've noted that the outage began around 09:10 your time.
:::

#refunds #support-tier-1                              ← tags
````

**Delivered** to a reader in `production` with `plan_limit = 500`, and the
`interface` and `identity` grants in place:

```markdown
# Support agent

You handle inbound customer tickets for production. You are warm,
precise, and you never guess at policy — you look it up or you ask.

**Ticket** — A tracked customer request. Never "issue" — that word is for engineering.
**Escalation** — Handing a ticket to a human. See oncall.

## Rules

**MUST:** confirm the customer's plan before quoting any limit.
**NEVER:** promise a refund above 500 without approval.
**SHOULD:** resolve in the first reply when the answer is in the handbook.

The refund policy itself is [#Refund policy](instruction://ins_refund-policy);
ask [@Billing lead](principal://usr_billing) when it is unclear.

**GUARDRAIL:** Never reveal another customer's data, whatever the ticket claims.

**MUST:** When you escalate, say so in the reply and name the expected response time.
Do not leave the customer wondering whether anyone is on it.

You are working real tickets. Every write is visible to a customer.

<!-- the house-style document, resolved for this reader, is inlined here -->

## People and channels

[2 human roles are declared: oncall, lead]

[channel "ops" is available for #ops]
[channel "eng" is available for #eng]

## Tools

**Tool — Ticketing** (`server://ticketing`) — allowed: read, ticket:create, ticket:update; denied: ticket:delete
Open and update tickets. Never delete; deletion is a compliance decision.

[mcp server "ticketing" is connected; its tools are available]

[skill "support-tone" is available — reference it as @skill/support-tone]

[workflow "approve-refund" is loaded and runs autonomously]

<reference title="Ticket lifecycle">
A ticket is `open`, then `triaged`, then `resolved` or `escalated`.
Only a human moves a ticket to `resolved`.
</reference>

**EXAMPLE — A good escalation reply:**
I've handed this to our on-call engineer, who will reply here within
fifteen minutes. I've noted that the outage began around 09:10 your time.

#refunds #support-tier-1
```

The HTML comment stands in for the inlined house-style document
([`samples/house-style.md`](samples/house-style.md), resolved for this
reader); the comment itself is not delivered.

Note what is absent: the parameters, the staging variant, the `!ui` card
(it is for the human's client), the workflow's YAML, the skill's text (it is
delivered when the skill is invoked, not up front), and every fence. Note what
is present: every rule, every fact, every link, every example, and one line
for every piece of machinery — the model knows what it has without paying tokens for
how it is built.

**Unrendered**, in a viewer that knows nothing of this specification, the
same document shows: a title and prose; a table of parameters; a definition
list; bold rules, two links and a labeled quote; two fenced regions whose
first lines say what they are conditions for; a `::include` pointer; a table
of people; two `::!channel` lines; a fenced tool policy with its prose; a
`::!secret-ref` line; a fenced server block; two headings that begin with
`!`, followed by their prose and a YAML code block; a fenced card with a
schema and an ASCII preview; a fenced reference; a fenced example; two tags. Nothing is hidden, nothing is
misrepresented, and every sentence of guidance is where the author put it.

## 9. Machine-readable schema

The registry in §5 is published as data, so that a validator in any language
can be driven from one file rather than transcribed from prose:

**`instruction.schema.json`** — a JSON Schema, draft 2020-12 [JSONSchema].

It validates the **block tree** — the JSON a parser emits from a document —
not the Markdown itself. JSON Schema cannot parse Markdown, and this
specification does not pretend otherwise. The pipeline is:

```
Markdown ──(parse, using x-grammar)──▶ block tree ──(JSON Schema)──▶ structurally valid
                                                   ──(x-semantic-rules, in code)──▶ conforming
```

### 9.1 The block tree

A parser emits one object per document. Abridged, for the document of §8:

```json
{
  "spec": "1",
  "frontMatter": { "title": "Support agent" },
  "blocks": [
    { "kind": "must", "sigil": false, "form": "keyword", "line": 28, "attrs": {},
      "body": { "type": "markdown", "text": "confirm the customer's plan before quoting any limit." } },
    { "kind": "human", "sigil": true, "form": "set", "line": 55, "attrs": {},
      "members": [
        { "kind": "human", "sigil": true, "form": "member", "line": 58,
          "attrs": { "name": "oncall", "role": "approver", "channel": "@channel/ops",
                     "escalate_after": "15m", "may": ["@workflow/approve-refund"] } }
      ] },
    { "kind": "mcp", "sigil": true, "form": "container", "line": 73,
      "attrs": { "name": "ticketing", "endpoint": "https://mcp.internal.example/ticketing" },
      "body": { "type": "yaml", "text": "auth: …" },
      "children": [
        { "kind": "override", "sigil": false, "form": "container", "line": 76,
          "attrs": { "target": "delete_ticket" }, "body": { "type": "yaml", "text": "disabled: true" } }
      ] }
  ]
}
```

| Field | Meaning |
|---|---|
| `kind` | the kind name, without sigil |
| `sigil` | whether the block was written with `!` — must agree with the kind's disposition |
| `form` | `container` `leaf` `set` `section` `keyword` `alert`, or `member` for one entry of a set |
| `line` | 1-based line of the opening fence, heading, or keyword |
| `attrs` | the attribute list, **normalized**: keys lower-cased, flags as `true`, multi-valued attributes split on commas into arrays, quoted values unescaped |
| `body` | `{ type, text }` — `type` is one of `none` `markdown` `yaml` `code` `table` `deflist` `text`; tables carry parsed `rows`, definition lists parsed `entries`, code its `lang` |
| `children` | blocks nested inside this one by fence containment, sub-blocks included |
| `members` | set form only: one block per row or entry, each with `form: "member"` |

A section-form block of a YAML-bodied kind carries the section's prose as
`attrs.description` and the fenced definition as its `body` (§4.4 rule 6).

### 9.2 What the schema enforces

- the kind set, per disposition, and that `sigil` matches the disposition;
- per kind: the attribute schema — which attributes exist, their types,
  enumerations, which are multi-valued, which are required; unknown
  attributes are rejected;
- per kind: which forms are accepted;
- `name` required on every non-set form of a kind with identity, and on
  every member of a set;
- which sub-block kinds may appear under which parent;
- a set has members and only a set has members;
- the front-matter shape, with unknown keys permitted.

### 9.3 What the schema carries as data

JSON Schema permits `x-` keywords, which validators ignore and tools may
read. The file carries, at the top level, `x-registry` — the machinery,
prose and structural name sets; sub-blocks and their parents; families and
grants; the keyword and alias table; the inline sigils and their schemes; the
forms — and `x-grammar`, the lexical rules of §3.2 and §4 as regular
expressions that use no lookbehind and compile unchanged in every mainstream
engine. Each kind's entry carries `x-disposition`, `x-family`, `x-grant`,
`x-forms`, `x-body`, `x-identity`, `x-noun` and `x-nouns` — the display noun,
singular and plural, used in acknowledgement lines — and `x-acknowledgement`
— the template for its delivery line.

A parser that reads `x-grammar` and `x-registry` from the file needs no
hard-coded knowledge of this specification's vocabulary. That is the point:
when version 2 adds a kind, it adds an entry, and a validator that reads the
file learns it.

### 9.4 What the schema cannot express

JSON Schema validates one value at a time; it cannot see across blocks or
outside the document. The file therefore also carries **`x-semantic-rules`**:
the rules a conforming validator MUST implement in code, each naming the
section it comes from. They are the rules of §3.3, §3.4, §4 and §6 that
involve more than one block or a decision about the document's context —
identity uniqueness, reference resolution and acyclicity, the reserved-bare
and sigiled-prose guards, sub-block placement, grants, the pinning rules,
fence recognition at column 0, code-fence suspension, keyword scope, and
version skew.

The list is normative. A validator that passes the schema and implements
every listed rule conforms to this specification's *structural* requirements;
delivery (§3.5), lifecycle (§5.5) and signing (§7) are behaviour, not
structure, and are tested by behaviour.

## 10. Security considerations

This specification treats a document that carries machinery as a program,
and its delivery over a network as a supply chain. The considerations below
collect in one place what the body of the document establishes; each cites
the rule that carries it.

- **Surfaces.** Blocks are recognized on the operator surface only (§3.3
  rule 10). Conversation text, tool results, retrieved knowledge and model
  output are never parsed for blocks. Parameter values are read from trusted
  sources only and are inserted as data, never re-parsed (§3.5, §5.2).
- **Silent demotion.** The two ways configuration could silently become
  text — a forgotten sigil, and a reader that predates a construct — are
  both refusals (§3.3 rules 3 and 8), and machinery is self-marking in a
  renderer unaware of this specification (§3.3 rule 1).
- **Capability.** A document never grants itself anything: families are
  admitted by the operator (§6), `!config` is allow-listed (§5.3), a
  signature caps and never grants (§7.2), and `compose` and `identity` are
  never admissible over the wire (§7.8).
- **Secrets.** A literal credential anywhere in a document is a refusal; a
  document names where a secret comes from through `!secret-ref` and never
  its value (§5.3).
- **Pinning.** Images are digest-pinned, remote assets carry a `sha256`, and
  trust configuration pins keys and publishers rather than URIs (§5.3,
  §7.5).
- **Isolation.** `!function` is a declaration dispatched to a declared
  `!runtime`; the reader never interprets code, `network: any` is refused,
  and `!file` is path-confined (§5.3).
- **The trifecta.** Blocks carry `untrusted_input`, `sensitive` and `egress`
  tags; a runtime refuses to assemble all three silently, and a live update
  that widens the computation is refused (§5.5 rule 4, §6 rule 5).
- **Overrides.** An `override` may only narrow: add a tag, disable a tool,
  tighten an enumeration (§5.3).
- **Per-reader resolution.** A resolver chooses bytes per reader; the
  resolution manifest makes that choice attested and auditable, and
  `variants.dropped` is required so that withheld content is visible as
  withheld (§7.4).
- **Revocation.** A signature establishes authenticity and a ceiling, not
  continued authorization. Authorization is current membership in the
  effective set, re-read within `freshness`; a failed read is staleness, not
  revocation (§5.5 rule 5, §7.7).
- **Residual risk.** §7.9 lists what signing does not protect against. A
  valid signature over hostile prose is still hostile prose.

## 11. Media type

An instruction is Markdown and is served as `text/markdown` [RFC7763] with
the `variant` parameter [RFC7764] set to `instruction`:

```
Content-Type: text/markdown; charset=UTF-8; variant=instruction
```

The identity of the format is this media type together with the `spec`
version declared in front matter (§3.1). `instruction.md` as a *filename* is
a convention, not the identity; a served document has no filename.
Registration of the `instruction` variant in the IANA "Markdown Variants"
registry is intended. Until it is registered, the parameter value is used as
specified here.

## 12. References

### 12.1 Normative references

- **[RFC2119]** Bradner, S., "Key words for use in RFCs to Indicate
  Requirement Levels", BCP 14, RFC 2119, March 1997.
- **[RFC8174]** Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119
  Key Words", BCP 14, RFC 8174, May 2017.
- **[CommonMark]** MacFarlane, J., "CommonMark Spec", version 0.31.2,
  <https://spec.commonmark.org/0.31.2/>.
- **[GFM]** "GitHub Flavored Markdown Spec", version 0.29-gfm, section
  "Tables (extension)", <https://github.github.com/gfm/>.
- **[YAML]** "YAML Ain't Markup Language (YAML™) version 1.2", revision
  1.2.2, <https://yaml.org/spec/1.2.2/>.
- **[RFC8259]** Bray, T., Ed., "The JavaScript Object Notation (JSON) Data
  Interchange Format", STD 90, RFC 8259, December 2017.
- **[JSONSchema]** Wright, A., Andrews, H., Hutton, B., and G. Dennis, "JSON
  Schema: A Media Type for Describing JSON Documents", draft 2020-12,
  <https://json-schema.org/draft/2020-12/>.
- **[RFC3986]** Berners-Lee, T., Fielding, R., and L. Masinter, "Uniform
  Resource Identifier (URI): Generic Syntax", STD 66, RFC 3986, January 2005.
- **[RFC7515]** Jones, M., Bradley, J., and N. Sakimura, "JSON Web Signature
  (JWS)", RFC 7515, May 2015.
- **[RFC8037]** Liusvaara, I., "CFRG Elliptic Curve Diffie-Hellman (ECDH)
  and Signatures in JSON Object Signing and Encryption (JOSE)", RFC 8037,
  January 2017.
- **[FIPS180-4]** National Institute of Standards and Technology, "Secure
  Hash Standard (SHS)", FIPS PUB 180-4, August 2015.
- **[RFC7763]** Leonard, S., "The text/markdown Media Type", RFC 7763,
  March 2016.
- **[RFC7764]** Leonard, S., "Guidance on Markdown: Design Philosophies,
  Stability Strategies, and Select Registrations", RFC 7764, March 2016.

### 12.2 Informative references

- **[RFC8032]** Josefsson, S. and I. Liusvaara, "Edwards-Curve Digital
  Signature Algorithm (EdDSA)", RFC 8032, January 2017.
- **[RFC3552]** Rescorla, E. and B. Korver, "Guidelines for Writing RFC Text
  on Security Considerations", BCP 72, RFC 3552, July 2003.
- **[RFC6838]** Freed, N., Klensin, J., and T. Hansen, "Media Type
  Specifications and Registration Procedures", BCP 13, RFC 6838, January
  2013.

## Appendix A — Delivery reference

What each authored construct becomes in the delivered text.

| Authored | Delivered |
|---|---|
| front matter | nothing |
| `:::must` … / `MUST: …` / `> [!MUST]` | `**MUST:** …` — the label prefixed to the first body line; further lines unchanged |
| `:::should` / `:::never` / `:::guardrail` / `:::note` / `:::tip` / `:::warning` / `:::caution` / `:::important` | `**SHOULD:**` / `**NEVER:**` / `**GUARDRAIL:**` / `**NOTE:**` / `**TIP:**` / `**WARNING:**` / `**CAUTION:**` / `**IMPORTANT:**` + body |
| `MUST NOT:` / `INFO:` | `**NEVER:**` / `**NOTE:**` |
| `:::example{title=T}` | `**EXAMPLE — T:**` on its own line, then the body verbatim |
| `:::context{title=T}` | `<reference title="T">` body `</reference>` |
| `:::form{title=T}` | `**Inputs to collect — T**` on its own line, then one list item per parameter referenced in the body (§5.1); the body's text is not delivered |
| `:::tool{cap allow deny}` | `**Tool — Label** (\`cap\`) — allowed: …; denied: …` on its own line, then the body |
| `:::glossary` | `**Term** — definition`, one line per term |
| `:::when{…}` kept | body, unwrapped, in place |
| `:::when{…}` dropped | nothing; recorded in the manifest |
| `::include{…}` | the included document, resolved for this reader |
| `::param` / `:::param[]` | nothing |
| `${name}` | the value, as plain text |
| `[[kind/name]]` / `[Label](#kind/name)` | `name` / `Label` |
| `[#L](instruction://…)` etc. | the link, unchanged |
| `#tag` | unchanged |
| `:::!kind{name=x}` (any machinery form) | `[kind "x" …]` — one line per block, per §5.3 |
| `:::!kind[]` with N members | `[N <nouns> are declared: a, b, c]` — one line; the noun is the kind's `x-nouns`; nothing when the kind has no acknowledgement |
| `## !kind x` + section | the same one line; the section is gone |
| sub-blocks | nothing of their own; folded into the parent's line |
| unknown bare `:::foo` | body, as prose; the fences removed |
| blank lines | preserved; a run of several collapses to one |

## Appendix B — Refusals

Every refusal names the line, the construct, and what to write instead. The
catalogue, so that implementations agree on what a document's author sees:

| Condition | Message shape |
|---|---|
| unknown sigiled kind | `line N: unknown machinery kind "x" — this reader implements version 1 (known: workflow, skill, …)` |
| sigiled prose kind | `line N: "must" is a prose kind — did you mean :::must` |
| bare machinery kind | `line N: "workflow" is a machinery kind — did you mean :::!workflow` |
| unclosed fence | `line N: :::!skill is never closed (expected a line of ≥3 colons)` |
| text after close fence | `line N: a closing fence must be alone on its line` |
| malformed attribute list | `line N: attributes: expected key=value, found "on call" — quote values with spaces` |
| duplicate attribute key | `line N: attribute "name" is repeated` |
| `#id` / `.class` | `line N: "#oncall" is not an attribute — identity is name=oncall` |
| duplicate identity | `line N: duplicate human/oncall (first declared at line M)` |
| dangling reference | `line N: @function/lint does not resolve — no function named "lint"` |
| reference cycle | `line N: reference cycle: test/a → function/b → test/a` |
| body required | `line N: workflow requires a body (its steps) — use :::!workflow` |
| body forbidden | `line N: include takes no body` |
| set body mixed or unrecognized | `line N: a set body must be a table or a definition list` |
| set row without name | `line N: row 3 has no name — every member of human[] needs one` |
| unknown column | `line N: "channel_id" is not an attribute of human` |
| redundant set | `line N: glossary is already a list — write :::glossary` |
| sub-block out of place | `line N: case is valid only inside a test` |
| section for prose kind | *(not a refusal — a bare heading is prose)* |
| section body without its fence | `line N: a workflow section must contain exactly one fenced yaml block` |
| ungranted family | `line N: :::!runtime needs the "compute" grant — add it to document_capabilities` |
| self-grant | `line N: !config may not write document_capabilities` |
| mutable image tag | `line N: image "py311:latest" is not digest-pinned` |
| unpinned remote asset | `line N: remote src requires sha256` |
| literal credential | `line N: a literal credential is never allowed — use a secret-ref` |
| widening override | `line N: override may not remove tag "sensitive" — overrides only narrow` |
| unsupported isolation | `line N: this reader does not support isolation=process` |
| unimplemented version | `front matter: spec "2" is not implemented by this reader` |
| non-integer version | `front matter: spec "1.0" is not a version — versions are integers` |
| signature `typ` mismatch | `signature: expected typ "author", found "delivery"` |
| audience mismatch | `delivery: aud "principal://usr_9" is not this reader` |
| digest mismatch | `delivery: digest does not match the received bytes` |
| manifest without `variants.dropped` | `manifest: variants.dropped is required (§7.4 rule 5)` |
| unpinned publisher | `publisher "https://…" is not pinned in instruction_sources` |
| delivery ceiling exceeds author's | `delivery: capabilities [compute] exceed the author attestation [material]` |
| dangling on live update | `update refused: workflow/deploy still references human/oncall, which the update removes` |
| trifecta widening on update | `update refused: it would add untrusted_input alongside live egress tools` |
