# The Instruction Document Specification

**Status:** draft-1 — content-complete; not yet stable.
**Publisher:** instruction.md.
**License:** CC BY 4.0.
**Identity:** the media type `text/markdown; variant=instruction-document`,
plus a version. `instruction.md` as a *filename* is a convention, not the
identity — a served document has no filename.

---

## 1. Purpose

An **instruction document** is one Markdown file that fully defines an AI
agent: the prose that instructs it, and the machinery that equips it —
workflows, tools, code, files, runtimes, knowledge, endpoints, people,
identity. It is readable top to bottom by a person, loadable by a runtime, and
governable — versioned, diffed, reviewed, signed, served, revoked — by a
control plane.

Two consumer roles are first-class and equal:

- a **runtime** extracts the machinery and *becomes* the agent;
- a **control plane** stores, versions, diffs, resolves, serves, signs and
  revokes documents *without executing them*.

Every rule in this document is written so that both roles can implement it. A
construct that only a runtime can check does not belong in the format.

## 2. Terminology

| Term | Meaning |
|---|---|
| document | UTF-8 Markdown: optional front matter, then interleaved prose and blocks |
| front matter | leading YAML metadata; always stripped from delivery |
| kind | a named unit of meaning — `must`, `human`, `workflow` — with one disposition |
| block | one occurrence of a kind in a document, in any of the forms of §4 |
| form | a way of writing a block: container, leaf, set, section, keyword (§4) |
| **disposition** | per kind: **prose** (degrades into delivered text) · **machinery** (stripped; folds into configuration) · **structural** (resolved away) |
| family | a named group of machinery kinds; the unit of capability granting (§6) |
| grant | operator-side admission of a family; never made in-document |
| delivery | the text a model actually receives, after resolution and degradation |
| operator surface | text the operator authored and the runtime read at startup |
| trifecta | the combination of untrusted input, sensitive access and egress in one agent — the shape of an exfiltration path; blocks carry these tags and the runtime refuses to assemble all three silently |

**Disposition is the foundation.** The same fence syntax can carry text meant
for the model and configuration meant for the runtime. Disposition makes both
true at once, and it decides what happens to a name nobody recognizes (§3.3).

## 3. Document model

### 3.1 Front matter

A document MAY declare its specification version in YAML front matter; a
reader refuses a version it does not implement. **Absent front matter means
version 1**, which is presently the only version.

The format is a **strict superset of prose**. An unknown bare kind is inert
punctuation (§3.3 rule 2), so a plain prose file — with or without `:::`
fences this specification has never heard of — is a valid document and loses
nothing. Only the `!` sigil and the reserved bare names carry obligations.
Adoption costs nothing.

Front matter may also carry `id`, `version`, parameter declarations (§5.4),
and signing metadata (§7). Front matter never reaches the model. The version
lives in the document, not in the reader's configuration: the same bytes must
mean the same thing to every reader.

```yaml
---
spec: "1"
id: instruction://ins_42
version: ver_01K003
parameters:
  - { name: environment, type: enum, values: [staging, production], source: workspace }
---
```

### 3.2 Grammar

```
document    := front-matter? (prose | block)*
block       := container | leaf | set | section | keyword          ; §4
container   := open-fence attrs? "\n" body close-fence
open-fence  := ":"{n} sigil? kind                                  ; n ≥ 3
close-fence := ":"{m}                                              ; m ≥ n, alone on its line
leaf        := "::" sigil? kind attrs?                             ; exactly two colons
set         := open-fence "[]" … close-fence                       ; open-fence := ":"{n} sigil? kind "[]"
sigil       := "!"                                                 ; marks machinery
kind        := [A-Za-z][A-Za-z0-9_-]*
body        := (prose | block | code-fence)*                       ; inner blocks use shorter fences
attrs       := "{" (key ("=" value)?)* "}"
key         := [A-Za-z][A-Za-z0-9_.-]*
value       := bare-word | '"' quoted '"'                          ; bare runs to whitespace or "}"
```

Attribute rules:

- `key=value` with a bare value runs to the next whitespace or `}`.
- `key="…"` is quoted; inside, `\"` and `\\` are the only escapes.
- A bare `key` with no value is a flag, equivalent to `key="true"`.
- Keys are case-insensitive on match and MUST NOT repeat within one list.
- `#id` and `.class` shorthands are **not** part of this grammar. Identity is
  the `name` attribute; classification is the kind. Both are explicit.

