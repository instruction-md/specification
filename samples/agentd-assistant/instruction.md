---
spec: "1"
title: A single-source AgentD assistant
exports:
  morning:
    adapter: agentd
    profile: agentd/1
    bindings:
      config: "#runtime"
      instruction: "#guidance"
      servers: ["#calendar"]
      skills: ["#prioritize"]
      workflows: ["#brief"]
---

# Morning assistant

:::instruction{id=guidance title="Morning guidance"}
Prepare a concise daily brief for the owner.
MUST[status]: keep tentative appointments tentative.
BECAUSE: an invitation is not a commitment.
SHOULD: suggest one achievable focus task.
NEVER: change an invitation without the owner’s approval.
:::

:::mcp{id=calendar title="Calendar" src="https://calendar.example.org/mcp" account=personal tools="events.list" allow="events.list" deny="events.delete"}
Read appointments for planning. The host supplies the account binding.
:::

:::skill{id=prioritize title="Prioritize the day" description="Choose one achievable focus task from the day’s commitments."}
1. Review commitments and available focus time.
2. Choose one useful, achievable task.
3. Explain why it is a good first priority.
:::

:::workflow{id=brief title="Morning brief" dialect="agentd/workflow" schema="https://agentd.dev/schema/workflow.json" schema-sha256="sha256:40f1d4a06967af70705d1b6aa508ebcc7defc7693ad3e8d8570eb02637ac5f23"}
name: morning-brief
description: Prepare a reviewable daily brief.
steps:
  start:
    kind: manual
  calendar:
    kind: mcp.tool
    depends_on:
    - start
    server: calendar
    tool: events.list
    args: {}
    timeout: 30s
    retry:
      max: 2
      backoff: 2s
  draft:
    kind: agent
    depends_on:
    - calendar
    instruction: 'Prepare a concise plan from these appointments, retaining their status: {{ steps.calendar.output }}'
    servers:
    - calendar
    timeout: 90s
  review:
    kind: human
    depends_on:
    - draft
    question: Accept this daily brief? {{ steps.draft.output }}
    schema:
      type: string
      enum:
      - accept
      - revise
    timeout: 2h
  route:
    kind: switch
    depends_on:
    - review
    'on': '{{ steps.review.output }}'
    cases:
      accept: accepted
      revise: revision
  accepted:
    kind: finish
    depends_on:
    - route
    output: '{{ steps.draft.output }}'
  revision:
    kind: finish
    depends_on:
    - route
    status: cancelled
    reason: The reviewer requested a revision.
:::

:::config{id=runtime dialect="agentd/config" adapter=agentd schema="https://agentd.dev/schema/config.json" schema-sha256="sha256:e9d632c2298d3e8ff80ec4f33419b6449ecd79e69853c75b37a071be7e562f5d"}
agent:
  name: morning-assistant
  instruction:
    file: ./guidance.md
  tools:
    internal: none
    code: none
    mcp:
    - calendar.events.list
skills:
  dir: ./skills
:::

---
authors: [Example author]
history:
  - summary: One source for guidance, native workflow, configuration and skill exports.
