# S11 — `!skill` `trigger`; the acknowledgement says when to use it

**Type:** additive (1.x); acknowledgement change · **Status:** accepted (owner, 2026-09-25) · **Raised by:** specification authoring review, 2026-09-25

## Motivation

`when` means two things: on the `when` kind it matches context keys before
delivery; on `!skill` it is a plain-English trigger (`{when="writing to
customers"}`). And the trigger never reaches the model: the acknowledgement
names the skill but not when to use it, which is the one thing the model needs.

## Normative text

§5.3 Core, `!skill`: attributes `name`, `description`, `trigger`. `when` is
accepted as an alias of `trigger` for version 1 and reported
(`skill-when-alias`); when both are given, `trigger` wins.

Acknowledgement: `[skill "x" is available — reference it as @skill/x]`, and
when a trigger is set: `[skill "x" is available — use it when {trigger};
reference it as @skill/x]`. A set of skills acknowledges as before.

## Delivery impact

Skills written with `when=` (the specification's own samples) now tell the
model when to use them.

## Fixture

`conformance/corpus/skill-trigger/`.
