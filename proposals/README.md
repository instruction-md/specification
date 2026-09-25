# Proposals

Changes to The Instruction Specification enter through proposals. A proposal is
one file here with: motivation, the exact normative text, an example, delivery
impact, and a fixture. Status ladder: `draft → review → accepted → published`.
Additive changes are published as 1.x errata within the same integer version and
never invalidate a conforming version-1 document; a new integer is reserved for
breaking changes. Anything that touches parsing or delivery must pass its fixture
in two independent implementations before `published`.

| # | Proposal | Type | Status |
|---|---|---|---|
| [S1](S1-license-front-matter.md) | Optional front-matter `license` (SPDX expression) | additive 1.x | draft |
| [S2](S2-description-front-matter.md) | Optional front-matter `description` | additive 1.x | draft |
| [S3](S3-requires-front-matter.md) | Optional front-matter `requires` (families, spec, extensions) | additive 1.x | draft |
| [S4](S4-registry-uri-conventions.md) | Informative: registry URI conventions (`@ref`, `@version`, owner/name aliases) | informative | draft |
| [S5](S5-conformance-fixtures.md) | Conformance fixtures layout (fixtures only; runners live with implementations) | process | draft |
| [S6](S6-media-type-registration.md) | Media type registration: `text/markdown; variant=instruction` and the OCI artifact types | process | draft |
| [S7](S7-resolution-manifest.md) | The resolution manifest: one shape, one byte form, pinned by the corpus | normative | draft |
| [S8](S8-should-not-keeps-its-negation.md) | `SHOULD NOT:` keeps its negation in delivery | erratum 1.x | accepted |
| [S9](S9-author-notes.md) | Author notes: block HTML comments are never delivered or parsed | additive 1.x | accepted |
| [S10](S10-context-keys-unless-otherwise.md) | Registered context keys; `unless` and `otherwise` | additive 1.x | accepted |
| [S11](S11-skill-trigger.md) | `!skill` `trigger`; the acknowledgement says when to use it | additive 1.x | accepted |
| [S12](S12-named-keyword-rules.md) | Named one-line rules `MUST[name]:` | additive 1.x | accepted |
| [S13](S13-may-always-avoid.md) | `MAY:`, `ALWAYS:`, `AVOID:` | additive 1.x | accepted |
| [S14](S14-because.md) | `BECAUSE:` — a rule's reason | additive 1.x | accepted |
| [S15](S15-if-conditions.md) | Situational conditions `MUST (if …):` | additive 1.x | accepted |
| [S16](S16-examples-to-avoid.md) | Examples of what to avoid: `example{avoid}` | additive 1.x | accepted |
| [S17](S17-output.md) | `output` — the response contract | additive 1.x | accepted |
| [S18](S18-parameter-example-and-types.md) | Parameter `example`; types `list`, `url`, `duration`; values checked | additive 1.x | accepted |
| [S19](S19-advisories.md) | Appendix C — advisories with stable codes | additive 1.x | accepted |
| [S20](S20-refusal-codes.md) | Stable refusal codes | process | accepted |
| [S21](S21-authoring-guide.md) | Authoring guide, cheat sheet, delivered samples | informative | accepted |
| [S22](S22-body-schemas.md) | Reference body schemas per machinery kind | informative | accepted |
| [S23](S23-eval.md) | `!eval` — behavioural tests for prose | additive 1.x | accepted |
| [S24](S24-precedence-and-overrides.md) | Rule strength and `overrides` | additive 1.x | accepted |
| [S25](S25-delivery-labels.md) | Delivery label styles | additive 1.x | accepted |
| [S26](S26-named-prose-blocks-have-identity.md) | Named prose blocks have identity (erratum: `[[must/x]]` was refused) | erratum 1.x | accepted |
