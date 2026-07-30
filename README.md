# Framework

> Created by *Mikuláš Kadečka* for RBCZ - Finance.

## About

A framework for building Python web applications with a coding assistant. You
describe the application you want in plain language; the assistant plans it,
builds it, tests it, and commits it.

- **For everyone.** Aimed at non-technical and technical people alike.
- **A fixed workflow, not free-form chat.** The main assistant session is the
  only thing that talks to you, and it delegates to two subagents: a **planner**
  that decides what to build, and a **coder** that builds it and verifies it
  against its own tests.
- **Four commands drive a session.** `start`, `spawn`, `kill`, and `end`.
- **Ready on day one.** The framework ships inside a CodeNow component, so a new
  repository already contains the deployment scaffold, the assistant
  configuration, and a runnable app. There is one component per architecture:
  Flask is built, FastAPI and Dash are planned.
- **Two assistants.** Claude Code and GitHub Copilot are both supported; the
  Copilot side is built but not yet verified in a live session (see
  `docs/3b_copilot_workflow.md`).

## What is in this repository

| Part | What it is |
| :--- | :--- |
| `docs/` | The framework description: the goal, the workflow, how each assistant implements it, and the non-obvious behaviour that shaped the design. Start at `1_goal.md`. |
| `flask_template/` | The deliverable. A complete Flask and CodeNow starting project with the assistant configuration already in it. This is the master copy the CodeNow component is built from. |
| `handbook/` | The user tutorial, written for the people who use the framework rather than the people who build it. |
| `flowcharts/` | Diagrams of the framework's processes. Currently out of date with the documents in `docs/`. |
| `resources/` | Additional information and data, such as an unmodified CodeNow component scaffold kept for reference. |
| `CLAUDE.md` | The rules Claude Code follows when working on this repository. |
| `tasks.md` | Open work. |
