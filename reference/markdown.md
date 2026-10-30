# Markdown language reference

This reference is normative for the core rich-authoring syntax of
[instruction/1](../README.md). Examples are source, not execution requests.

The native [Instruction Workflows language](workflows.md) is specified alongside
Markdown. Use `:::workflow{id=… dialect="instruction/workflow"}` for a structured
workflow definition; use Mermaid or other diagram fences for explanations.
The same workflow model supports source, graph and agent-facing projections.

## Base Markdown

Use CommonMark 0.31.2 plus the four GFM extensions named in §4 of the main spec.
The following are supported without redefining their base syntax:

| Feature | Examples |
|---|---|
| Headings | `# Heading` through `###### Heading`; setext underlines |
| Emphasis | `*emphasis*`, `**strong**`, combinations |
| Lists | `- item`, `1. item`, nested/loose/tight lists |
| Tasks | `- [ ] pending`, `- [x] complete` |
| Quotes | `> quotation` |
| Breaks | `---`, `***`; CommonMark hard/soft line breaks |
| Links | `[label](target)`, reference-style links, angle autolinks |
| Images | `![description](image.png)` |
| Code | Backtick spans, fenced backtick/tilde blocks, indented code |
| Tables | GFM pipe tables, escaped pipes, alignment markers |
| Strike | GFM strikethrough; struck guidance stays content |
| Escapes | CommonMark backslash escapes and character references |
| HTML | Preserved source with host-controlled rendering/fallback |

Base parsing does not guarantee a particular renderer's fonts, CSS, syntax
highlighter or remote-media support. Ordinary Markdown links/images never
become executable operations.

## Footnotes

`[^label]` references a footnote. A definition begins at zero to three spaces
with `[^label]: ` followed by content. Labels use the document ID grammar and
are case-sensitive. Continuations are indented at least four spaces relative
to the definition opener; blank lines may separate continuation blocks.
Duplicate definitions are errors. Missing definitions produce a warning and
remain literal. Number notes by first reference, not definition order.

```markdown
Tentative events remain tentative.[^tentative]

[^tentative]: This preserves the original calendar status.
    It does not imply the owner declined the invitation.
```

Footnotes are body content. Resolved/text projections retain definitions and
labels; a renderer may number them. Each included document instance retains
its own footnote namespace, qualified by the include/base path when merged.
No Instruction directive may start inside a definition's indented continuation;
ordinary Markdown and inline references remain usable there.

## Definition lists and glossary

A term is one nonblank line of free text. Its first definition starts on the
next line with a physical-column-zero `:` followed by at least one space.
Continuation lines indent at least four spaces. Additional definitions begin
with another `:` line. Entries are separated by a blank line. A term can have
several definitions; a definition may contain paragraphs and nested base lists.
This production takes precedence over an ordinary term paragraph only when
its following line is a definition opener. `:::kind` is a directive, not a
definition opener. Inline `:kind[label]` is not a definition opener.

```markdown
Morning brief
:   A short plan for the coming day.
    It distinguishes commitments from suggestions.
```

A `glossary` labels a collection of definitions. Terms have no automatic object
identity. A glossary with an ID may be referenced or included as a whole.

## Heading attributes and anchors

ATX headings may end with an attribute list separated from their text by a
space: `## Morning plan {#morning-plan .wide}`. Only `id`, `class` and `style`
are accepted there. The attribute list is excluded from visible heading text.
Closing ATX `#` markers, if used, precede the attribute list. Setext headings
use generated anchors only. Generated anchors follow §11.2 of the main spec;
explicit IDs share the document identity namespace with directive IDs.

## Math

A `math` code fence is a display formula with inert source. `$$` on a line
by itself opens a display-math region and the next standalone `$$` closes it;
it cannot cross a directive boundary. An unclosed region is literal prose
with a warning. Directive/reference/interpolation recognition is suspended
inside a recognized formula.

Inline math uses `$text$` on one line. The opener must be unescaped, immediately
followed by non-whitespace and not a digit. The closer must be unescaped,
immediately preceded by non-whitespace and not followed by a digit. This avoids
common currency strings. There must be a matching closer on the same line;
otherwise the dollar is ordinary text. Code spans and escapes take precedence.
A renderer may support a named TeX-compatible engine; unsupported formulas show
source. No TeX macro may execute host commands or access credentials/files.

## Directives and rich layout

Core block forms are `:::kind{attrs}` with a closing fence and `::kind{attrs}`
for a leaf. Inner container fences must be shorter than their outer fence.
Use the [registry](../registry.json) for accepted forms and attributes.

````markdown
::::tabs{title="Morning routine"}
:::tab{title="Calendar"}
Review confirmed and tentative appointments.
:::
:::tab{title="Priorities"}
Choose one focused task before adding optional work.
:::
::::
````

Every tab remains body content. Use `columns`/`column`, `grid`/`card`,
`steps`/`step`, `details` and `aside` for other layouts. Containers may nest;
use a longer outer fence for each additional level. CSS class/style attributes
control appearance only. Unaware renderers display visible source punctuation.

## Inline annotations and typed references