### 3.3 Rules

1. **Machinery is lexically namespaced.** `:::!workflow` is machinery; bare
   `:::note` is prose. The sigil was chosen on evidence: `:::!kind` does not
   parse as a directive in existing Markdown tooling, so an unaware renderer
   shows the fence itself and machinery announces itself as machinery. A
   prefix that *does* parse gets its markers consumed and its body rendered as
   prose — configuration silently laundered into text, the inverse of the
   degradation contract. The property this buys, as a property of the lexeme
   rather than a rule anyone has to enforce: **machinery never masquerades as
   prose in an unaware renderer.**
2. **Unknown-name policy is per disposition.** An unknown sigiled kind
   (`:::!foo`) fails **closed**: the document is refused with an error naming
   the known machinery set, so a mistyped `:::!worfklow` cannot silently become
   text. An unknown bare kind (`:::foo`) fails **open**: it is inert
   punctuation and the prose inside it is preserved, so the degradation
   contract holds. A sigiled kind that shadows a known prose name (`:::!must`)
   fails closed with "did you mean `:::must`".
3. **Reserved-bare guard, version-scoped.** A bare kind that shadows a
   machinery name — `:::workflow` without the sigil — fails **closed** with
   "did you mean `:::!workflow`"; otherwise a forgotten sigil demotes
   configuration to prose one keystroke from correct. The reserved set is the
   machinery set of *the document's declared version*, not the reader's: a
   bare prose name legal at version 1 stays legal under every later reader, or
   registry growth would retroactively invalidate documents. Consequently
   this specification publishes its machinery-name set per version (§5).
4. **Nesting is fence-length containment.** A block opened with `::::` is
   closed only by a run of four or more colons, so it may contain `:::`
   blocks. This is the same convention as CommonMark code fences: the longer
   fence contains the shorter. A `verbatim` attribute quotes a body without
   parsing it.
5. **Colon-fence scanning is suspended inside fenced code.** A function body,
   or an embedded example document, never terminates its container.
6. **Degradation contract** (prose disposition). Paste the document into a
   Markdown viewer that knows nothing of this specification and it must still
   read as correct, complete guidance. A construct that hides prose when
   unrendered is rejected from the prose vocabulary.
7. **Acknowledgement contract** (machinery disposition). A machinery block
   delivers exactly one provenance line — `[workflow "drain" is loaded and runs
   autonomously]` — and never its body. Prose degrades in; machinery
   acknowledges out; between the two, delivery is fully specified.
8. **Version-skew refusal.** A reader MUST refuse a document that declares a
   version it does not implement, and MUST refuse lexical markers of a newer
   version it does not recognize. The refusal keys on *evidence* of a newer
   version, not on the mere presence of front matter. This rule is written for
   versions that do not exist yet, and it is not speculative: a reader that
   predates a marker parses it as prose, and the configuration it carried
   vanishes without a diagnostic. Silence is the failure this rule prevents.
9. **Block identity.** `name` is a block's identity within the document and is
   **unique per kind**; `kind/name` is the qualified form. A duplicate
   `kind/name` is refused. Reference resolution (§3.4) is undefined without
   this rule.

### 3.4 References

**Cross-document references** are ordinary Markdown links whose label begins
with a sigil and whose target is a URI naming the serving authority:

```
[#Coding standards](instruction://ins_42)     another instruction
[@On-call](principal://usr_7)                  a person or agent
[&Ticketing](server://ticketing)               a capability: server, skill, model, service, sandbox
```

They degrade to links — the one form that loses nothing anywhere.

**Local references** name a block in the same document. In attribute position
the form is `@kind/name`, **always qualified** — resolution must never depend
on the schema of the attribute it sits in, so that a diff tool without the
registry can still resolve. In prose the form is a link to a fragment, or the
wiki-link shorthand for it (§4.6):

```
target=@function/lint                          in attributes
[the linter](#function/lint)                   in prose
[[function/lint]]                              in prose, shorthand
```

