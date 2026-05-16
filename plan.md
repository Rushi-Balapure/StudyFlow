# StudyFlow Build Plan

## Project Goal
Build a Python-first, single-user, local-first agentic study companion that:
- creates personalized study plans,
- teaches concepts adaptively,
- evaluates progress and retention,
- updates memory + knowledge graph state,
- and enforces focus with warning + soft-block controls.

## Locked Decisions
- Interface: CLI-first MVP
- Model backend: OpenAI-compatible configurable provider
- Memory model: `mem0` primary memory + `SQLite` for app state/evals
- User scope: single-user for now
- Focus enforcement v1: both websites/domains and desktop apps/windows
- Study content scope: user-provided content + URLs + generated lessons
- Priority metrics: learning adaptation and agent correctness

## MVP Definition (End-to-End Study Loop)
A user can run one complete local session in CLI:
1. Enter a goal, duration, and content source(s).
2. Receive a prerequisite-aware plan.
3. Learn a concept via tutor agent.
4. Complete quiz/evaluation.
5. Get mastery update and feedback.
6. Continue adaptive loop (advance/remediate).
7. Receive focus warnings and soft-block actions when distracted.
8. Persist state for next session continuity.

## Architecture (Initial)
- Orchestration: LangGraph state machine
- Agents: planner, tutor, evaluator, memory, focus
- Knowledge model: topic graph + mastery map
- Memory: mem0 semantic memory
- Deterministic persistence: SQLite for sessions/evals/graph metadata
- Interface: CLI app commands + session runner
- Evaluation harness: replayable scenarios for adaptation + routing checks

## Milestones

## M1 - Foundation
Target outcomes:
- Project scaffold and dependency setup
- Config loading (`.env`) and provider abstraction
- Base typed state and orchestration skeleton
- CLI entrypoint and basic command flow

Deliverables:
- `src/studyflow/` package layout
- `graph/state.py`, `graph/graph.py`, `graph/nodes.py` placeholders
- `config.py` and provider client wrapper
- `cli.py` with `start-session` command

Acceptance checks:
- CLI starts a mock session without crashing
- Graph executes a no-op loop with typed state

## M2 - Core Study Session Loop
Target outcomes:
- Real planner -> tutor -> evaluator loop
- Session state persisted in SQLite

Deliverables:
- Goal intake schema
- Plan generation node
- Tutor lesson generation node
- Quiz generation/scoring node
- Session repository and basic schema

Acceptance checks:
- One full session loop works end-to-end
- Session transcript + scores are stored

## M3 - Adaptive Difficulty + Mastery Engine
Target outcomes:
- Dynamic difficulty and progression logic based on performance

Deliverables:
- Mastery calculation strategy
- Difficulty adjustment policy
- Advance/reinforce/remediate routing logic

Acceptance checks:
- Weak performance triggers remediation
- Strong performance advances difficulty

## M4 - Memory + Knowledge Graph Integration
Target outcomes:
- Persistent personalization and graph-aware planning

Deliverables:
- mem0 integration layer
- Topic graph representation + prerequisite queries
- Planner uses graph + mastery for sequencing

Acceptance checks:
- Prior mistakes influence lesson generation
- Prerequisite violations are prevented in plan

## M5 - Focus Agent (Warn + Soft-Block)
Target outcomes:
- Local distraction monitoring and interventions

Deliverables:
- Focus policy config (allowlist/blocklist)
- Website/domain monitoring hooks
- Desktop app/window monitoring hooks
- Warning + soft-block adapters and event logging

Acceptance checks:
- Distraction event creates warning
- Repeated event triggers soft-block action
- Study loop remains stable after intervention

## M6 - Evaluation Harness
Target outcomes:
- Regression-safe measurement for adaptation + agent correctness

Deliverables:
- Offline scenario fixtures
- Session replay runner
- Agent routing/assertion tests
- Adaptation quality metrics report

Acceptance checks:
- Harness catches routing regressions
- Harness reports adaptation trends across fixtures

## Implementation Backlog (Rolling)
- [ ] Finalize repo skeleton and package structure
- [ ] Define typed shared state contract
- [ ] Build provider abstraction for OpenAI-compatible backends
- [ ] Implement SQLite schema for sessions/evaluations/mastery
- [ ] Integrate mem0 retrieval/write policies
- [ ] Implement planner/tutor/evaluator node prompts and parsers
- [ ] Implement adaptive routing logic
- [ ] Implement knowledge graph utilities
- [ ] Implement focus policy engine and detectors
- [ ] Build evaluation harness fixtures and CI test target

## Non-Goals (Current Phase)
- Multi-user auth and tenant isolation
- Cloud deployment and distributed scale
- Hard OS lockout enforcement

## Risks and Mitigations
- Focus hooks vary by OS -> isolate adapters behind interfaces.
- LLM output instability -> structured outputs + validation + retries.
- Memory drift -> keep deterministic SQLite truth for metrics/evals.
- Prompt regressions -> protect with replay-based evaluation harness.

## Update Protocol
How we keep this file current:
1. Mark backlog items as done as soon as completed.
2. Add new tasks discovered during implementation.
3. Record milestone status (`not started`, `in progress`, `done`).
4. Update acceptance checks when requirements evolve.
