# Engineering

Skills I use daily for code work.

## User-invoked

Reachable only when you type them (Claude Code: `disable-model-invocation: true`; Codex: `policy.allow_implicit_invocation: false` in `agents/openai.yaml`).

- **[ask-matt](./ask-matt/SKILL.md)**: Ask which skill or flow fits your situation. A router over the user-invoked skills in this repo.
- **[grill-with-docs](./grill-with-docs/SKILL.md)**: Grilling session that also builds your project's domain model, sharpening terminology and updating `CONTEXT.md` and ADRs inline.
- **[triage](./triage/SKILL.md)**: Move issues through a state machine of triage roles.
- **[improve-codebase-architecture](./improve-codebase-architecture/SKILL.md)**: Scan a codebase for deepening opportunities, present them as a visual HTML report, then grill through whichever one you pick.
- **[setup-matt-pocock-skills](./setup-matt-pocock-skills/SKILL.md)**: Configure this repo for the engineering skills (issue tracker, triage labels, domain doc layout). Run once per repo.
- **[to-spec](./to-spec/SKILL.md)**: Turn the current conversation into a spec and publish it to the issue tracker.
- **[to-tickets](./to-tickets/SKILL.md)**: Break any plan, spec, or conversation into a set of tracer-bullet tickets, each declaring its blocking edges, whether as text in a local file or as native blocking links on a real tracker.
- **[implement](./implement/SKILL.md)**: Build the work described by a spec or set of tickets, driving `/tdd` at pre-agreed seams and closing out with `/code-review` before committing.
- **[wayfinder](./wayfinder/SKILL.md)**: Plan a huge chunk of work (more than one agent session can hold) as a shared map of decision tickets on the issue tracker, resolved one at a time until the way to the destination is clear.

## Model-invoked

Model- or user-reachable (rich trigger phrasing so the model can reach for them).

- **[dsg](./dsg/SKILL.md)**: Trạm điều phối thông minh & Phân tích sâu tự động: Tự động chẩn đoán tình trạng dự án và kích hoạt chuỗi skill phù hợp mà không cần người dùng nhớ tên skill.
- **[prototype](./prototype/SKILL.md)**: Build a throwaway prototype to answer a design question: a single shareable HTML file for state/logic, or several toggleable UI variations.

- **[diagnosing-bugs](./diagnosing-bugs/SKILL.md)**: Disciplined diagnosis loop for hard bugs and performance regressions: build a feedback loop that goes red on this bug → minimise → hypothesise → instrument → fix → regression-test.
- **[research](./research/SKILL.md)**: Investigate a question against high-trust primary sources and capture the findings as a cited Markdown file in the repo, run as a background agent.
- **[tdd](./tdd/SKILL.md)**: Test-driven development with a red-green-refactor loop. Builds features or fixes bugs one vertical slice at a time.
- **[domain-modeling](./domain-modeling/SKILL.md)**: Actively build and sharpen a project's domain model by challenging terms, stress-testing with scenarios, and updating `CONTEXT.md` and ADRs inline.
- **[codebase-design](./codebase-design/SKILL.md)**: Shared discipline and vocabulary for designing deep modules: small interfaces, clean seams, testable through the interface.
- **[code-review](./code-review/SKILL.md)**: Two-axis review of the diff since a fixed point: **Standards** (does it follow the repo's coding standards, plus a Fowler smell baseline?) and **Spec** (does it faithfully implement the originating issue/spec?), run as parallel sub-agents.
- **[resolving-merge-conflicts](./resolving-merge-conflicts/SKILL.md)**: Work through an in-progress git merge or rebase conflict hunk by hunk, resolving by intent traced to each side's primary source, then finish the operation, never `--abort`.
- **[wizard](./wizard/SKILL.md)**: Generate an interactive bash wizard that walks a human through steps only they can perform: provisioning infrastructure, setting up credentials or CI secrets, walking an unfamiliar third-party dashboard, or running a one-off migration or cutover.
- **[agent-disorientation-recovery](./agent-disorientation-recovery/SKILL.md)**: Recovery protocols when agent loses context, gets stuck in loops, or drifts from project requirements.
- **[chrome-web-store-prep](./chrome-web-store-prep/SKILL.md)**: Prepare Chrome Extension MV3 assets, manifest, permissions justification, and privacy policy for store review.
- **[claude-task-runner](./claude-task-runner/SKILL.md)**: Task runner and execution loop coordinator for Claude and agent automation workflows.
- **[code-bug-inspector](./code-bug-inspector/SKILL.md)**: Static inspection and automatic triage of syntax, type, import, and logic bugs with Python inspector.
- **[codebase-line-budget-guard](./codebase-line-budget-guard/SKILL.md)**: Track and enforce line count budgets and modularity limits across repository files.
- **[fullstack-boilerplate-architect](./fullstack-boilerplate-architect/SKILL.md)**: Architect and scaffold clean, production-ready fullstack project boilerplates.
- **[macos-m1-multiagent-setup](./macos-m1-multiagent-setup/SKILL.md)**: Setup, configure, and optimize local multi-agent environments on Apple Silicon macOS machines.
- **[multiagent-setup-crossplatform](./multiagent-setup-crossplatform/SKILL.md)**: Cross-platform multi-agent development setup across macOS, Linux, and Windows.
- **[project-blueprint-loop-architect](./project-blueprint-loop-architect/SKILL.md)**: Design project blueprints, state machine loops, and autonomous agent iteration cycles.
- **[system-logs-and-diagnostics](./system-logs-and-diagnostics/SKILL.md)**: System logs and diagnostic chains for Chrome Extension MV3 and complex apps.
- **[workflow-node-studio](./workflow-node-studio/SKILL.md)**: Canvas studio UI design and custom node development for React Flow workflows.