Local references are **statically acyclic**, checked at load; a cycle is
refused. Cross-document references are **cycle-guarded at resolution**, with
normative depth and fan-out caps — static acyclicity across documents you do
not hold is not achievable and is not claimed.

In YAML bodies a reference MUST be quoted — `file: "@file/pyproject"` — because
`@` opens a reserved indicator in YAML 1.2 and implementations diverge on the
unquoted form. **Quoting of references in bodies is semantically load-bearing;
formatters MUST preserve it.** In prose, `@` belongs to the person/agent sigil;
positions are disjoint, and editors MUST NOT rewrite the interior of an
attribute list.

### 3.5 Delivery and degradation

What the model sees is a declared property of each kind — its disposition —
not a hard-coded table. Machinery renders as one acknowledgement line; prose
degrades to labeled text; structural resolves away.

Machinery bodies are **never silently AI-edited**. An assistant's proposed
edit to a machinery body MUST surface as a separately confirmed diff and MUST
NOT be bundled into a prose-edit hunk. The property is *no incidental
rewrite*, not *never*: a user may still ask for the edit deliberately.

Tables inside data-bearing blocks: **cell content is normative, layout is
not**. A formatter that preserves cells preserves semantics.

### 3.6 Control-plane duties

A conforming control plane parses without executing; diffs **block-granular
for review and attribution, line-granular for merge**; attributes every block
to an author and a version; resolves per reader deterministically and
**attests the resolution** (§7.3); and **serves revocation** (§7.6).

## 4. Forms — how a block is written

A **kind** is a unit of meaning. A **form** is a way of writing one. The
container fence is the general form, but it is heavy for entities that are
small, that have no body, that come in tens, or that are naturally a section
of a long document. This section defines the other forms. They are not new
kinds and not new semantics: every form maps to the same kind, with the same
disposition, family, grant, attribute schema, identity rule and lifecycle.
**A reader MUST accept every form for every kind it accepts at all**, except
where a form is restricted below.

### 4.1 Container — one instance, with a body

```markdown
:::!human{name=oncall role=approver}
reach: { channel: "@channel/ops", escalate_after: 15m }
:::
```

The general form. Body interpretation belongs to the kind: YAML for most
machinery, Markdown for prose kinds and skills, a fenced code block for
functions.

### 4.2 Leaf — one instance, no body

```markdown
::!human{name=oncall role=approver channel=@channel/ops escalate_after=15m}
::include{id="ins_42"}
::param{name=environment type=enum values="staging,production" source=prompt}
```

Exactly two colons, one line. Everything the block needs is in its attribute
list. A leaf is valid for any kind whose body is optional; a kind that
requires a body (`!function`, `!workflow`) refuses the leaf form naming what
is missing. Unrendered, a leaf is a single visible line — self-marking, like
the container.

### 4.3 Set — many instances

The multiplicity form. A `[]` suffix on the kind declares that the block
defines a **set of instances**, one per entry of its body:

```markdown
:::!human[]
| name   | role     | channel        | escalate_after |
|--------|----------|----------------|----------------|
| oncall | approver | @channel/ops   | 15m            |
| lead   | reviewer | @channel/eng   | 1h             |
| sre    | operator | @channel/ops   | 5m             |
:::
```

The body is one of two shapes, chosen by what the entries need:

- **A table**, for instances defined by attributes. The header row names the
  attributes; each following row is one instance. Cells hold attribute values
  under §3.2's value grammar — references allowed, multi-valued cells
  comma-separated. A kind with identity requires a `name` column.
- **A definition list**, for instances defined by a body. The term is the
  instance's `name`, optionally followed by an attribute list; the definition
  is its body.

```markdown
:::!skill[]
tone {when="writing to customers"}
:   Be brief. Warm, specific, no filler. Apologize once, then resolve.

refunds
:   Never promise above the plan's limit without a human approval.
:::
```

Sub-blocks may take the set form inside their parent — a `:::case[]` table of
test vectors is the most readable way to write ten of them:

```markdown
::::!test{name=lint-works target=@function/lint}
:::case[]
| name        | given                          | expect       |
|-------------|--------------------------------|--------------|
| finds-one   | { diff: "+ // TODO: fix" }     | { count: 1 } |
| ignores-old | { diff: "- // TODO: gone" }    | { count: 0 } |
:::
::::
```

