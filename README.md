# The instruction.md Specification

**Status:** First-edition working draft. **Format:** `instruction/1`.
**Date:** 2026-10-28. **Publisher:** instruction.md.
**License:** specification text CC BY 4.0; conformance data Apache-2.0.

An **instruction document** is a reusable Markdown document that conveys nuanced
guidance from people to agents and lets people review the same guidance through
rich rendering. It can describe an assistant, a skill, a workflow, a team practice
or a reusable part of any of them. It combines ordinary prose with meaningful
rules, policies, examples, media, code, connected objects and composition. It can
also carry typed runtime configuration and workflow definitions, making one
authored instruction the source for a compiled agent setup and its resource bundle.

This specification defines the first version of that language. It also defines
standardized resolution, extension manifests and portable resource packaging.
The instruction.md web editor and other editors, including a VS Code extension,
can implement it. Production execution is provided by external systems.

Start with the [authoring guide](guide/README.md), [language reference](reference/markdown.md)
and [morning-assistant example](samples/morning-assistant/instruction.md) and the
[compiled AgentD setup](samples/agentd-assistant/README.md).
[Instruction Workflows](reference/workflows.md) define the native workflow
language, its [node catalog](reference/workflow-nodes.md), schemas and execution
semantics. AgentD is one runtime adapter for that language.
[JSON schemas](schemas/README.md) and [conformance cases](conformance/README.md)
accompany the normative text. They do not constitute a reference implementation.

## Contents

