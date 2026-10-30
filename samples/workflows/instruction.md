---
spec: "1"
title: Workflow examples
---

# Workflow examples

These definitions are authored examples. Opening this file does not activate them.

:::workflow{id=human-review dialect="instruction/workflow"}
name: morning-brief
steps:
  start:
    kind: manual
  read:
    kind: mcp.tool
    depends_on:
    - start
    server: calendar
    tool: events.list
    timeout: 30s
    retry:
      max: 2
      backoff: 2s
  draft:
    kind: agent
    depends_on:
    - read
    instruction: Prepare a daily brief. Keep tentative appointments tentative.
  review:
    kind: human
    depends_on:
    - draft
    question: Accept this daily brief?
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

:::workflow{id=parallel dialect="instruction/workflow"}
name: parallel-research
limits:
  steps: 20
  tokens: 6000
  deadline: 10m
steps:
  start:
    kind: manual
  research:
    kind: parallel
    depends_on:
    - start
    branches:
      calendar:
        steps:
          read:
            kind: mcp.tool
            server: calendar
            tool: availability.read
            args: {}
      priorities:
        steps:
          read:
            kind: agent
            instruction: Identify one achievable focus task from the supplied context.
  brief:
    kind: agent
    depends_on:
    - research
    instruction: 'Combine the research into a short brief: {{ steps.research.output
      }}'
  done:
    kind: finish
    depends_on:
    - brief
    output: '{{ steps.brief.output }}'
:::

:::workflow{id=resilience dialect="instruction/workflow"}
name: reliable-read
inputs:
  schema:
    type: object
    required:
    - request_id
    properties:
      request_id:
        type: string
steps:
  start:
    kind: manual
  fetch:
    kind: mcp.tool
    depends_on:
    - start
    server: calendar
    tool: events.list
    args: {}
    timeout: 30s
    retry:
      max: 3
      backoff: 2s
    breaker:
      failures: 5
      cooldown: 60s
    rate: 10/1s
    idempotency:
      value: '{{ inputs.request_id }}'
    on_replay: fail
  done:
    kind: finish
    depends_on:
    - fetch
    output: '{{ steps.fetch.output }}'
:::

:::workflow{id=schedule dialect="instruction/workflow"}
name: weekday-brief
steps:
  weekday:
    kind: schedule
    cron: 0 8 * * 1-5
  draft:
    kind: agent
    depends_on:
    - weekday
    instruction: Prepare a weekday brief. Name uncertainty and keep it under 150 words.
  done:
    kind: finish
    depends_on:
    - draft
    output: '{{ steps.draft.output }}'
:::

:::workflow{id=foreach dialect="instruction/workflow"}
name: review-items
inputs:
  schema:
    type: object
    required:
    - items
    properties:
      items:
        type: array
steps:
  start:
    kind: manual
  each:
    kind: foreach
    depends_on:
    - start
    over: '{{ inputs.items }}'
    as: task
    batch:
      size: 1
      parallel: 3
      rate: 10/1s
    body:
      steps:
        review:
          kind: agent
          instruction: 'Summarize this task and identify its next decision: {{ task
            }}'
  done:
    kind: finish
    depends_on:
    - each
    output: '{{ steps.each.output }}'
:::
