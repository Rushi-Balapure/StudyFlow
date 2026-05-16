# StudyFlow Agents

## System Overview
StudyFlow is a single-user, local-first, agentic AI study companion.

Core loop:
1. Plan a study session from a goal.
2. Teach one concept at a time.
3. Evaluate learning with adaptive quizzes.
4. Update memory, mastery, and knowledge graph.
5. Enforce focus with warnings and soft-block actions.
6. Re-plan the next step based on performance.

## Agent Catalog

### 1) Planner Agent
Purpose:
- Builds and revises study plans using learner goals, available time, prerequisites, and mastery.

Inputs:
- Learner goal and scope
- Session duration
- Topic graph + prerequisite edges
- Current mastery state
- Recent evaluator outputs

Outputs:
- Ordered lesson sequence
- Per-lesson objective and target difficulty
- Remediation path for weak concepts

Success criteria:
- Plan is prerequisite-aware and executable in current session time.

### 2) Tutor Agent
Purpose:
- Teaches the current concept and adapts explanation style to learner performance and preference.

Inputs:
- Current topic
- Planner objective
- Retrieved memory context
- Learner mistakes/weak patterns

Outputs:
- Structured explanation
- Worked example(s)
- Quick comprehension checks
- Suggested next concept risk level

Success criteria:
- Explanation clarity and relevance improve quiz outcomes over time.

### 3) Evaluator Agent
Purpose:
- Generates and scores assessments to estimate understanding and retention.

Inputs:
- Current topic
- Target difficulty from planner
- Tutor lesson context
- Past errors and confidence trend

Outputs:
- Quiz set (MCQ/short answer)
- Score + rubric feedback
- Mastery delta and confidence score
- Recommendation: advance, reinforce, or remediate

Success criteria:
- Scores are consistent, actionable, and useful for adaptation.

### 4) Memory Agent
Purpose:
- Maintains long-term learner context and retrieves relevant study history.

Storage model:
- `mem0` as primary semantic/personal memory
- `SQLite` as deterministic app-state/eval store

Inputs:
- Session interactions
- Evaluator outcomes
- Learner preferences

Outputs:
- Retrieved context for planner/tutor
- Updated learner profile signals
- Persistent records for analytics and replay

Success criteria:
- Useful context retrieval with deterministic auditability.

### 5) Focus Agent
Purpose:
- Enforces focus during active study sessions.

V1 enforcement mode:
- Warning + soft-block (not hard OS lockout)
- Coverage for both websites/domains and desktop apps/windows

Inputs:
- Active study session state
- Allowlist/blocklist policy
- Local activity/event signals

Outputs:
- Warning events
- Soft-block actions
- Intervention logs
- Session focus signal

Success criteria:
- Reduces distractions without breaking the study loop.

## Shared State Contract (Initial)
All agents read/write through a shared orchestration state and durable stores.

Primary state domains:
- `session`: id, goal, timing, current topic
- `plan`: steps, objectives, target difficulty
- `learning`: mastery map, confidence, retention estimates
- `evaluation`: quiz items, responses, scores, feedback
- `memory`: retrieved context and profile traits
- `focus`: events, warnings, soft-block actions

## Orchestration Contract
Initial LangGraph-style flow:
1. `planner` creates/updates next study step.
2. `focus` initializes session policy checks.
3. `tutor` delivers lesson content.
4. `evaluator` assesses understanding.
5. `memory` persists/retrieves context updates.
6. `focus` logs interventions during session.
7. `planner` adapts next step based on evaluator + memory.
8. Loop until session objective is complete.

## Guardrails
- Single-user only in current phase.
- Local-first execution.
- OpenAI-compatible provider abstraction for model backends.
- Keep agent outputs structured for replay and evaluation.

## File Ownership (Planned)
- `graph/graph.py`: orchestration graph assembly
- `graph/state.py`: typed shared state
- `graph/nodes.py`: planner/tutor/evaluator/memory/focus nodes
- `memory/`: mem0 integration + retrieval policies
- `store/`: SQLite models, migrations, repository layer
- `focus/`: policy engine + detectors + soft-block adapters
- `evals/`: evaluation harness and benchmark scenarios