1. [Scope and conformance](#1-scope-and-conformance)
2. [Terms and document model](#2-terms-and-document-model)
3. [Metadata and comments](#3-metadata-and-comments)
4. [Markdown profile and parsing](#4-markdown-profile-and-parsing)
5. [Directives, attributes and identities](#5-directives-attributes-and-identities)
6. [Instruction semantics](#6-instruction-semantics)
7. [Core block registry](#7-core-block-registry)
8. [Layout and presentation](#8-layout-and-presentation)
9. [Code, data, media and drawings](#9-code-data-media-and-drawings)
10. [People, skills, MCP and agents](#10-people-skills-mcp-and-agents)
11. [References and selectors](#11-references-and-selectors)
12. [Parameters](#12-parameters)
13. [Composition and inheritance](#13-composition-and-inheritance)
14. [Resolution and agent representation](#14-resolution-and-agent-representation)
15. [Extensions](#15-extensions)
16. [Resources and bundles](#16-resources-and-bundles)
17. [Editors and integration adapters](#17-editors-and-integration-adapters)
18. [Diagnostics and limits](#18-diagnostics-and-limits)
19. [Security and provenance](#19-security-and-provenance)
20. [Schemas, governance and references](#20-schemas-governance-and-references)

## 1. Scope and conformance

The capitalized words MUST, MUST NOT, SHOULD, SHOULD NOT and MAY have the
BCP 14 meanings of RFC 2119 and RFC 8174. These implementer requirements are
distinct from authored rule keywords addressed to an agent (§6).

An implementation declares its roles and supported extensions:

| Role | Required behavior |
|---|---|
| Parser | Apply §§2–12 and emit the authored tree; preserve unsupported syntax and diagnose structural errors |
| Resolver | Implement the parser contract and §§11–16; produce a resolved result and dependency/provenance records |
| Renderer | Implement the parser contract and §§6–11, 15; show shared content with useful fallbacks |
| Agent serializer | Implement §14's text profile; preserve shared content, references and resource descriptions |
| Editor | Implement parser/renderer requirements and §17's source preservation and review duties |
| Compiler | Resolve declared targets, validate named native profiles, and emit traceable configuration/workflow/skill artifacts without activating them (§§16–17) |
| Test adapter | Implement §17's request/result contract and declare its supported external test service |
| Workflow host | Validate and explicitly activate native workflows under a declared node, expression, identity and durability capability profile |

A role claim is scoped: a renderer is not thereby a workflow engine. Rendering,
resolving or opening a document MUST NOT register schedules, execute scripts,
call business tools, or deploy an agent. A deliberate test operation uses a
host-authorized integration. External runtime exports are explicitly identified
adapter outputs, not behavior implied by ordinary code fences.

A document without Instruction-specific constructs is valid ordinary Markdown.
An unaware viewer can display the source but cannot claim to have applied
inheritance, checked rules or resolved connected objects. A conforming consumer
MUST distinguish source readability, partial resolution and complete resolution.

## 2. Terms and document model

The conventional filename is `instruction.md`; other filenames may carry the
same format. Source is strict UTF-8 and may be served as `text/markdown` with
`charset=UTF-8`. LF, CRLF and CR line endings are accepted for parsing; source
digests always cover original bytes. Invalid UTF-8 is an `invalid-source` error.

| Term | Meaning |
|---|---|
| Source | Original UTF-8 bytes of a Markdown file and its resources |
| Body | Shared human/agent content, excluding metadata and Markdown comments |
| Node | An ordered piece of content: Markdown or a typed directive |
| Kind | A block or inline object's registered meaning, such as `must`, `person`, `mcp` |
| Form | Container, leaf, inline, keyword or alert spelling |
| Identity | Explicit `id`, stable within a document instance |
| Reference | A target identity/location plus an optional selector and version mode |
| Resolution | Applying inheritance/includes/parameters and enriching references |
| Projection | A representation of the same shared content, such as HTML or agent text |
| Origin | Source document, source range and composition path of a node |
| Extension | A namespaced, versioned addition with a manifest and fallback contract |
| Adapter | A host implementation of discovery, resolution, rendering, testing or export |
| Bundle | Main Markdown file plus resources and a manifest with original identities |

All substantive body content is shared. There is no human-only or agent-only
body switch. Tabs, columns, accordions and other layout wrappers MUST NOT
silently remove content from agent projections. Examples and quoted code are
shared **as examples and quoted code**, not promoted into operative rules.
Metadata may configure resolution; its arbitrary prose MUST NOT be injected as
additional hidden instructions. Referenced object data appears only through an
explicit body reference or object declaration.

The authored tree is `{format, metadata, body}`. `format` is `instruction/1`.
`metadata` has `front` and `back` mappings. `body` is an ordered array:

- Markdown node: `{type: "markdown", source: "…"}`.
- Directive node: `{type: "directive", kind, form, attrs, children}`.
- `id`, when present, is `attrs.id`; `range` records 1-based start/end source
  lines. Markdown nodes retain base Markdown syntax in `source`. A resolved
  node additionally carries `instance`, its composition path such as
  `root/personal`; identity is the pair `(instance, attrs.id)`.
- A directive with a structured/literal body carries `value: {format, source}`
  instead of `children`. Parsed structured data is additionally in `value.data`.
- Keywords and alerts normalize to directive nodes with `form: keyword` or
  `form: alert`, their label removed from their Markdown children. Inline objects
  remain in Markdown `source`; a full Markdown AST
  may be attached by an implementation, but is not required by this interchange.

Node order, body interpretation and origin are semantic. HTML/CSS and editor
selection state are not the document model. A lossless editor keeps original
source/trivia in addition to this semantic tree. The schema validates the tree;
it does not parse Markdown or prove cross-document correctness.

## 3. Metadata and comments

### 3.1 Front matter

Optional front matter starts on the first line with exact `---` and ends with
exact `---`. A leading UTF-8 BOM is ignored for recognition but retained for
source hashes. A recognized metadata block MUST be a YAML mapping.

```yaml
---
spec: "1"
id: https://example.org/instructions/morning
title: Morning assistant
version: "2026-10-26"
language: en-CA
tags: [personal, planning]
parameters:
  timezone: { type: string, default: America/Toronto }
extensions:
  charts: { id: dev.example/charts, version: "1.0.0", required: false }
resolvers:
  contacts: { adapter: directory, account: personal }
---
```

| Key | Contract |
|---|---|
| `spec` | String `"1"`; an integer `1` normalizes to it. Other values are unsupported-format errors |
| `id`, `version` | Document URI and author's version label; neither substitutes for a byte digest |
| `title`, `description`, `language`, `tags`, `license` | Descriptive metadata; language uses BCP 47 and license may use SPDX |
| `parameters` | Mapping of parameter names to typed declarations (§12) |
| `extends` | Ordered base-document reference records (§13) |
| `extensions` | Local aliases bound to exact manifest identities/versions (§15) |
| `references` | Named reference records used by explicit body references (§11) |
| `resolvers` | Adapter/account aliases; credentials are host-side |
| `exports` | Named explicit compiler targets: adapter, profile, body-reference bindings and optional required flag (§16.1) |
| `presentation` | Theme/style tokens and optional stylesheet/component references |
| `requires` | Extension aliases required in addition to their bindings; never a grant |

Unknown metadata keys MUST be preserved and MUST NOT affect core semantics.
Known keys MUST follow the metadata schema. `spec` absent means this format.
Core consumers MUST NOT infer a different dialect from a filename alone.

### 3.2 Backmatter

Optional **backmatter** follows the body after a plain **`---`** separator. There
is no word after the separator and no closing fence: its YAML mapping continues
to the end of the file. It is recognized only at the whole-document level.

```yaml
---
authors: [Alex]
owners: [Alex]
review: { next: "2027-01-26" }
history:
  - { date: "2026-10-26", summary: Add weekday planning guidance }
sources:
  - { id: handbook, title: Team handbook, uri: https://example.org/handbook }
test_results:
  - { uri: ./results/morning.json, source_digest: "sha256:…" }
```

Backmatter records authorship, ownership, review, history, sources, approvals,
notes and test-artifact references. Unknown keys are preserved in `metadata.back`.
It MUST NOT supply resolution configuration that changes preceding body content.
`sources` records may be cited as `:cite[Handbook]{ref=handbook}`; citations add
attribution, not the source's unreferenced contents.

To distinguish backmatter from ordinary Markdown thematic breaks, recognition
uses these rules:

1. The separator is an exact `---` line at physical column zero, preceded by a
   blank line after the body. It is outside code, directive containers, block
   quotes, list items and HTML blocks. The front-matter closing fence is never
   a backmatter opener. A setext heading underline is not an opener.
2. The first subsequent nonblank line that is not a YAML `#` comment begins
   with an unquoted root key `authors:`, `owners:`, `review:`, `history:`,
   `sources:`, `approvals:`, `notes:` or `test_results:`. The colon is followed
   by whitespace or the end of the line. This known first key identifies the
   terminal metadata region; additional, unknown keys are allowed after it.
3. Once an opener is recognized, everything after it is a single YAML mapping
   through EOF, subject to §3.3. Empty, malformed or multidocument YAML is an
   `invalid-metadata` error, not a reason to reinterpret the region as guidance.
   A second `---` closing fence is therefore not used.

A separator without that known-key cue remains an ordinary thematic break.
To write a thematic break followed by prose that looks like backmatter, use
`***` or `___` for the break, or escape it as `\---`. Delimiter-looking lines
inside examples and other inert regions remain literal. Included documents
retain their own front-matter/backmatter boundaries and metadata scope.

### 3.3 YAML and comments

All metadata/structured bodies use YAML 1.2.2 Core Schema, restricted to
JSON-compatible values, or JSON where declared. Duplicate mapping keys,
non-string mapping keys, custom tags, aliases/anchors and non-finite numbers
are errors. Dates are strings; no timestamp type is inferred. A parser MUST
NOT execute constructors. Known fields are not silently coerced except where
this specification explicitly permits normalization.

CommonMark HTML comments outside code/literal bodies are author comments.
Their comment bytes are excluded from resolved body content at any position;
text before/after a comment remains. A comment occupying a whole source line
removes that line. An unclosed comment runs to EOF and reports a warning.
Comment-looking text inside code, data and verbatim bodies stays literal.
Comments are never scanned for directives, references, rules or interpolation.

## 4. Markdown profile and parsing

### 4.1 Base and additions

The base is CommonMark 0.31.2 with the **table, task-list, strikethrough and
extended-autolink** productions of GFM 0.29-gfm, applied on that CommonMark base.
GFM's site behavior and HTML sanitization are not imported as language rules.

Core rich authoring additionally defines footnotes, definition lists, heading
attributes, math, directives, wiki-links, typed inline references and rule
keywords. Their exact boundaries are in [the language reference](reference/markdown.md),
which is normative. Diagram/drawing languages retain their own syntax in code
or resources. Rich rendering support is declared independently of source parsing.

A checked task is authored status, not permission to act. Strikethrough is
presentation, not removal of an instruction. Code info strings identify content;
they never imply execution. A URL becoming a link never implies fetching it.

### 4.2 Precedence

A parser MUST use Markdown block/inline context, not only line regexes:

1. Recognize whole-document metadata only in its permitted scope.
2. Recognize CommonMark fenced/indented code and HTML blocks; comments are
   opaque until closed. Code fences indented up to three spaces, including
   within lists/quotes, suspend Instruction recognition.
3. Outside those regions, recognize container/leaf directives at physical
   column zero. Parse Markdown-bodied directive content recursively. A
   directive interrupts a top-level paragraph and terminates an enclosing
   Markdown list/quote rather than becoming an implicit child of it.
4. Within Markdown content, recognize alert headers and keyword rules before
   ordinary paragraph continuation. Footnotes/definitions follow §4.1's reference.
5. Within parsed inline content, code spans, escapes, link destinations and
   raw HTML tags take precedence over inline directives and interpolation.
   Recognize ordinary links before wiki-links/typed inline objects.

Instruction block directives are not recognized when indented or prefixed by
`>` or a list marker. Their Markdown bodies may contain any base Markdown,
and may contain shorter nested directive fences at physical column zero.
Inline objects work in parsed prose, including list items and table cells.
Rules do not activate in headings, table cells, link labels, code, math or
literal/example content. Ordinary blockquote paragraphs may carry rules;
`example` is the explicit quoted-example boundary.

Escaped syntax stays literal. Entity decoding MUST NOT manufacture a new
Instruction opener: `&#58;person[…]` is text. Base Markdown remains source
preserved; a formatter MUST NOT change its meaning to satisfy a stylistic rule.

## 5. Directives, attributes and identities

### 5.1 Forms

```markdown
:::policy{id=calendar title="Calendar policy"}
MUST: preserve tentative status.
:::

::person{id=alex title="Alex" role=owner src="https://example.org/people/alex"}

Ask :person[Alex]{ref=#alex} before changing a confirmed meeting.
```

Grammar (ASCII syntax; `SP` is space/tab, `EOL` is LF, CRLF, CR or the end of the file):

```text
kind       = [a-z][a-z0-9-]* (":" [a-z][a-z0-9-]*)?
id         = [A-Za-z0-9][A-Za-z0-9._-]*
open       = ":"{n>=3} kind attrs? SP* EOL
close      = ":"{m>=n} SP* EOL
leaf       = "::" kind attrs? SP* (EOL | EOF)
inline     = ":" kind "[" inline-label "]" attrs?
attrs      = "{" SP* (attribute (SP+ attribute)*)? SP* "}"
attribute  = key ("=" (quoted | bare))? | "#" id | "." class
key        = [a-z][a-z0-9_.-]*
quoted     = JSON double-quoted string, on one source line
bare       = one or more non-whitespace characters except { } "
```

The opener occupies its line. A close has no trailing text. Longer outer
fences contain shorter inner fences. An opening directive inside a parsed
container MUST use a shorter fence; equal/longer opening fences are errors.
A bare colon run outside a container is an ordinary Markdown line.
Unclosed known directives are errors. EOF is not an implicit close.

Inline labels use balanced brackets and CommonMark inline content without
nested links/inline directives. Recognition requires line start, whitespace or
an opening punctuation character before `:`. An escaped colon is literal.
Inline forms are references/citations/annotations, not hidden object definitions.
There is no heading-based declaration or overloaded `[]` set form: ordinary
headings and tables keep their normal meanings. Repeated objects use repeated
leaves/containers, which a visual editor may present as a table.

### 5.2 Attributes

Canonical spelling is `{id=x class="a,b" title="A title"}`. `{#x .a .b}` is
accepted sugar; duplicate IDs/keys are errors, including shorthand plus an
explicit key. Multiple `.class` shorthands accumulate, in order, into `class`.
Core attribute keys are lower-case and case-sensitive. No value is executable.

Bare flags normalize to boolean `true`. Schema-declared booleans accept only
`true`/`false`; integers use `-?[0-9]+`; numbers use
`-?[0-9]+(\.[0-9]+)?`. A schema-declared list splits its decoded value on
commas, trimming ASCII spaces; empty members are errors. Free-text commas
remain text. Structured objects/arrays belong in YAML/JSON bodies, not
attribute mini-languages. Unknown core attributes are errors; `x-*` attributes
are preservable annotations with no core effect. Extension attributes follow
the extension schema.

Titles are single-line strings. Common attributes are `id`, `title`, `class` (list), `format`, `verbatim`
(boolean), `src`, `ref`, `mode` (`live`/`pinned`), `version`, `sha256`,
`required` (boolean), `description` and `style`. Kind-specific attributes are
published in `registry.json`. `style` names a presentation token, not inline CSS.
An HTML/CSS component uses the explicit optional `component` mechanism (§8).

### 5.3 Identity and unsupported constructs

Explicit IDs are unique across a document instance, regardless of kind or
form. Heading suffix `{#id}` assigns the same identity. Kind names do not
namespace IDs. Names/titles are display data and need not be unique.

Unqualified kinds belong to this specification. A colon-qualified kind such
as `charts:metric` uses the document's `charts` extension alias. A well-formed
unknown directive MUST be preserved with its full source as an opaque node;
its body MUST NOT be rescanned to discover nested operative definitions.
An unsupported optional presentation extension uses its fallback. An unknown
core kind, undeclared extension alias, or unsupported required semantic
extension prevents a **complete** resolved result and produces an error.
A source renderer may still show that source with a visible diagnostic.

## 6. Instruction semantics

### 6.1 Rules

The operative rules are `must`, `should`, `may`, `never` and `guardrail`.
`always` aliases `must`; `avoid` aliases negated `should`. The advisory kinds
are `note`, `tip`, `important`, `warning`, `caution`; `info` aliases `note`.

| Authored keyword | Normalized kind | Meaning |
|---|---|---|
| `MUST`, `ALWAYS` | `must` | Binding obligation within its scope |
| `MUST NOT`, `NEVER` | `never` | Binding prohibition |
| `SHOULD` | `should` | Recommended default; departures should be explained |
| `SHOULD NOT`, `AVOID` | `should`, `not=true` | Recommended avoidance; negation is retained |
| `MAY` | `may` | Permission in the guidance, not a host capability grant |
| `GUARDRAIL` | `guardrail` | Explicit high-importance boundary for review and agent guidance |
| `NOTE`, `INFO`, `TIP`, `IMPORTANT`, `WARNING`, `CAUTION` | corresponding advisory | Context/advice; no rule strength |

Keyword form is `KEYWORD[id] (if condition): text`, with the
optional ID/condition independently optional and matched `**` markers when
used: `**MUST[id] (if condition):** text` is the emphasized spelling.
The bracketed ID and parenthesized condition are independently optional;
unmatched emphasis markers do not create a rule. At least one space follows
the label. A recognized keyword starts at a
parsed paragraph/list-item start **or interrupts the preceding keyword rule
at a new line in the same scope**. A non-keyword continuation stays with that
rule. Ordinary prose does not gain keyword semantics from a mid-sentence word.

```markdown
MUST[confirm]: confirm the person's timezone.
SHOULD: keep the brief under 200 words.
BECAUSE: the brief is a starting point for the day.
NEVER (if an event is tentative): describe it as confirmed.
```

A named keyword shares the ID namespace with directives. A condition is
nonempty single-line text without parentheses, interpreted by the agent,
not evaluated by the resolver. Containers express it with `if="…"`.
A `BECAUSE:` line/paragraph immediately after a rule in the same parent,
separated only by blank lines/comments, attaches its reason. `because="…"`
is equivalent. Two reasons are an error. An orphan reason remains prose
with an advisory. Reasons and conditions travel with their rule.

Alert form is a CommonMark blockquote beginning on its own line with
`> [!KEYWORD]`, case-insensitive and including multiword keywords. Its body
may have paragraphs. It normalizes to the corresponding rule/advisory.
Unknown alert types are ordinary blockquotes unless an extension defines them.

### 6.2 Policies, context and examples

`policy` groups related guidance under a title and optional `scope`, `authority`
and `source` attributes. Nested rules remain individual rules with their
origin and policy context. `instruction` is a named reusable guidance block;
`context` is labelled reference material. These meanings MUST survive projections.

`example` labels quoted material. Its body is base Markdown with Instruction
recognition/interpolation disabled; `avoid=true` means a counterexample.
An example MUST remain labelled as such in agent output. `verbatim=true`
on a Markdown-bodied directive similarly preserves its body literally.
Closing-fence recognition remains active so the container can end.

`output` describes the response contract with optional `response-format` and a `schema`
reference. A supplied schema is shared reference data, not silently hidden.
A schema reference alone does not promise that a host validates responses.

Rules are not proofs or runtime enforcement. Consumers MUST NOT claim that
styling a guardrail enforces it. Conflicting natural-language rules may be
flagged for review; no automatic textual strength sort removes content.
Explicit inheritance modifications can change any named block and MUST record
that change. Reviewers must be able to inspect the removed/replaced origin.

## 7. Core block registry

The normative [registry](registry.json) lists each kind's body interpretation,
forms and typed attributes. `M` below is Markdown; `Y` is YAML/JSON structured data.
Every body is shared; there is no machinery-stripping class.

| Family | Kinds | Default body / purpose |
|---|---|---|
| Guidance | `instruction`, `policy`, `context`, `must`, `should`, `may`, `never`, `guardrail`, `always`, `avoid` | M; reusable guidance, groups, obligations/permissions |
| Advisories | `note`, `info`, `tip`, `important`, `warning`, `caution`, `example` | M; labelled advice or quoted examples |
| Contracts | `output`, `form`, `param`, `glossary` | M except glossary definition list; parameter/input descriptions |
| Connected objects | `person`, `role`, `skill`, `mcp`, `tool`, `agent`, `service`, `source` | M; identity, connection reference and usage guidance |
| Resources | `resource`, `image`, `audio`, `video`, `pdf`, `figure`, `diagram`, `drawing` | M descriptions/captions; literal source uses nested code or a resource |
| Technical objects | `script`, `data`, `config`, `schedule`, `workflow`, `sandbox`, `test`, `eval`, `properties` | Script M with code; remaining Y by default |
| Layout | `section`, `columns`, `column`, `grid`, `card`, `tabs`, `tab`, `steps`, `step`, `details`, `aside` | M with ordered nested content |
| Optional presentation | `component` | M fallback; named component/HTML resource reference |
| Composition | `include`, `embed`, `replace`, `extend`, `remove` | References/patches (§13); forms restricted by registry |

Container form is accepted where the registry says so. Leaf form is accepted
only where the complete declaration may be expressed by attributes. Structured
bodies declare `format=yaml` or `format=json`; defaults are in the registry.
`data` additionally accepts CSV/text. CSV uses RFC 4180 quoting/record rules
with UTF-8 text: the first record is a header of unique nonempty field names,
each subsequent record has the same field count, and cells remain strings.
CSV cells and embedded spreadsheet formulas are never evaluated.
A structured body is not scanned for
Markdown or nested directives. JSON must be RFC 8259 JSON without duplicate keys.
`properties` attaches a structured data mapping to its immediate parent; it is
not a second source for attributes. A key repeated between parent attrs and
properties is an error, rather than an invisible override. Multiple properties
blocks under one parent are errors.

`form` lists parameter/input capture guidance; a renderer may offer fields,
but the shared body remains present. A collected value becomes a parameter
only through §12's declared input contract. `glossary` uses §4.1's definition-list
syntax; terms are free text and do not create implicit block IDs.

## 8. Layout and presentation

A layout contains ordinary shared content and has no instruction authority.
A `column` requires `columns`; a `tab` requires `tabs`; a `step` requires
`steps`. `columns` takes integer `count` from 1 to 12. `grid` takes `columns`
from 1 to 12. `column` may take `span` from 1 to 12. `details` takes boolean
`open`. Tab/step/card titles use `title`. A renderer MAY responsively stack
columns and MUST preserve reading order. Tabs and closed details retain all
content in accessible views, exports and agent output.

Inside `tabs`, a fenced code block that is not in a `tab` is a tab of its own,
titled by its `title`, else its `filename`, else its language: the same step
shown for several tools or languages. Such a tab is a view of the same children,
not a node of its own; the text profile delivers the fences unchanged and in
order, each with its attribute list.

`````markdown
:::tabs{title="Install"}
```bash {title="npm"}
npm install instruction.md
```
```bash {title="pnpm"}
pnpm add instruction.md
```
:::
`````

````markdown
::::columns{count=2}
:::card{title="What to do"}
MUST: distinguish confirmed and tentative meetings.
:::
:::card{title="What good looks like"}
Your 09:00 meeting is tentative. Your 11:00 review is confirmed.
:::
::::
````

Themes can change appearance but MUST NOT change rule meaning or composition.
Optional `component` blocks name an installed component and MAY reference HTML,
CSS or component resources. Their Markdown body is a mandatory substantive
fallback, and the component MUST NOT contribute hidden guidance beyond it.
Unknown components show that fallback. Raw HTML is preserved as source; a host
may sanitize or show it as code. HTML rendering MUST NOT execute document-supplied
scripts or access integration credentials. An explicit installed extension may
implement interactive UI through the host's component API.

## 9. Code, data, media and drawings

Ordinary fenced code supports any language info string, including `python`,
`bash`, `javascript`, `pseudo`, `mermaid`, `dot`, `plantuml`, `json`, `yaml`,
`toml` and `csv`. Unknown languages still show code. A trailing attribute list
on the info line supports `id`, `title`, `filename`, `highlight` (line ranges),
`caption` and `preview`. The language is the first token. Instruction constructs and
parameters inside code/math remain literal.

A renderer MAY show an `html` fence both as its code and as the page that code
describes. The rendering is a view of the code, never content of its own: it is
drawn in an isolated frame that runs no script, submits no form, cannot navigate
or read the host page, its storage or its credentials, and makes no request that
carries them. The code remains the shared content and is what agents receive.
`preview=false` keeps a fence as code only, for a fragment that is not a page;
`preview` is ignored on other languages.

`script` wraps code plus documentation, with `lang`, `sandbox` and `entry`
attributes. It does not itself run. `sandbox` describes an external execution
profile; its `adapter`/image/resources/network requirements are data for an
explicit test/export adapter. Core never guarantees a particular runtime.
`test` declares structured fixtures/assertions for code or workflows; `eval`
declares model cases. §17 specifies test exchange, not a universal judge model.

A diagram fence is a diagram **description**. A `workflow` is a declarative
object with a `dialect` and structured definition. A renderer MUST NOT treat
arbitrary Mermaid as an executable workflow. An extension may explicitly map
both views to one declared workflow model and MUST preserve that model on edits.

Media blocks use `src`, optional `sha256`, `mode`, `version`, `media-type`,
`alt`, `caption`, `transcript`, `preview` and type-specific selectors. Image
syntax remains valid; explicit blocks enable richer control. A media block's
Markdown body supplies shared description/usage. An informative media-only
block MUST have useful alt text, description or transcript. A decorative image
may use empty alt text but MUST be identified `decorative=true`.

A PDF may select `page` (positive integer); audio/video use `start` and `end`
in nonnegative milliseconds with `end > start`; image regions use `region`
as `x,y,width,height` normalized fractions in [0,1], with positive extents
inside the unit square. Page selection is not a claim to extract text or OCR.
Unsupported rich views show description, source link and selector.

Editable drawings retain a source resource (SVG, Excalidraw JSON, JSON Canvas
or an extension format), an optional preview and a shared description. The
preview is derived, not the authoritative editable drawing. A bundle includes
all declared image/font/file dependencies or visibly reports omitted ones.

### 9.1 Runtime configuration and workflow dialects

A `config` container is a YAML/JSON mapping with required `id` and `dialect`.
It carries configuration data for an explicit compiler/export operation, rather
than extra prose instructions. `workflow` also requires a named dialect.
`schema` and `schema-sha256` may identify and pin a native validation schema.
A reader that only renders source need not implement that runtime; a compiler
claiming a profile MUST validate its declared schema and profile constraints.

```markdown
:::config{id=runtime dialect="agentd/config" adapter=agentd}
agent:
  name: morning-assistant
  instruction: { file: ./guidance.md }
  tools: { internal: none, code: none, mcp: [calendar.events.list] }
skills: { dir: ./skills }
:::
```

The native **Instruction Workflows** language uses `dialect="instruction/workflow"`.
Its [normative reference](reference/workflows.md), [node catalog](reference/workflow-nodes.md),
[schema](schemas/workflow.schema.json) and [registry](workflow-registry.json)
define typed steps, triggers, dependencies, conditions, templates, branching,
human decisions, parallel/repeated work, durable waits, retries, idempotency,
budgets, schemas and run states. The complete initial 74-kind registry migrates
from AgentD; the language is now specified as part of instruction.md.

Native `{{ steps.calendar.output }}` expressions stay literal inside structured
bodies. The outer block records dialect/schema identity; the native definition
does not acquire an invented `version` field. Rendering a workflow never arms
its triggers or executes it. A workflow host validates a definition and its
capability profile, then activates it through an explicit authorized operation.

The [AgentD export profile](profiles/agentd.md) retains `agentd/config` and the
legacy `agentd/workflow` compatibility binding, and can export native Instruction
Workflows using supported node capabilities. Runtime configuration, credentials,
activation, process supervision and deployment remain adapter responsibilities.

Mermaid flowcharts, sequence diagrams and other diagrams remain explanatory
source. They are not alternative executable spellings of a workflow. An editor
may derive a view from a declared workflow model, but MUST preserve that model,
its dialect and unsupported fields when editing the diagram.

A new dialect/profile defines its native schema, bindings, path rules,
validation, conflicts, resource closure and output contracts. Syntax recognized
by this draft is not thereby syntax understood natively by an existing runtime.
AgentD's existing instruction parser need not accept these new unsigilled blocks:
the explicit profile emits native AgentD files instead.

## 10. People, skills, MCP and agents

Connected-object declarations identify entities and explain intended use:

```markdown
::person{id=alex title="Alex" role=owner src="https://example.org/people/alex" resolver=contacts}

:::mcp{id=calendar title="Calendar" src="https://example.org/mcp/calendar" account=personal tools="events.list,availability.read"}
Read appointments for planning. Ask before sending or changing invitations.
:::

:::skill{id=prioritize src="./skills/prioritize/SKILL.md" trigger="planning the day"}
Use the prioritization guidance when meetings and tasks compete for time.
:::

::agent{id=travel title="Travel researcher" protocol=a2a src="https://example.org/.well-known/agent-card.json"}

::agent{id=bookings title="Bookings" protocol=a2a endpoint="https://agents.example.org/a2a/v1" binding=JSONRPC skills="search,reserve"}
```

A people reference is a stable identity/role with an authored readable label.
A renderer may show a pill/profile card and a resolver may attach permitted
profile fields. A role may resolve to a different person per deployment.
Labels MUST NOT be silently rewritten to imply a different person.

An `mcp` can reference an MCP Registry entry, server metadata or endpoint.
`tool` can identify a server-local tool with a `server` reference and `name`.
Authored `tools`, `allow` and `deny` express intended use; they do not grant
connection or calling authority. Live tool discovery is a host integration.
An inaccessible profile/tool/schema is not permission to broaden a request.

A `skill` can reference a packaged Agent Skills `SKILL.md`, local guidance or
another instruction. Its trigger is guidance, not a resolver-time condition.
An A2A `agent` (`protocol=a2a`) is identified by its Agent Card, its endpoint,
or both, and MUST have `src` or `endpoint`. `src` names the Agent Card or a
catalog record. `endpoint` names the interface URL the agent receives A2A
messages at; `binding` names that interface's protocol binding in A2A's own
spelling (`JSONRPC`, `HTTP+JSON`, `GRPC`, or another the host supports), and
`tenant` the A2A tenant when one endpoint serves several agents. Given only an
endpoint, a resolver reads the card at `/.well-known/agent-card.json` on the
endpoint's origin; with no card there, the agent is known by its endpoint, with
the authored title and body as its only description. Given both, `endpoint`
selects one of the card's interfaces: one the card does not list is
`reference-missing` for a required agent and `reference-optional` otherwise.
`skills` lists the A2A skill IDs the author intends the agent to be asked for;
like an MCP server's `tools`, it expresses intended use and grants nothing.
A2A-advertised skills and packaged SKILL.md skills remain distinct unless an
adapter explicitly maps them. This spec does not reproduce or override MCP,
Agent Skills or A2A protocols.

Resolvers MUST record which fields came from a provider, their source/version
and the authored label. They MUST NOT import arbitrary external descriptions as
new operative document blocks. Enriched guidance stays visibly attributed.
Resolution itself MUST NOT send messages, invoke tools or instantiate agents.

## 11. References and selectors

### 11.1 Source forms

Ordinary Markdown links are navigation; matching IDs may be enriched without
transclusion. Reference-style links use their parsed destination, not a regex
restricted to inline links. A wiki-link `[[target|label]]` is sugar for a
navigation link; `[[target]]` uses target text as its label. An embed shorthand
`![[target|label]]` is an `embed`, never an implicit include.

Typed inline forms are `:ref[Label]{ref=target}` and the connected/resource kind
shortcuts `:person`, `:role`, `:skill`, `:mcp`, `:tool`, `:agent`, `:service`,
`:source`, `:resource`. A shortcut MUST match a known resolved target kind;
a mismatch is an error. `:cite[Label]{ref=source-id}` cites a source record.
Typed reference labels are required. Plain `@name` and `#tag` remain prose
unless an extension adds a presentation annotation; they do not resolve identities.

A target is a relative/absolute URI, local `#id`, included `#alias/id`, or a
named metadata-reference key. Attributes such as `target`, `ref`, `schema`,
`sandbox` and `server` use these same targets, not an inferred kind namespace.
Within YAML/JSON, reference-carrying fields are identified by the kind/adapter
schema; arbitrary strings are not scanned for accidental `@` references.

### 11.2 Reference records

A full reference record is `{uri, select?, mode?, version?, sha256?, required?}`.
A bare named target first looks up the current source's `references` mapping,
then is treated as a relative URI; use `./name` to force a relative path.
An extension binding may additionally specify a `manifest` URI; otherwise the
host locates its manifest by identity/version through its installed catalog.
Selectors are `{id: "…"}`, `{heading: "…", occurrence: 1}`, `{lines: [a,b]}`,
`{pointer: "/json/pointer"}`, `{page: n}`, `{time: [start,end]}` or
`{region: [x,y,w,h]}`. Exactly one selector is permitted. Bounds/type must
match the resource. Line numbers are 1-based inclusive; heading matching is
exact visible text and occurrence is 1-based. Stable IDs are recommended.
URI fragments beginning `id=` or `heading=` select those forms; ordinary
fragments match explicit IDs first, then a generated heading anchor.

Generated heading anchors: take visible inline text, Unicode-casefold it,
replace whitespace runs with `-`, remove characters except Unicode letters,
numbers, `_` and `-`, trim `-`; empty becomes `section`. Number collisions
`-2`, `-3`, … in source order, avoiding explicit IDs. Extension-rich headings
use their declared plain-text fallback. Explicit IDs are not casefolded.

`mode` defaults to `live`. `pinned` requires a full `sha256:<64 lowercase hex>`
digest of the target source bytes; an optional version is additionally checked
against provider metadata. `version` alone is a label, not an immutable pin.
`live` resolves once per resolution transaction and records the chosen snapshot;
a UI refresh begins a new transaction. It MUST NOT mutate an existing resolved
artifact behind its recorded digest.

Navigation links are not existence assertions and may form cycles. Composition
and required typed references are existence assertions. Missing optional
references produce a visible unresolved marker and a partial result; a required
missing reference, pin mismatch or composition cycle is an error. A host MUST
NOT reveal inaccessible private target details through diagnostics.

## 12. Parameters

Parameters are declared in front matter's `parameters` mapping or as a visible
`param` leaf (`name` required). Duplicate declarations are errors. Name grammar
is `[A-Za-z_][A-Za-z0-9_.-]*`, the same in declarations and `${name}` tokens.
Types are `string`, `number`, `integer`, `boolean`, `enum`, `list`, `url`,
`duration`. `enum` requires a nonempty string `values` array. `list` is an
array of strings, not a host-language object coercion. URL requires an absolute
HTTP(S) URI without whitespace. Duration is a nonnegative integer followed by
`ms`, `s`, `m`, `h`, `d` or `w`. Defaults must satisfy the declared type.

A declaration can specify `required`, `default`, `example`, `description` and
`source` (`input`, `workspace`, `identity`, `static`; default `input`). Values
come from explicit resolver inputs or verified host sources, not guessed from
conversation/tool output. Invalid supplied values are errors, not an invitation
to substitute a default. `example` is preview data only. Each included document
has its own declarations/values; an include/base record may explicitly pass
`with` values. Undeclared values are not inherited implicitly.

Interpolation applies only to parsed prose text and rule conditions/reasons,
never code spans/fences, math, URLs, attributes, HTML, YAML/JSON, comments,
verbatim or examples. Interpolation is one-pass data insertion, not reparsing.
Text serialization escapes Markdown punctuation introduced by a value.
Strings stay strings; booleans/numbers use JSON scalars; lists use comma-space
joined strings with escaped punctuation. Missing optional values stay `${name}`
with a diagnostic; missing required values are errors. A visible `param` block
is retained as an input description rather than stripped.

## 13. Composition and inheritance

### 13.1 Include and embed

```markdown
::include{src="./shared.md#id=privacy" as=privacy mode=live required}
::embed{src="./brief.pdf" page=2 title="Example brief"}
```

An `include` inserts a whole instruction body or selected fragment. An `embed`
presents a resource/fragment in place without importing its definitions into
local lookup. Both retain origin and descriptions. `as` is required for an
include and unique in the parent document. IDs from an include are addressed
externally as `#alias/id`; internal links retain their original lexical scope.
Repeated inclusion with different aliases creates separate instances.

Relative references resolve against the **originating source URI**, including
inside inherited/imported fragments, never accidentally against the receiving
file. Metadata of an included file is not injected into the parent's metadata.
Its own parameters/extensions/reference declarations are used while resolving
its content. Fragment selection does not silently import unrelated siblings;
dependencies referenced from a selected fragment are looked up in its original
document and recorded when needed. Selected nodes retain enclosing policy context.

### 13.2 Inheritance

Front matter `extends` is an ordered array of reference records, each also
carrying a unique `as` alias and optional `with` parameter mapping. A base must
be an instruction document; `select` may choose a reusable fragment. Resolve
bases depth-first in declared order, then apply the child's body patches in
source order, then append its ordinary local body content.

```yaml
extends:
  - { uri: ./personal-base.md, as: personal, mode: live }
```

```markdown
:::replace{target="#personal/brief-length"}
SHOULD: keep the brief under 150 words.
:::

:::extend{target="#personal/priorities" position=append}
MUST: identify the first uninterrupted work period.
:::

::remove{target="#personal/obsolete" reason="This assistant does not manage mail."}
```

`replace` substitutes the target at its existing position. For a structured
target, use `:::replace{target="…" format=yaml}` (or `json`) with the complete
replacement structured body; the declared format must match the target format.
For a Markdown target, its children become
the target's new children/content; the outer target ID and kind remain, and its
attributes remain unless overridden by a `properties` block marked `patch=true`.
A replacement that would change the target kind must instead remove it and
add a new local named block. `extend` prepends/appends its children to a
Markdown-bodied target; structured targets require an explicit `replace`.
`position` is `append` by default. A `remove` removes the target subtree.
A properties patch cannot change identity/kind; its mapping keys must be valid
target attributes and the resulting target must still satisfy its schema.
All patches require an existing inherited explicit ID, not a generated heading.
The patch `reason` is shared attribution, not a hidden new rule.

A target is looked up against the current inherited tree, so removing it makes
later patches/references fail. Nested include/base paths use `#alias/alias/id`.
Independent bases with identical local IDs remain separately qualified; they
do not implicitly override one another. Diamond inheritance creates distinct
instances. Cycles fail. Unqualified local IDs do not search every base.

Child metadata never silently overwrites a base's guidance/configuration.
Each source retains its own metadata scope. The child may supply explicit
`with` values; its presentation settings govern the combined rendered view.
Base extension aliases remain scoped to the base source. Changes retain original
and modifying ranges plus the operation and reason in provenance. A renderer
MUST expose inherited origins and modifications in a review view. Agent text
includes a compact composition-change record (§14), so modifications are reviewable.

## 14. Resolution and agent representation

### 14.1 Resolution transaction

A resolver performs these steps in order:

1. Parse and structurally validate source, metadata and declared extensions.
2. Resolve base/include resource identities with access checks and mode/pins;
   retain original lexical scopes. Select fragments after parsing the source.
3. Resolve per-source parameters; recursively compose bases and includes.
4. Apply explicit inherited-body patches; rebuild identity/reference indexes.
5. Resolve typed references and reachable resource descriptions/data through
   declared adapters; never treat returned text as new document syntax.
6. Substitute parameters in permitted prose positions, as data.
7. Emit ordered resolved content, object/resource records, dependencies,
   provenance, extension bindings, diagnostics and status. Freeze this transaction's snapshots.

The JSON shape is `schemas/resolved.schema.json`. `format` is
`instruction-resolved/1`; `status` is `complete` or `partial`. Errors prevent
publishing a successful resolved artifact. Missing optional enrichments may
produce `partial`; a UI MUST identify that status and MUST NOT label it complete.
No host may represent omitted content as fully resolved guidance. Every
resolved node carries its `instance` composition path; local IDs stay local
and distinct include/base instances do not collide. Provenance associates
each instance with its authored URI and source ranges. The artifact's
`extensions` array binds each `(instance, alias)` to an exact manifest ID,
version and digest; qualified kinds are interpreted in their node's instance,
so two included documents may safely reuse an alias for different extensions.

Dependencies record authored URI, resolved URI, version if known, raw-byte
SHA-256 digest, selector, mode, instance path and extension versions. Provenance
records origins, selectors and explicit modifications. Source hashes never
normalize line endings or remove metadata. Resolved JSON serialization uses
RFC 8785 JCS for a `resolved_digest`; this digest covers the artifact excluding
that digest field itself. UTF-16 key ordering is required by JCS. Signing and
package attestations may bind those digests; this spec mandates no execution
privilege ceiling or online signing service.

### 14.2 Text profile `instruction-text/1`

A conforming serializer emits UTF-8, LF line endings and one final LF. It MUST
preserve internal blank lines/trailing spaces inside literal/source segments.
Outside generated separators it MUST NOT globally collapse blank lines.

| Content | Text representation |
|---|---|
| Ordinary Markdown | Source, with permitted interpolation/reference forms normalized |
| Rule | Canonical `MUST:`, `SHOULD NOT:`, `NEVER:`, `MAY:` or `GUARDRAIL:` prefix; condition remains `(if …)` |
| Reason | `BECAUSE: …` immediately after its rule |
| Policy/instruction/context | `### Policy: T`, `### Instruction: T`, `### Context: T`, meaningful attribute JSON when present, then shared children |
| Example | `### Example: T` or `### Counterexample: T`, then body as quoted source |
| Other Markdown-bodied kind | `### kind: T` then a `Attributes: ` JSON line (excluding id/title/class/style) when nonempty, then all shared children |
| Structured kind | Kind/title heading, attribute line, then a fenced block with its format and complete source |
| Layout | Kind/title heading followed by every child in source order; only class/style/count/columns/span/open presentation attrs omitted |
| Typed inline reference | Authored label plus `(kind; target)`; unresolved adds `[unresolved]` |
| Include | Selected content in place, with origin in sidecar; no opaque replacement |
| Media/drawing | Kind/title, description/alt/transcript, source URI, selector and preview when present |
| Component | Its substantive Markdown fallback; component source remains a labelled resource reference |
| Removed/replaced inherited content | Effective content plus document-end `Composition changes` list naming operation, qualified target, origin and reason |
| Metadata/comments | Nothing as instructional body |

Generated headings always have exactly `### `, a label, `: ` and title or ID;
if neither exists use the kind. Generated attribute JSON uses RFC 8785 JCS.
Meaningful attributes on policies, contexts, examples and rules MUST also be
retained. A rule's `if`, `because` and `not` are already represented by its
label/reason and are omitted from its attribute line; an example's `avoid` is
already represented by its label. Other nonpresentation attributes remain.
Every generated unit
is separated from neighbors by exactly one blank line; an authored Markdown
segment is copied internally unchanged except for line-ending conversion.
Only segment-boundary LF characters are trimmed before generated separators
are inserted; internal blank lines and spaces are retained. Fenced wrappers
use a backtick run longer than any backtick run in their
literal body. Example source is fenced as `markdown`, so its rule-looking text
cannot be presented as an unlabelled operative rule.

After the body, emit `### Resolved references` when body-referenced object or
resource records exist. Sort records by `key` and emit each permitted record
as a JCS JSON fence, separated by a blank line. Do not emit unrelated provider
data. Then emit `### Composition changes` when patches exist, in application
order. Each line is `- operation target (origin: URI)` followed, when present,
by ` — reason`. This records changes without reinstating removed guidance.
These two informational sections are omitted when empty.

Inline references/citations are normalized only in parsed prose, not code or
HTML. Unknown optional presentation directives use their preserved shared
fallback/source with a visible type label. A multimodal adapter may additionally
attach resource bytes/crops/transcripts; it MUST identify unsupported modalities
and MUST NOT silently replace a description with unrelated generated content.
Exact serializer vectors live in `conformance/text/`; passing schema fixtures
alone is not a text-profile conformance claim.

## 15. Extensions

An extension manifest identifies `id` as `reverse.domain/name`, exact `version`,
`format: instruction-extension/1`, compatible `spec: ["1"]` and one or more
roles (`syntax`, `semantic`, `presentation`, `resolver`, `test-adapter`). The
schema is `schemas/extension.schema.json`.

```yaml
format: instruction-extension/1
id: dev.example/charts
version: 1.0.0
spec: ["1"]
roles: [presentation]
provides:
  blocks:
    metric:
      body: markdown
      forms: [container]
      attributes: { label: { type: string }, value: { type: number } }
      fallback: children
```

A document alias `charts` makes the kind `charts:metric`. Aliases are scoped to
their authored document. A manifest MUST declare each provided block/inline
kind, accepted forms, body interpretation, attribute JSON Schema and fallback.
Semantic extensions additionally define a standardized resolved-node mapping
and processing requirements. Resolvers/test adapters declare their request and
result schemas and external service requirements. Optional renderer/editor
modules are implementation references, not remotely executable document code.

The manifest must be available even when an implementation module is not.
If an optional manifest itself cannot be retrieved, the consumer preserves
source with a partial result; it cannot assert that unknown semantics are
fully supported. If the binding is required, that failure is an error.

A fallback is `children` for Markdown-bodied presentation types or `source`
for literal types. Unsupported optional presentation manifests can fall back
without semantic loss; semantic/resolver/syntax extensions affecting body
meaning MUST be required. Core names cannot be replaced; extensions cannot
redefine escaping, metadata boundaries or shared-body preservation. New syntax
must declare precedence/conflict behavior and its extension must be required.
Document `requires` entries are extension aliases and make those bindings
required; undeclared aliases are errors. Manifest `requires` entries identify
extension dependency IDs declared in its `dependencies` mapping.

Consumers MUST bind the exact declared manifest version and record its digest.
Manifest retrieval never installs or executes a module automatically. Hosts
own extension installation, authentication and permissions. Source, schemas,
renderers and adapters may be implemented in different languages/frameworks.
Extension publishers supply positive, fallback, invalid and resolution vectors.

## 16. Resources and bundles

Resource locations may be relative paths, absolute URLs or embedded `data:`
URIs. Encoding for embedded binary resources is base64; MIME type is required.
A host publishes size limits. Relative paths resolve under source origins, and
bundle mapping MUST preserve those semantics. A resolver MUST NOT escape a
bundle root through `..`, absolute paths or symlinks while materializing files.

A bundle is a ZIP file with `instruction.json` at its root, a `main` Markdown
path, and listed resource entries. `schemas/bundle.schema.json` defines its
manifest. Every entry records `path`, `media_type`, `sha256` and original `uri`;
optional `version` and `mode` preserve reference history. Paths are unique,
relative forward-slash paths with no empty, `.` or `..` segments. Reject duplicate
ZIP entries and symlinks; validate sizes and digests before use. A bundle MUST
NOT auto-unpack code into executable locations or overwrite unrelated files.

`mapping` maps original absolute resource URIs to entry paths. Bundled snapshots
are used when their digests match declared pins; live references retain their
mode and require an explicit online refresh to replace a bundle snapshot.
Missing unbundled resources are reported. A self-contained bundle must include
all required reachable resources/manifests or declare that it is incomplete.
A self-contained file uses embedded resources with the same identities/digests.

### 16.1 One authored source, explicit compilation

The format supports one authored source for guidance, configuration, skills,
workflows and resources. A compiler may emit a self-contained Markdown file or
a resource bundle plus runtime-native artifacts. Those outputs can replace
separately maintained configuration inputs; they do not replace operator
credentials, runtime installation, account binding or approval authority.

Front-matter `exports` entries have `adapter`, `profile`, `bindings` and optional
`required`. Bindings point explicitly to authored block identities; profile
rules define their keys. Missing/ambiguous targets and competing declarations
are errors, not grounds for silently merging grants or selecting arbitrary blocks.

```yaml
exports:
  morning:
    adapter: agentd
    profile: agentd/1
    bindings:
      config: "#runtime"
      instruction: "#guidance"
      servers: ["#calendar"]
      skills: ["#prioritize"]
      workflows: ["#brief"]
```

A compiler MUST resolve the selected document instance, preserve origins,
validate profile/schema pins, check references and paths, and report unresolved
required resources. It MUST distinguish complete from partial output. A
profile-selected guidance fragment is identified as that selected scope; it
MUST NOT be presented as a complete projection of the entire document.

A bundle may add an `exports` array. Each record has `id`, `kind`, `path`,
`sha256`, `adapter`, `profile`, optional `dialect`, and nonempty `sources` records
with source `uri`, byte `sha256`, and optional `select`. Export kinds are
`agent-instructions`, `config`, `workflow`, `skill`, and `resource`. Every export
path MUST identify a listed bundle entry with the same digest; export IDs are
unique. Source records MUST include every contributing document snapshot.
A compiler records its selected scopes and does not claim an output came only
from one block if other declarations contributed to it.

Compilation writes reviewable artifacts. It MUST NOT execute code, call business
tools, register schedules, install dependencies, connect accounts or start an
agent. Activation is a separate, explicitly authorized runtime operation. Native
runtime validation may still be needed after schema validation; passing a JSON
Schema does not prove operational correctness.

## 17. Editors and integration adapters

A web editor or VS Code extension may provide completions, pills, code editors,
schedule forms, drawing editors, layout controls, resolver pickers and test/eval
buttons. Every persistent semantic edit MUST be representable in the source or
listed resources. Saving MUST NOT depend on hidden editor-only semantic state.
The same document model and extension contracts apply in each editor.

Editors MUST preserve unsupported blocks, attributes, resources, quoted values,
comments and metadata they do not edit. They MUST NOT silently rewrite a script,
workflow, policy or connection target during an unrelated prose/layout edit.
Show changes to those objects as reviewable source diffs. A visual editor's
round trip must preserve stable IDs and references. Inheritance review shows
effective content, original content, origins and explicit modifications.

A resolver adapter receives the target, selector, mode and a host-bound account
alias; it returns status, immutable snapshot identity/digest, permitted object
fields/resources and diagnostics. It MUST declare its supported protocols and
must not perform business actions while enriching a reference. Authentication
credentials stay outside shared source/bundles; hosts bind aliases per user.

A host MAY keep a catalog of the integrations it has approved (MCP servers, MCP
registries, skill repositories, A2A agents) and offer their objects in
completions. A host MAY also restrict connected objects to that catalog. Under
a restriction, an object whose target is outside the catalog stays in the
document and in agent projections: it is never removed. It is not resolved or
enriched, a renderer marks it as not approved, and the host reports it with a
host-policy diagnostic (§18). The catalog grants nothing by itself; approved
objects still need the host's access checks.

An explicit test request identifies `format: instruction-test-request/1`, the
resolved/source digest, target block ID, adapter, inputs and optional model or
sandbox profile. A result (`instruction-test-result/1`) records that request's
identity/digests, status (`passed`, `failed`, `error`, `skipped`), environment,
timestamps, assertions and artifact references. Results use
`schemas/testing.schema.json`. No provider credentials are specified by the
format. Assertions can use equals/contains/not-contains/JSON Schema; regex/judge
checks must name their dialect/model settings to avoid claiming universal
cross-language equivalence. A skipped case is not a passing case.

Schedules record timezone and a declared expression dialect or structured
recurrence. Editors may show an occurrence preview. Calendar/timezone/cron
semantics belong to that named dialect. External systems explicitly import or
activate declarations; the document cannot silently schedule itself.

## 18. Diagnostics and limits

Diagnostics are `{code, severity, message, uri?, range?, target?, remedy?}`.
Severity is `error`, `warning` or `info`. Errors block a successful complete
resolution; readers may still display source with errors. Warnings do not
change content by themselves. Ranges use 1-based inclusive lines.

Core codes:

| Code | Condition |
|---|---|
| `unsupported-format` | Unknown `spec` or interchange format |
| `invalid-source` | Source bytes are not valid UTF-8 |
| `invalid-metadata` | Invalid/nonmapping metadata or known field shape |
| `adapter-unavailable` | Required compiler/runtime profile unavailable |
| `invalid-native-config` | Native configuration/profile validation failed |
| `invalid-workflow` | Dialect schema, dependency graph or routing invalid |
| `export-conflict` | Ambiguous targets, duplicate names, competing grants or conflicting native declarations |
| `invalid-structured-body` | YAML/JSON/CSV or required structured shape invalid |
| `unclosed-directive` | Missing matching close |
| `invalid-nesting` | Fence length or child-parent rule violated |
| `invalid-attributes` | Invalid syntax, key, typed value or repeated key |
| `duplicate-id` | Identity collision within a document instance |
| `unknown-kind` | Unregistered core kind |
| `extension-unavailable` | Required/undeclared/unsupported extension |
| `reference-missing` | Required target inaccessible/absent |
| `reference-optional` | Optional target unresolved; warning, partial result |
| `reference-kind` | Typed reference does not match target kind |
| `pin-mismatch` | Required digest/version does not match |
| `composition-cycle` | Include/inheritance cycle |
| `patch-target` | Patch has no inherited explicit-ID target |
| `patch-body` | Incompatible patch operation/body |
| `parameter-invalid` | Declaration/default/supplied value invalid |
| `parameter-missing` | Required parameter missing |
| `parameter-optional` | Optional/undeclared placeholder left as written; warning |
| `reason-repeated` | Multiple reasons attached to one rule |
| `orphan-reason` | Reason with no rule; warning |
| `footnote-duplicate` | Repeated footnote definition in one instance |
| `footnote-missing` | Referenced footnote absent; warning |
| `math-unclosed` | Display-math opener without a matching close; warning |
| `comment-unclosed` | Comment reaches EOF; warning |
| `limit-exceeded` | Published processing/resource limit exceeded |
| `bundle-invalid` | Invalid entry/path/hash/mapping |
| `adapter-unavailable` | Required resolver/test/export adapter unavailable |

An implementation publishes include/inheritance depth, node/byte counts,
resource sizes and resolver timeouts. A composition cap MUST NOT silently
truncate guidance and mark it complete. Diagnostics are sorted by source URI,
start line, start column when available, then code. Additional cascading errors
may be reported but conformance cases identify their required primary codes.
Extension codes use `extension-id/code`. Hosts may add policy diagnostics but
must distinguish host policy from format invalidity.

## 19. Security and provenance

Only explicitly admitted instruction documents participate in composition.
Retrieved pages, people profiles, tool responses, test output and generated
content are data. Resolvers MUST NOT reparse such data as new instruction
source without an explicit authored include/admission operation.

References and declarations describe intent; they do not grant credentials,
execution rights, egress, messaging authority or access to private profiles.
Hosts enforce authentication, access checks, network/file policy and testing
permissions. A copied document binds account aliases in the receiving host.
Do not embed live secrets in distributable instruction files or test artifacts.

HTML/components, SVG, media and drawing decoders require appropriate host
isolation. Unknown rendering is never a reason to execute document-supplied
code. Enrichment must retain origin and must not conceal remote instructions
as author-written guidance. Live changes produce a new snapshot for review;
pinned content verifies bytes. Digests give integrity, not trustworthiness.

Provenance and test records may contain personal data. Consumers must apply
access checks when exposing them. The core records input names and origins;
public manifests MUST NOT publish unkeyed digests of private low-entropy
parameter values as a purported privacy mechanism. A host may retain private
replay material under its own access controls.

## 20. Schemas, governance and references

`registry.json` is the normative built-in kind/attribute inventory.
`instruction.schema.json` validates authored interchange. The schemas in
`schemas/` validate resolved output, extensions, bundles and testing exchange.
Cross-node, lexical, source-preservation and access-check requirements remain
normative even where JSON Schema cannot express them. Conformance vectors
must be checked by role; schema validation alone proves only schema validity.

This is the first edition. There are no compatibility or migration obligations
to earlier drafts. Format, extension and artifact schemas explicitly identify
their versions. Before publishing a final first edition, parsing and resolved/text
vectors must agree in two independent implementations and all substantive
language features need reviewable examples. This repository's checks report
what they actually verify and do not claim that release gate has passed.

Changes enter through [proposals](proposals/README.md): motivation, normative
text, source/rich/agent examples, schema changes, fallback, diagnostics and
positive/negative vectors. Preserve authorship and license attribution when
adopting syntax or vendoring reference data.

Normative references:

- [CommonMark 0.31.2](https://spec.commonmark.org/0.31.2/).
- [GFM 0.29-gfm](https://github.github.com/gfm/), named extensions in §4.
- [YAML 1.2.2](https://yaml.org/spec/1.2.2/), restricted as §3.3.
- [JSON Schema 2020-12](https://json-schema.org/draft/2020-12/).
- [RFC 2119](https://www.rfc-editor.org/rfc/rfc2119), [RFC 8174](https://www.rfc-editor.org/rfc/rfc8174),
  [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986), [RFC 8259](https://www.rfc-editor.org/rfc/rfc8259),
  [RFC 6901](https://www.rfc-editor.org/rfc/rfc6901), [RFC 4180](https://www.rfc-editor.org/rfc/rfc4180), [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785).

Informative design sources and external protocols:
[MyST](https://mystmd.org/guide/syntax-overview),
[Pandoc](https://pandoc.org/MANUAL.html), [Quarto](https://quarto.org/docs/authoring/markdown-basics),
[remark-directive](https://github.com/remarkjs/remark-directive),
[Markdoc](https://markdoc.dev/docs/syntax), [Obsidian](https://obsidian.md/help/embeds),
[MDX](https://mdxjs.com/docs/what-is-mdx/), [VitePress](https://vitepress.dev/guide/markdown),
[JSON Canvas 1.0](https://jsoncanvas.org/spec/1.0/),
[Excalidraw](https://docs.excalidraw.com/docs/codebase/json-schema),
[Agent Skills](https://agentskills.io/specification),
[MCP Registry](https://registry.modelcontextprotocol.io/docs),
[A2A](https://a2a-protocol.org/latest/specification/),
[VS Code Markdown extensions](https://code.visualstudio.com/api/extension-guides/markdown-extension).
External protocol versions are bound by adapter declarations; `latest` links
are entry points, not immutable dependency pins.
