# Machine-readable contracts

All schemas use JSON Schema draft 2020-12. They validate interchange values,
not Markdown parsing, resolution correctness, permissions or rendering quality.

| File | Contract |
|---|---|
| [`../instruction.schema.json`](../instruction.schema.json) | Authored document/tree |
| [`resolved.schema.json`](resolved.schema.json) | Resolved snapshot, dependencies and provenance |
| [`extension.schema.json`](extension.schema.json) | Namespaced extension manifest |
| [`bundle.schema.json`](bundle.schema.json) | Resource bundle manifest |
| [`testing.schema.json`](testing.schema.json) | Test requests and results |
| [`workflow.schema.json`](workflow.schema.json) | Native Instruction Workflow definitions and per-kind step fields |
| [`../workflow-registry.json`](../workflow-registry.json) | Workflow kinds, trigger roles, required fields and common fields |
| [`../registry.json`](../registry.json) | Built-in kinds, forms, attributes, inline types, keywords and lexical tokens |

`tools/build_registry.py` is the editable source for the registry and generated
schemas. Run it after changing those definitions; `--check` detects drift.
Workflow artifacts are generated with `tools/workflow_support.py` from the
frozen provenance snapshot. Graph validation and scheduler semantics live in
the [workflow reference](../reference/workflows.md), beyond JSON Schema.
`tools/check_spec.py` checks these artifacts and conformance-data consistency.
The main text and language reference remain normative for requirements that
JSON Schema cannot express. Resolve schema references locally by their `$id`;
validation must not depend on a network request to instruction.md.
