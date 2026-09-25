# S20 — Stable refusal codes

**Type:** process (1.x) · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

A refusal is compared by its message string: rewording a message breaks
conformance, messages cannot be translated, and documentation cannot link to
one.

## Normative text

§1.4: "A refusal MUST name the line, the construct, and what to write instead,
and MUST carry the **code** Appendix B gives its condition." Appendix B gains a
`Code` column; the message shapes remain RECOMMENDED. Conformance compares
`line` and `code`; `refusals.json` carries both, and the message as a reference.

The codes are listed in Appendix B.
