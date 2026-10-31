# A2A endpoints, a tab per code block, and HTML shown as a page

Status: accepted — the owner's request, 2026-10-31. Roles: parser, renderer,
resolver, editor.

## Problem

1. An A2A agent can be named only by its Agent Card. Agents are often known by
   the endpoint they receive messages at, and one endpoint can serve several
   agents (A2A `tenant`).
2. Documentation shows one step for several tools or languages as tabs of code;
   `tabs` needed a `tab` wrapper around every fence.
3. An `html` fence showed only its code, though a reader often needs to see what
   it looks like.

## Change

- `agent` gains `endpoint`, `binding`, `tenant` and `skills` (§10). An agent with
  `protocol=a2a` MUST have `src` or `endpoint`. With only an endpoint, the card is
  read from `/.well-known/agent-card.json` on its origin (A2A discovery). With
  both, `endpoint` selects one of the card's `supportedInterfaces`; one the card
  does not list is `reference-missing` (required) or `reference-optional`.
  `skills` is intended use, like `mcp`'s `tools`.
- A fence directly inside `tabs` is a tab of its own (§8), titled by `title`,
  `filename` or its language. It is a view; the text profile is unchanged.
- An `html` fence MAY also be drawn as a page (§9), in an isolated frame: no
  script, no form submission, no navigation, no access to the host or its
  credentials. The fence attribute `preview=false` keeps it as code.
- A host MAY keep a catalog of approved integrations and restrict connected
  objects to it (§17); an object outside it stays in the document, is not
  resolved, is marked as not approved and gets a host-policy diagnostic.

## Representations

Source:

````markdown
::agent{id=bookings title="Bookings" protocol=a2a endpoint="https://agents.example.org/a2a/v1" binding=JSONRPC skills="search,reserve"}

:::tabs
```bash {title="npm"}
npm install instruction.md
```
```bash {title="pnpm"}
pnpm add instruction.md
```
:::
````

Agent text (`instruction-text/1`, unchanged rules): the agent is
`### agent: Bookings` followed by
`Attributes: {"binding":"JSONRPC","endpoint":"https://agents.example.org/a2a/v1","protocol":"a2a","skills":["search","reserve"]}`;
the tabs are `### tabs: tabs` followed by both fences as written.

## Registry and schema

`agent.attributes` adds `endpoint` (string), `binding` (string), `tenant`
(string) and `skills` (string list). The fence attribute list adds `preview`
(boolean); fence attributes are not in the registry.

## Fallback

An unaware renderer shows the agent's attributes, the fences one after another,
and the HTML as code. Nothing is lost.

## Diagnostics

`invalid-attributes` for an `a2a` agent with neither `src` nor `endpoint`.
`reference-missing` / `reference-optional` for an endpoint its card does not list.
A restriction to approved integrations uses a host-policy code.

## Security

The HTML view runs no document script and reaches nothing of the host's.
Integrations and restrictions grant nothing; access checks still apply.

## Vectors

The model vectors carry an agent known only by its endpoint; the reference
implementation's tests carry the missing-`src`-and-`endpoint` error, the code
tabs and the HTML view.