Each instance of a set is a block in every respect: it has identity, it is
addressable as `@kind/name`, and it retires individually (§5.1). A set of
machinery delivers **one** acknowledgement line naming its members; a set of
prose degrades per entry. Unrendered, a set is a table or a definition list —
both are among the best-degrading constructs Markdown has.

### 4.4 Section — one instance, whose body is a section of the document

Long entities — a skill with pages of guidance, a persona, a function with
real documentation — are naturally written as sections, not fences. A heading
whose text begins with a **sigiled** kind declares a block whose body is
everything that follows until the next heading of the same or a higher level:

```markdown
## !skill support-tone {when="writing to customers"}

Warm, concise, specific. Apologize once, then move to resolution.

### Escalation

If the customer asks for a human, hand off; see [[human/oncall]].

## Next section
```

The kind, then whitespace, then the `name`, then an optional attribute list.
Headings inside the section belong to the body (as in the example). Fences
inside are parsed normally. The section form is **machinery only** — a bare
heading is always just a heading, so `## human oncall` is prose and the
reserved-bare guard does not apply to headings. Unrendered, the section is a
heading and its text: it reads exactly as the author wrote it, and the `!`
marks it.

### 4.5 Keyword — normativity in a single line

The prose kinds `must`, `should`, `never`, `guardrail`, `note`, `tip`,
`warning`, `caution`, `important` and `example` degrade at delivery to a
labeled line — `**MUST:** Run the test suite before opening a PR.` That
delivered form is also an **authored** form. A paragraph or list item that
begins with the kind's keyword in capitals, followed by a colon, optionally
bold, *is* a block of that kind:

```markdown
MUST: Run the full test suite before opening a PR.

- **NEVER:** push to `main` directly.
- SHOULD: keep functions under forty lines.
```

A document with forty rules does not want forty fences. The keyword form
costs nothing to degrade because it is already the degraded form, and it is
how normative documents have been written for decades. Recognition is at the
start of a paragraph or list item only; `must:` in lower case or mid-sentence
is prose. The blockquote alert `> [!NOTE]` remains valid as a third spelling
of the same kinds and is normalized to the keyword form on delivery.

### 4.6 Inline — chips, tags, parameters, wiki-links

Inline forms live inside prose and are rendered by an aware editor as
**chips**: atomic, styled, resolvable. Unrendered, each is a link, a word, or
a bracketed name — all readable.

| Inline form | Meaning | Unrendered |
|---|---|---|
| `[#Label](instruction://…)` | another instruction | a link |
| `[@Label](principal://…)` `[@Label](agent://…)` | a person or agent | a link |
| `[&Label](server://…)` `skill://` `model://` `service://` `sandbox://` | a capability | a link |
| `[Label](#kind/name)` | a block in this document | a link |
| `[[kind/name]]` `[[kind/name\|Label]]` | the same, shorthand | bracketed name |
| `${name}` | a declared parameter, resolved at delivery | the placeholder |
| `#tag` | a free topic label; not a reference | a word |

The wiki-link is sugar for the fragment link and MUST resolve identically. A
sigil in a link label selects the chip type; the target decides whether it is
local (`#…`) or cross-document (a URI). Inline forms inside inline code or a
fenced code block are inert, as §3.3 rule 5 requires for fences.

The inline directive syntax `:kind[text]{attrs}` is **reserved** by this
specification and defines no kinds at version 1. Implementations MUST treat
it as prose and MUST NOT assign it meaning.

### 4.7 Equivalence and degradation across forms

| Form | Multiplicity | Body | Restricted to | Unrendered, reads as |
|---|---|---|---|---|
| container `:::kind` | one | yes | — | fenced text |
| leaf `::kind` | one | no | body-optional kinds | one visible line |
| set `:::kind[]` | many | table or definition list | — | a table / a definition list |
| section `## !kind name` | one | the section | machinery | a heading and its text |
| keyword `MUST:` | one | the line | normativity prose kinds | the same line |
| alert `> [!NOTE]` | one | the quote | normativity prose kinds | a labeled quote |
| inline | — | — | references, parameters, tags | a link or a word |

Rules that hold across all forms:

- The disposition is the kind's, never the form's. A set of machinery is
  machinery; a keyword `MUST:` is prose.
