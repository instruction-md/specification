# Cheat sheet

Every construct, how you write it, and what the model receives (default label
style). The full rules are in the [specification](../README.md); the guide is
[here](README.md).

## Rules

| You write | The model receives |
|---|---|
| `MUST: x` · `ALWAYS: x` · `:::must` | `**MUST:** x` |
| `SHOULD: x` | `**SHOULD:** x` |
| `SHOULD NOT: x` · `AVOID: x` · `:::should{not}` | `**SHOULD NOT:** x` |
| `NEVER: x` · `MUST NOT: x` | `**NEVER:** x` |
| `MAY: x` | `**MAY:** x` |
| `> [!GUARDRAIL]` | `**GUARDRAIL:** …` |
| `MUST[name]: x` | `**MUST:** x` (the name is for people and references) |
| `MUST (if c): x` · `:::must{if="c"}` | `**MUST (if c):** x` |
| `BECAUSE: y` after a rule · `{because="y"}` | `**BECAUSE:** y` after the rule |
| `:::must{overrides="should/brevity"}` | the overridden rule is not delivered |
| `NOTE:` `TIP:` `WARNING:` `CAUTION:` `IMPORTANT:` | the same label, bold |

Strength: `GUARDRAIL` > `NEVER` = `MUST` > `SHOULD` > `MAY`.

## Examples, context, output

| You write | The model receives |
|---|---|
| `:::example{title=T}` | `**EXAMPLE — T:**` then the body verbatim |
| `:::example{title=T avoid}` | `**EXAMPLE (avoid) — T:**` then the body |
| `:::output{format=json title=T}` | `**OUTPUT (json) — T:**` then the body |
| `:::context{title=T}` | `<reference title="T">` … `</reference>` |
| `:::glossary` | `**Term** — definition`, one per line |
| `:::tool{cap="server://x" allow="read"}` | `**Tool — X** (\`server://x\`) — allowed: read` |

## Situations

| You write | The model receives |
|---|---|
| `${name}` | its value, if it fits the parameter's type; else `${name}` |
| `:::when{environment="production"}` | the body, for a matching context |
| `:::unless{host="agentd"}` | the body, unless the context matches |
| `:::otherwise` | the body, when no variant just before it was kept |
| `::include{id="ins_42"}` | the included document, delivered for this reader |
| `::param{…}` · `:::param[]` | nothing |

Context keys: `agent` `model` `host` `environment` `locale`, and your parameters.
Parameter types: `string` `number` `boolean` `enum` `list` `url` `duration`.

## References

| You write | Means |
|---|---|
| `[[kind/name]]` · `[label](#kind/name)` | a block in this document (delivered as its label or name) |
| `[#Label](instruction://…)` | another instruction |
| `[@Label](principal://…)` | a person or an agent |
| `[&Label](server://…)` | a capability |
| `#tag` | a topic label |

## For people only

| You write | The model receives |
|---|---|
| `<!-- note -->` on its own line | nothing |
| front matter | nothing |
| end matter — a closing `---` YAML block (owners, approved, review, changelog, sources) | nothing |
| `:::!eval{name=…}` | nothing — run it with `instruction eval` |

## Machinery (L3)

| You write | The model receives |
|---|---|
| `:::!mcp{name=x …}` | `[mcp server "x" is connected; its tools are available]` |
| `## !skill x {trigger="…"}` + section | `[skill "x" is available — use it when …; reference it as @skill/x]` |
| `:::!human[]` table | `[3 human roles are declared: a, b, c]` |
| `:::!workflow{name=x}` | `[workflow "x" is loaded and runs autonomously]` |

## Label styles

Front matter `delivery: { labels: bold | plain | tags }`:

| bold (default) | plain | tags |
|---|---|---|
| `**MUST (if c):** x` | `MUST (if c): x` | `<must if="c">x</must>` |
