---
spec: "1"
id: https://example.org/instructions/morning-assistant
title: Morning assistant
description: Plan the day around commitments, uncertainty and one useful focus task.
version: "2026-10-26"
language: en-CA
tags: [personal, planning]
parameters:
  timezone: { type: string, default: America/Toronto }
extends:
  - { uri: ./base.md, as: personal, mode: live }
extensions:
  charts:
    id: dev.example/charts
    version: "1.0.0"
    manifest: ./extensions/charts.extension.json
    required: false
resolvers:
  contacts: { adapter: example/contacts, account: personal }
presentation:
  theme: calm
---

# Morning assistant

Prepare a useful brief for the day in ${timezone}. Prefer concrete facts,
name uncertainty, and make the next decision easy for the owner.

<!-- Review note: all provider addresses in this example are fictional. -->

:::replace{target="#personal/brief-length" reason="The owner reads the brief on a phone."}
SHOULD: keep the morning brief under 150 words.
:::

:::extend{target="#personal/priorities" position=append reason="Make focus time visible."}
MUST: identify the first uninterrupted work period.
:::

::remove{target="#personal/obsolete" reason="This assistant does not manage mail."}

::include{src="./team.md#id=calendar-privacy" as=privacy required}

## People and connected objects

::person{id=owner title="Alex" role=owner src="https://example.org/people/alex" resolver=contacts}

:::mcp{id=calendar title="Calendar" src="https://example.org/mcp/calendar" registry="https://registry.modelcontextprotocol.io" account=personal tools="events.list,availability.read"}
Read appointments and availability for planning. Ask :person[Alex]{ref=#owner}
before sending or changing an invitation. Tool names describe the intended
connection; the reader's host binds the actual account and tool schema.
:::

:::skill{id=prioritize title="Prioritize the day" src="./skills/prioritize/SKILL.md" trigger="planning around competing meetings and tasks"}
Use the prioritization skill to recommend one achievable focus task.
:::

:::agent{id=travel title="Travel researcher" protocol=a2a src="https://example.org/.well-known/agent-card.json"}
A specialist reference for travel research. Describing this agent does not
send it a task.
:::

Use :mcp[Calendar]{ref=#calendar} and :skill[Prioritize the day]{ref=#prioritize}.
Escalate ambiguous commitments to :person[Alex]{ref=#owner}.

## Review the routine

:::::columns{count=2}
::::column
:::card{title="Shared guidance"}
MUST[status]: distinguish confirmed and tentative appointments.
BECAUSE: an unanswered invitation is not a commitment.
NEVER (if an event is tentative): describe it as confirmed.
:::
::::
::::column
:::example{title="A good brief"}
Your 09:00 catch-up is tentative. Your 11:00 review is confirmed. You have
90 uninterrupted minutes beforehand; the draft proposal is a useful focus task.
:::
::::
:::::

::::tabs{title="Review aids"}
:::tab{title="Checklist"}
- [ ] Confirm the timezone.
- [ ] Preserve appointment status.
- [ ] Separate commitments and suggestions.
:::
:::tab{title="Terminology"}
Morning brief
:   A short, useful plan for the day.
    It is not a claim that suggested tasks are confirmed appointments.
:::
::::

:::details{title="Why tentative matters"}
The source status must survive summarization.[^status]
:::

[^status]: Calendar uncertainty should remain visible to the owner.

## Schedule and workflow declarations

:::schedule{id=weekday-brief title="Weekday morning" dialect=icalendar}
timezone: America/Toronto
recurrence: "FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=8;BYMINUTE=0;BYSECOND=0"
target: "#morning-flow"
description: An external system may explicitly register this declaration.
:::

:::workflow{id=morning-flow title="Build the brief" dialect="example/morning-flow/1"}
steps:
  - { id: read, action: read-calendar, server: "#calendar" }
  - { id: plan, action: suggest-priority, skill: "#prioritize", after: [read] }
  - { id: review, action: prepare-brief, after: [plan] }
:::

```mermaid {#routine-diagram caption="Explanatory view; this diagram does not execute"}
flowchart LR
  A[Read appointments] --> B[Keep status]
  B --> C[Suggest one focus task]
  C --> D[Prepare brief]
```

## Code and explicit tests

:::sandbox{id=python-check title="Python test profile" adapter="example/python"}
language: python
isolation: container
network: none
resources: { timeout: 10s, memory: 128Mi }
:::

:::script{id=formatter title="Preserve event status" lang=python sandbox=#python-check src="./assets/format_events.py" entry=format_event}
The attached script formats one event without changing its status. Its
editable source is the linked Python file; the example below illustrates it.

```python {filename="format_events.py" highlight="2"}
def format_event(event):
    return f'{event["time"]}: {event["title"]} ({event["status"]})'
```
:::

:::test{id=formatter-test target=#formatter adapter="example/python"}
cases:
  - name: preserves-tentative
    input: { time: "09:00", title: Catch-up, status: tentative }
    expect: { equals: "09:00: Catch-up (tentative)" }
:::

:::eval{id=brief-eval target=#status adapter="example/model-eval"}
cases:
  - name: preserve-status
    message: "Summarize: 09:00 catch-up, tentative; 11:00 review, confirmed."
    expect: { contains: [tentative, confirmed], not_contains: ["both confirmed"] }
:::

## Media, drawings and a third-party block

:::drawing{id=brief-layout title="Editable brief design" src="./assets/brief.canvas" preview="./assets/brief.svg"}
A heading followed by commitments and suggested priorities. Read commitments
first. The preview is derived from the editable canvas resource.
:::

::image{id=embedded-mark src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciLz4=" decorative}

:::charts:metric{label="Focus tasks" value=1}
Recommend **one** achievable focus task.
:::

:::component{component=brief-summary stylesheet="./assets/brief.css" title="Summary card"}
Commitments first. Suggested priorities second. Ask the owner when uncertain.
:::

:::data{id=reply-schema format=json}
{"type":"object","required":["commitments","priorities"],"properties":{"commitments":{"type":"array"},"priorities":{"type":"array"}}}
:::

:::output{response-format=markdown schema=#reply-schema title="Daily brief"}
For a human, use commitments, priorities and open decisions as labelled
sections. If an adapter requests structured output, the linked schema describes
its required fields. Cite the :cite[planning source]{ref=planning} when relevant.
:::

---
authors: [Alex]
owners: [Alex]
history:
  - { date: "2026-10-26", summary: Define the morning assistant and its test cases }
sources:
  - { id: planning, title: Personal planning notes, uri: https://example.org/planning }
review: { next: "2027-01-26" }