- The reserved-bare guard (§3.3 rule 3) applies wherever a kind name is
  unambiguous: after `:::`, `::`, and `[]`. It does not apply to headings or
  to keywords.
- Identity (§3.3 rule 9) is per kind across all forms: a `!human` declared as
  a leaf and another with the same name in a set are a duplicate.
- Grants (§6) and lifecycle (§5.1) are per kind. A set of `!function`s needs
  `compute` exactly as one does, and each retires on its own.

## 5. Block registry

Every kind declares: disposition, family, attribute schema, which forms it
accepts, and a lifecycle — what happens when the block disappears on a live
update.

### 5.1 Prose kinds (bare)

`must` `should` `never` `guardrail` `note` `info` `tip` `important` `warning`
`caution` `example` `context` `form` `tool` `glossary`

- The **normativity** kinds (`must` … `example`) are RFC 2119-classifiable:
  every MUST in a document is mechanically extractable for review. They accept
  the container, keyword and alert forms.
- `context` carries material that is true rather than imperative; delivered
  wrapped in `<reference>` tags. `example` shows what good output looks like.
- `form` is parameter capture: it references declared parameters and degrades
  to a labeled "inputs to collect" list — never a live form.
- `tool` pins how a referenced capability may be used, in prose with inline
  policy: `:::tool{cap="server://ticketing" allow="read, ticket:create"
  deny="ticket:delete"}`.
- `glossary` is a definition list of terms the agent must use precisely.
  Delivered as `**Term** — definition`. A glossary is the canonical use of the
  definition-list body.

### 5.2 Structural kinds (bare)

`when` `include` `param`

- `when{key="value" …}` keeps its body only for a matching delivery context
  and drops it otherwise; conditions match the same facts parameters resolve
  from. An unknown key keeps the content — a host that cannot evaluate a
  dimension keeps the guidance.
- `include{id="…"}` transcludes another document at delivery, access-checked
  against the reader, cycle- and depth-bounded. Leaf form only.
- `param` declares a parameter in the body rather than in front matter — the
  two are equivalent, and a set of parameters is more readable as a table
  than as YAML. Attributes: `name`, `type` (`string|number|boolean|enum`),
  `values`, `required`, `default`, `source` (`static|workspace|agent_attribute|prompt`),
  `description`. Leaf and set forms.

```markdown
:::param[]
| name        | type   | values              | source          | required |
|-------------|--------|---------------------|-----------------|----------|
| environment | enum   | staging, production | workspace       | true     |
| region      | string |                     | agent_attribute | false    |
:::
```

### 5.3 Machinery kinds (sigiled), by family

| Family | Kinds | Contract |
|---|---|---|
| core | `!workflow` `!skill` `!config` `!mcp` `!stream` `!tools` | what the agent runs, knows, connects to, and may call |
| material | `!file` `!data` `!media` `!asset` | bytes and values the document materializes; remote references integrity-pinned |
| knowledge | `!knowledge` `!retrieval` `!source` | retrieval policy and provenance tags; executed elsewhere |
| interface | `!endpoint` `!ui` `!human` `!channel` | listeners, render schemas with a text preview, human roles |
| identity | `!peer` `!policy` `!secret-ref` | principals, egress policy, secret *locations* — never values |
| compute | `!runtime` `!function` `!test` `!fixture` | code as declaration plus dispatch target; digest-pinned runtimes; testable |
| infra | `!git` `!volume` `!image` | mounted state and images, pinned and verifiable |
| compose | `!agent` `!override` | children inherit at most the parent's grants; override narrows only |

Notes on specific kinds:

- `!human` names a *role*, never contact details. Reachability goes through a
  `!channel`, so the document says "oncall" and the deployment decides who
  that is. Its `may` verbs bind to declared references (`@workflow/…`), never
  free strings.
- `!ui` ships a `schema` sub-block and a plain-text `preview` sub-block. The
  preview is normatively non-normative: clients render the schema first; tools
  MAY regenerate the preview.
- `!runtime` declares a portable **isolation contract** — `isolation: oci |
  process | none` — and an implementation refuses levels it does not support.
  Reader-side feature flags are not portable semantics. `image` MUST be
  digest-pinned; a mutable tag is refused by name.
