---
description: Implement the confirmed plan filed on an issue, test first
---

Use the skill `implement-feature`. Read AGENTS.md first.

Read the issue and its comments first: the newest comment headed
`## Umsetzungsplan (bestätigt)` is the plan. Without one, stop and point to
`/plan`.

Follow the cycle: scaffold → red → commit "Test:" → green → commit "Impl:".
The red run must fail on the assertion, and every new test must be red.

Implement **exactly** the acceptance criteria. No extra error handling, no
extension points, no configuration options, no new abstraction layers, no new
dependencies.

Run the profile's check chain after **every** step. Deviating from the plan: say
so first, then deviate, and note it on the issue. After three failed attempts at
the same problem: stop and report.

$ARGUMENTS
