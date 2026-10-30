# instruction.md cheat sheet

| Intent | Source |
|---|---|
| Bind guidance | `MUST[id]: …`, `NEVER: …`, `SHOULD NOT: …`, `MAY: …` |
| Explain it | `BECAUSE: …` immediately after a rule |
| Qualify a task-time rule | `MUST (if the invitation is tentative): …` |
| Group policies | `:::policy{id=privacy title="Privacy"}` … `:::` |
| Label examples | `:::example{avoid title="Counterexample"}` … `:::` |
| Describe output | `:::output{response-format=json schema=#reply}` … `:::` |
| Declare an object | `::person{id=owner title="Alex" src="https://…"}` |
| Reference an object | `:person[Alex]{ref=#owner}` |
| Reference guidance | `[[./team.md#id=privacy\|Privacy policy]]` |
| Include guidance | `::include{src="./team.md#id=privacy" as=privacy required}` |
| Preview a resource | `::embed{src="./brief.pdf" page=2}` |
| Inherit | Front matter `extends: [{uri: ./base.md, as: personal}]` |
| Modify inherited content | `:::replace{target="#personal/brief-length"}` … `:::` |
| Add to inherited guidance | `:::extend{target="#personal/priorities"}` … `:::` |
| Remove inherited content | `::remove{target="#personal/obsolete" reason="…"}` |
| Embed media | `:::video{src="./demo.mp4" start=0 end=10000}` description `:::` |
| Drawings | `:::drawing{src="./diagram.excalidraw" preview="./diagram.svg"}` description `:::` |
| Third-party block | `:::charts:metric{label="Tasks" value=3}` fallback `:::` |
| Runtime configuration | `:::config{id=runtime dialect="agentd/config"}` YAML/JSON `:::` |
| Native workflow DSL | `:::workflow{id=brief dialect="instruction/workflow"}` typed steps `:::` |
| Compiler target | Front-matter `exports` with adapter, profile and explicit block bindings |
| Parameter | `${timezone}` in prose; declarations in metadata or a `param` leaf |
| Front matter | Initial `---` / YAML mapping / `---` |
| Backmatter | blank line + `---` / known metadata key first / YAML mapping through EOF |

Nested containers use longer outer fences. Code, math, examples and verbatim
content are literal. Metadata/comments are excluded from shared body. Every
layout child remains available in agent projections. References never grant
accounts or execution permission. Editor tests are explicit external operations.
