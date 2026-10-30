# First-edition conformance data

This corpus describes the current `instruction/1` working draft. It does not
claim that two independent readers have already implemented the new language.
Data is Apache-2.0 licensed; the repository specification text is CC BY 4.0.

| Data | What it checks |
|---|---|
| `model/cases.json` | Positive built-in kind/attribute shapes, negative attributes and targeted schema edge cases |
| `source/cases.json` | Structural source cases: escapes, fence nesting, literal code/examples, metadata and comments |
| `text/*.json` / `*.txt` | Exact UTF-8 text serialization vectors for the listed authored-model subset |
| `resolution/cases.json` | Parsed-model composition: inherited replace/extend/remove, selected includes, namespaces and cycles |
| `samples/agentd-assistant/` | Single-source configuration/workflow/skill exports, digests and bounded graph cases; no runtime execution |
| `workflows/cases.json` | Native workflow positive/negative schema and graph vectors, including scoped bodies, branch targets and replay constraints |
| `resolved.json` | Resolved-snapshot interchange example |
| `test-request.json`, `test-result.json` | External testing exchange; the sample result is deliberately skipped |

`tools/check_spec.py` validates schema definitions, schema/model examples, a
bounded source structural scanner, the listed text vectors, parsed-model
composition cases, sample resources and bundle digests. Its helper is **not a
complete CommonMark/Instruction parser**, live-reference resolver or renderer.
Passing it is repository consistency evidence, not full role conformance.

Run with Python 3.9+ and `requirements-dev.txt` dependencies:

```sh
python3 tools/build_registry.py --check
python3 tools/build_agentd_sample.py --check
python3 tools/check_spec.py
```

`tools/build_fixtures.py` rebuilds generated kind examples and the bundle
manifest after intentional source/resource changes. Hand-authored edge/source
and exact text cases are declared in that file for review; changing generated
expected output is not proof of correctness. New semantics need independently
reviewed vectors and two implementations before first-edition publication.

Remaining implementation-level coverage includes full CommonMark interaction,
inline tokenization and escaping, heading/footnote normalization, external
selectors/enrichment, access checks, extension dispatch, full text serialization,
JCS, visual rendering, editor round trips and external adapters. Implementations
must publish their role/extension coverage and compare applicable fixtures.
