# S18 — Parameter `example`; types `list`, `url`, `duration`; values checked

**Type:** additive (1.x) · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

`default` doubles as the preview sample (§5.2), so a writer who wants a
realistic preview must change what is delivered. And a resolved value is
inserted whatever it is: `abc` for a `number` reaches the model.

## Normative text

§5.2 `param`:

- A new attribute `example`: a sample value for previews and capture forms.
  It is never delivered and never used as a value.
- `type` gains `list` (a comma-separated value), `url` (`http://` or
  `https://` and no whitespace) and `duration` (an integer and one of `ms`,
  `s`, `m`, `h`, `d`, `w`).
- **Values are checked against their type** at resolution: a `number` is
  `-?digits(.digits)?`, a `boolean` is `true` or `false`, an `enum` value is one
  of `values`. A value that fails is treated as unresolved — the placeholder
  stays and the name is reported — never inserted.
- A `default` that fails its own type is reported (`param-default-type`).

## Fixture

`conformance/corpus/parameter-types/`.
