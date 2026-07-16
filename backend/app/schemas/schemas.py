from pydantic import BaseModel, Field, field_validator
import json
from typing import Optional, List, Any
from datetime import datetime
from enum import Enum


class GoalStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class PlanStatus(str, Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    DRAFT = "draft"


class MilestoneStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"
    DELAYED = "delayed"


class TaskType(str, Enum):
    VIDEO = "video"
    READING = "reading"
    QUIZ = "quiz"
    PROJECT = "project"


class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class ActivityEventType(str, Enum):
    STARTED = "started"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class AttemptType(str, Enum):
    QUIZ = "quiz"
    SELF_ASSESSMENT = "self_assessment"


class NudgeTriggerType(str, Enum):
    INACTIVITY = "inactivity"
    QUIZ_FAILURE = "quiz_failure"
    SCHEDULE_SLIP = "schedule_slip"
    ACCELERATION = "acceleration"


# Intent Parser schemas
class ParsedIntent(BaseModel):
    domain: str = Field(..., description="The learning domain requested by the user")
    current_skill_level: str = Field(..., description="Current skill level derived from the prompt")
    target_outcome: str = Field(..., description="Specific target outcome or certification requested")
    timeline_weeks: int = Field(..., ge=1, le=52, description="Target timeline in weeks")
    constraints: List[str] = Field(default_factory=list, description="Any constraints mentioned by the user")


class IntentParserResponse(BaseModel):
    parsed_intent: ParsedIntent


# Plan Generator schemas
class TaskConfig(BaseModel):
    title: str
    task_type: TaskType
    est_minutes: int = Field(..., ge=5, le=480)
    description: Optional[str] = None


class MilestoneConfig(BaseModel):
    title: str
    target_week: int = Field(..., ge=1)
    tasks: List[TaskConfig]


class PlanGeneratorResponse(BaseModel):
    milestones: List[MilestoneConfig]


# Plan Reviser schemas
class DiffChange(BaseModel):
    change_type: str = Field(..., description="Type of change: 'add', 'remove', 'modify', 'delay'")
    entity_type: str = Field(..., description="Entity type: 'milestone' or 'task'")
    entity_id: Optional[int] = Field(None, description="ID of existing entity (for modify/remove/delay)")
    entity_data: Optional[dict] = Field(None, description="New/updated entity data (for add/modify)")
    reason: str = Field(..., description="Why this change is being made")


class PlanReviserResponse(BaseModel):
    trigger_reason: str
    diff_summary: str
    changes: List[DiffChange]


# Nudge Composer schemas
class NudgeComposerResponse(BaseModel):
    message: str
    suggested_action: Optional[str] = None


# Request/Response schemas for API
class GoalCreate(BaseModel):
    raw_input: str


class GoalResponse(BaseModel):
    id: int
    raw_input: str
    domain: Optional[str]
    current_level: Optional[str]
    target_outcome: Optional[str]
    deadline: Optional[datetime]
    status: GoalStatus
    created_at: datetime

    class Config:
        from_attributes = True


class GoalWithIntent(BaseModel):
    id: int
    raw_input: str
    parsed_intent: Optional[ParsedIntent]
    status: GoalStatus

    class Config:
        from_attributes = True


class PlanCreate(BaseModel):
    goal_id: int


class PlanResponse(BaseModel):
    id: int
    goal_id: int
    version: int
    generated_at: datetime
    status: PlanStatus
    plan_data: dict

    @field_validator('plan_data', mode='before')
    @classmethod
    def parse_plan_data(cls, v: Any) -> dict:
        if isinstance(v, str):
            try:
                return json.loads(v)
            except:
                return {}
        return v

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: int
    milestone_id: int
    title: str
    task_type: TaskType
    est_minutes: Optional[int]
    description: Optional[str]
    status: TaskStatus
    due_date: Optional[datetime]

    class Config:
        from_attributes = True


class MilestoneResponse(BaseModel):
    id: int
    plan_id: int
    order: int
    title: str
    target_date: Optional[datetime]
    status: MilestoneStatus
    tasks: List[TaskResponse]

    class Config:
        from_attributes = True


class ActivityLogCreate(BaseModel):
    task_id: int
    event_type: ActivityEventType
    time_spent_min: Optional[int] = None


class ActivityLogResponse(BaseModel):
    id: int
    user_id: int
    task_id: int
    event_type: ActivityEventType
    timestamp: datetime
    time_spent_min: Optional[int]

    class Config:
        from_attributes = True


class AttemptCreate(BaseModel):
    task_id: int
    attempt_type: AttemptType
    score: Optional[float] = Field(None, ge=0, le=100)
    notes: Optional[str] = None


class AttemptResponse(BaseModel):
    id: int
    task_id: int
    attempt_type: AttemptType
    score: Optional[float]
    notes: Optional[str]
    submitted_at: datetime

    class Config:
        from_attributes = True


class NudgeResponse(BaseModel):
    id: int
    user_id: int
    trigger_type: NudgeTriggerType
    trigger_context: Optional[str]
    message: str
    sent_at: datetime
    dismissed: bool
    acted_on: bool

    class Config:
        from_attributes = True


class PlanRevisionResponse(BaseModel):
    id: int
    plan_id: int
    trigger: str
    trigger_data: Optional[str]
    diff_summary: dict
    reason: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


class DashboardStats(BaseModel):
    completion_percent: float
    current_streak_days: int
    time_spent_min: int
    time_planned_min: int
    upcoming_tasks_count: int
    active_milestones_count: int


class PlanOverviewResponse(BaseModel):
    plan_id: int
    domain: str
    target_outcome: str
    completion_percent: float
    status: str


class UserCreate(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str