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
