# AI-Powered Personal Learning Agent (MVP)

A closed-loop personal learning agent that adapts to your progress in real-time.

## Quick Start

### Backend

```bash
cd backend
pip install -e .
cp .env.example .env
# Add your ANTHROPIC_API_KEY to .env
python init_db.py
python seed_db.py
uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm run dev
```

Visit http://localhost:3000

## Demo Scenario

The seed script creates an AWS Solutions Architect preparation scenario:
- User has completed foundational content
- Scored 45% on Core Services Quiz (below 60% threshold)
- Nudge created for VPC remediation

Use the **Debug Controls** (bottom-right) to simulate:
- 3 days inactivity
- Low quiz score
- Schedule slip
- Early task completion

## Architecture

### Backend (FastAPI)
- **Models**: User, Goal, Plan, Milestone, Task, Attempt, ActivityLog, Nudge, PlanRevision
- **Agents**: IntentParser, PlanGenerator, PlanReviser, NudgeComposer
- **Triggers**: Inactivity, QuizFailure, ScheduleSlip, Acceleration

### Frontend (Next.js)
- **Goal Intake**: Parse user's learning goal
- **Dashboard**: Progress tracking, activity log, nudges
- **Plan Diff**: Visible before/after when plan adapts
- **Debug Controls**: Simulate triggers for demo

## Key Features

1. **Intent Parsing**: Raw goal → structured learning parameters
2. **Plan Generation**: Week-by-week milestones with tasks
3. **Activity Tracking**: Log progress, submit quiz scores
4. **Trigger Detection**: Rule-based detection of trouble states
5. **Plan Revision**: Visible diff when plan adapts
6. **Contextual Nudges**: Specific messages based on actual state

## API Endpoints

- `POST /goals` - Create learning goal
- `POST /plans` - Generate learning plan
- `GET /plans/active/dashboard` - Dashboard stats
- `POST /activity/log` - Log task activity
- `POST /activity/attempts` - Submit quiz
- `GET /activity/nudges` - Get nudges
- `POST /plans/{id}/revise` - Revise plan
- `POST /activity/check-triggers` - Manually check triggers

## Tech Stack

- **Backend**: FastAPI, SQLAlchemy, Pydantic v2
- **Frontend**: Next.js 15, React, Tailwind
- **LLM**: Anthropic Claude (structured JSON outputs)
- **DB**: SQLite (dev), Postgres (prod)

## Design Tokens

- Paper: `#F7F5F0`
- Graphite: `#232323`
- Signal (progress): `#2F6F4F`
- Flag (trouble): `#B5482E`
- Line: `#D8D3C8`

Typography: JetBrains Mono + Inter