- `!function` is a declaration bound to a runtime, never an interpreter. Its
  body is a fenced code block; its `signature` sub-block gives input and
  output shapes.
- `!override` is **append-only and attributed**: the server's own tool
  description is preserved verbatim and the override renders as a delimited,
  provenance-marked operator annotation beneath it. It may add tags, disable a
  tool, or tighten an enum. Description *replacement* and default changes are
  behavioural steering, not narrowing, and are refused.
- `!config` writes against an **allow-list**: grant keys, security, services,
  specification version and signing configuration are unreachable by
  construction, and the next configuration key added is unreachable by
  default. The document cannot grant itself anything.

**Sub-blocks** are valid only inside their parent, unsigiled (the parent's
fence and sigil govern them), with the parent's disposition. Their names are
scoped to the parent and **exempt from rule 9's uniqueness** — two `!test`
blocks may each carry a `case` named `happy` — and therefore they have no
document-level identity and MUST NOT be referenced. The set: `case` (in
`!test`), `signature` (in `!function`), `schema` and `preview` (in `!ui`). A
sub-block outside its parent is refused, naming the parent it needs.

### 5.4 Lifecycle — what removal means

Six general rules, then the per-kind table.

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
   *successful* effective-set read. A failed or unreachable read is
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
| `!tools` `!override` | registry decoration recomputed; the next turn sees it |
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

## 6. The trust ladder

Machinery families above the default require an explicit operator grant, held
outside the document; fail-closed; restart-only; introspectable. **Grants are
an independent set, not cumulative levels:** granting `compute` grants nothing
else, and the table's order is presentational.

| Grant | Families | Blast radius when granted |
|---|---|---|
| *(default)* | prose · structural · core machinery · `!data` · `!override` | the prompt, and configuration the runtime already accepted; `!data` never leaves the document |
| `material` | `!file` `!media` `!asset` | bytes materialize into the workspace |
| `interface` | `!endpoint` `!ui` `!human` `!channel` | listeners bind; people become addressable |
| `knowledge` | `!knowledge` `!retrieval` `!source` | **the agent's context window points at a corpus others may influence** — attacker-steered context with tools in reach; feeds the trifecta directly |
| `identity` | `!peer` `!policy` `!secret-ref` | credentials and principals become nameable |
| `compute` | `!runtime` `!function` `!test` `!fixture` | code executes, in declared isolation |
| `infra` | `!git` `!volume` `!image` | state mounts; images pull |
| `compose` | `!agent` | children carry this document's grants; the intersection is computed at document load, so templates must be statically resolvable |

Rules that make the ladder real:

1. **Fail-closed and specific.** A block whose family is not granted is a
   refusal naming the block, the line, the family and the exact grant to add.
2. **A grant is not a blank cheque.** `compute` lets a document *declare* a
   function; whether it may run still passes tool policy, egress policy and
   the trifecta check. Two independent gates.
3. **Grants are restart-only.** Widening what a document may do is never a hot
   reload; a capability an operator believes they revoked, still live in the
   running process, is the worst class of lie.
4. **The document cannot grant itself anything.** `!config` is allow-listed
   (§5.3); a served document is never a source of its own trust configuration.
5. **Content-driven trifecta widening is refused.** On a live update, if the
   re-resolved document's trifecta computation differs from the loaded one,
   the update MUST NOT apply — refuse-and-keep or refuse-and-stop, the
   operator's choice, never silently widen.

## 7. Signing, serving, revocation

### 7.0 Scope

A document carrying machinery is code, and a document delivered over a
network is a supply chain. This section specifies what a signature attests,
what it authorizes, and — separately — what keeps it authorized. Signing
establishes **authenticity and a capability ceiling**; it does not establish
**authorization**, which is §7.6. A signature is valid forever; a document
that can execute code must stop being usable the moment it stops being
sanctioned.

### 7.1 The attestation

Signatures are JWS compact serializations over a claims object.
Implementations MUST support Ed25519 and MUST domain-separate by `typ`.

```json
{ "spec": "instruction-document/1",
  "typ": "author",
  "doc": "instruction://ins_42",
  "version": "ver_01K003",
  "digest": "sha256:…",
  "capabilities": ["material", "compute"],
  "pub": "https://instruction.md/pub/acme",
  "iat": 1757000000, "exp": 1788536000 }
```