The core inline kinds below have required labels. The shared plain-text
fallback is the label; annotations add no hidden behavioral instruction.

| Form | Meaning / attributes |
|---|---|
| `:mark[important]` | Highlight text |
| `:sub[2]`, `:sup[2]` | Subscript/superscript |
| `:kbd[Ctrl+Enter]` | Key sequence |
| `:abbr[MCP]{title="Model Context Protocol"}` | Abbreviation with an expanded title |
| `:icon[calendar]` | Icon with a readable textual name |
| `:badge[tentative]` | Visible status label; no implicit state mutation |
| `:button[Read policy]{href="./policy.md"}` | Navigation link, never a business-action call |
| `:person[Alex]{ref=#alex}` | Typed person reference |
| `:skill[Prioritize]{ref=#prioritize}` | Typed skill reference |
| `:mcp[Calendar]{ref=#calendar}` | Typed MCP reference |
| `:agent[Travel researcher]{ref=#travel}` | Typed agent/A2A reference |
| `:ref[Privacy rule]{ref=#privacy}` | Generic typed-object/block reference |
| `:cite[Handbook]{ref=handbook}` | Attribution to a source record |

Core inline attributes are exactly those in `registry.json`'s `inline` map;
`class`, `style` and `x-*` annotations are also accepted. Reference/shortcut
kinds require `ref`, citation requires `ref`, button requires `href`, and abbr
requires `title`. Required values are nonempty. Reference labels can contain
base inline formatting, but cannot contain links or nested directives.

A colon opener must follow line start, whitespace or an opening punctuation
character `(`, `[`, `{`, `<`, `"` or `'`. Closing label brackets may be escaped.
This syntax is never recognized in code, math, HTML tags, link destinations or
literal/example regions. Plain tags such as `#planning` and mentions such as
`@alex` remain readable prose; an editor can suggest replacing them with an
explicit typed object reference.

## Wiki-links and references to parts

`[[target|label]]` is a link and `![[target|label]]` is a resource preview.
Targets may select fragments: `[[./team.md#id=privacy|Privacy policy]]`.
Use `\|` for a literal pipe in the label. The first unescaped pipe separates
target from label. Inside pipe tables escape the separator pipe for the GFM
cell tokenizer; apply wiki-link parsing after that tokenizer removes its one
escape layer. A label cannot span lines or contain nested wiki-links.

Navigation alone does not include guidance. Use an explicit `include` to
incorporate it. A reference record selector can address an explicit ID,
heading occurrence, code line range, JSON Pointer, PDF page, media time range
or image region; the main spec gives exact bounds and namespace rules.

## Rich code fences

````markdown
```python {#format-events filename="format_events.py" highlight="2-3" caption="Keep status visible"}
def format_event(event):
    status = event["status"]
    return f'{event["time"]}: {event["title"]} ({status})'
```
````

The code content is literal. Code-fence attribute lists accept `id`, `title`,
`filename`, `highlight` and `caption` only. `highlight` is a comma-separated
list of positive integers or inclusive `a-b` ranges with `a <= b`. Values are
presentation annotations, never dispatch targets. The displayed filename does
not materialize a file. A `script` block gives an explicit script object for
a testing/export adapter.

## Media and drawings

```markdown
:::video{id=walkthrough src="./assets/morning.mp4" start=1000 end=12000 transcript="./assets/morning.txt"}
A walkthrough of the morning brief. The owner selects a focus period after
reviewing confirmed meetings.
:::

:::drawing{id=brief-design src="./assets/brief.excalidraw" preview="./assets/brief.svg"}
A heading, an appointments column and a priorities column, in that order.
:::
```

A transcript attribute is a resource URI; an inline transcript belongs in the
shared description. A preview is a resource URI. Neither silently adds
unrelated guidance. Ordinary `![alt](src)` stays valid. PDF/page, audio/video
millisecond ranges and normalized image regions follow §9 of the main spec.

## Metadata and body boundaries

Front matter uses `---` at file start and a closing `---`. Backmatter follows
the body after a blank line and a plain `---` separator, with no label and no
closing fence. Its YAML mapping runs to EOF and begins with a known key such as
`authors:`, `history:` or `sources:` (after optional blanks/YAML comments). See
§3.2 of the main specification for the complete recognition rule and how to keep
ordinary thematic breaks. Comments are Markdown HTML comments. These
metadata/comment regions do not become instructional body. Delimiter-looking
text inside code, examples, verbatim/structured bodies and other inert regions
remains literal. Front matter/backmatter of an included file stays in its own scope.


## Runtime configuration and compiled exports

Use `:::config{id=runtime dialect="agentd/config"}` for a structured configuration
mapping, and `:::workflow{id=brief dialect="agentd/workflow"}` for its named
workflow DSL. Optional `schema` and `schema-sha256` attributes pin validation.
Expressions inside these structured bodies remain literal. Export bindings
select explicit block IDs; native runtime files and inline skill packages are
compiler outputs with provenance, not side effects of rendering.

See the [AgentD profile](../profiles/agentd.md) for exact bindings, schema pins,
conflict handling and a native workflow example. Mermaid flowcharts and sequence
diagrams remain explanatory code fences.