**A signature caps; it MUST NOT grant.** Effective families = operator grant ∩
per-source ceiling ∩ attested `capabilities`. A document attested for
`compute` on a runtime that granted only `material` gets `material`.
`capabilities` is the maximum the publisher stands behind, not what the
document uses; a block outside its attestation refuses the document whole.

### 7.2 Two signatures, and why both

- **Author signature** (`typ: "author"`) — an **offline** key over the
  *authored* version. Attests who wrote it and what they stand behind.
  Survives compromise of the control plane, which is the only reason it
  exists.
- **Delivery signature** (`typ: "delivery"`) — an **online service key**, in
  the serving path, over the *delivered* bytes, the audience, the resolution
  manifest (§7.3) and a reference to the author signature. Attests what was
  actually sent, and to whom.

The online key is structurally weaker than the offline one, and this
specification says so rather than letting deployments discover it. `compute`
and `infra` blocks MUST require both; where only one is available it MUST be
the author signature.

The verification chain must be implemented as stated: the delivery signature
covers the manifest; the manifest names the authored version and its digest;
the author signature covers that digest. A verifier that skips the manifest
cannot check authorship at all.

### 7.3 The resolution manifest

Per-reader resolution means the server chooses bytes. Without an attested
account of *how*, that is an unbounded content-injection channel wearing a
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

### 7.4 Trust configuration

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

### 7.5 Verification, in order

1. Read the front-matter version; refuse an unimplemented version (§3.1) and
   unrecognized markers of a newer one (§3.3 rule 8).
2. Verify the delivery signature over the received bytes; recompute and
   compare `digest`. Mismatch ⇒ refuse.
3. Extract the manifest; verify the author signature over `authored.digest`
   against a pinned key for the claimed publisher. An unpinned publisher is
   not a weaker trust level — it is a refusal.
4. Effective families = grant ∩ `max_capabilities` ∩ author-attested ∩
   delivery-attested.
5. Any block whose family exceeds effective ⇒ refuse the document whole. No
   partial load.
6. Apply the §7.7 floor.
7. Check revocation freshness (§7.6); stale past deadline ⇒ no new work.
8. Recompute the trifecta; widening refuses (§6). Apply at a quiesce boundary;
   run §5.4 lifecycle for departed blocks.

Failure at any step is **refuse, never degrade**. A failed signature check
MUST NOT reach any weaker path meant for unsigned advisory content, or an
attacker strips the signature to obtain it.

### 7.6 Revocation — the half signing cannot do

1. **Authorization is current membership in the caller's effective set**,
   re-read on an interval bounded by `freshness`. `compute` and `infra` MUST
   re-check; other classes SHOULD.
2. **Only an affirmative signal changes state** (§5.4 rule 5). A failed read
   is staleness; past the deadline, refuse new work and let live work follow
   §5.4.
3. **On revocation:** no new work; live work follows §5.4; the runtime
   triggers local retraction of derived state. The control plane revokes
   documents; the runtime retracts what they caused.
4. **Offline revocations are honored at reconnect.** A full reconcile
   converges to the current effective set and runs retraction for anything
   that left.
5. Revocation is **per principal**. Absence from one caller's effective set
   says nothing about another's.

### 7.7 Hard floor

`compose` and `identity` are **never admissible in a document that arrived
over the wire**, signed or not. A signature over a remote
privilege-management channel establishes whose fault it was, not that it was
safe. Operator surface only.

### 7.8 What this does not protect against

- **Delivery-key compromise** ⇒ arbitrary *resolutions* of authored documents,
  bounded by the author attestation's ceiling and detectable by manifest
  audit. This is the cost of per-reader resolution, and why the author
  signature ships first.
- **Author-key compromise** ⇒ full compromise within the attested ceiling,
  bounded only by `max_capabilities` and §7.7.
- **A valid signature over hostile prose is still hostile prose.** Signing is
  provenance, not safety; approval, provenance envelopes and the trifecta
  check stay load-bearing.
- **The manifest proves determinism, not benevolence.** A resolver that
  consistently substitutes a hostile value produces a consistent manifest.
  Trusted-inputs-only constrains that, and it is enforced by the resolver,
  not the verifier.
