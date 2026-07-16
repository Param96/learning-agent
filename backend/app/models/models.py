from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, ForeignKey, Float, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum

from app.core.database import Base


class GoalStatus(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class PlanStatus(str, enum.Enum):
    ACTIVE = "active"
    SUPERSEDED = "superseded"
    DRAFT = "draft"


class MilestoneStatus(str, enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    DONE = "done"
    DELAYED = "delayed"


class TaskType(str, enum.Enum):
    VIDEO = "video"
    READING = "reading"
    QUIZ = "quiz"
    PROJECT = "project"


class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class ActivityEventType(str, enum.Enum):
    STARTED = "started"
    COMPLETED = "completed"
    SKIPPED = "skipped"


class AttemptType(str, enum.Enum):
    QUIZ = "quiz"
    SELF_ASSESSMENT = "self_assessment"


class NudgeTriggerType(str, enum.Enum):
    INACTIVITY = "inactivity"
    QUIZ_FAILURE = "quiz_failure"
    SCHEDULE_SLIP = "schedule_slip"
    ACCELERATION = "acceleration"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    goals = relationship("Goal", back_populates="user")
    activity_logs = relationship("ActivityLog", back_populates="user")
    nudges = relationship("Nudge", back_populates="user")


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    raw_input = Column(Text, nullable=False)
    domain = Column(String(255))
    current_level = Column(String(100))
    target_outcome = Column(Text)
    deadline = Column(DateTime(timezone=True))
    status = Column(Enum(GoalStatus), default=GoalStatus.DRAFT)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    user = relationship("User", back_populates="goals")
    plans = relationship("Plan", back_populates="goal")


class Plan(Base):
    __tablename__ = "plans"

    id = Column(Integer, primary_key=True, index=True)
    goal_id = Column(Integer, ForeignKey("goals.id"), nullable=False)
    
    version = Column(Integer, default=1)
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(Enum(PlanStatus), default=PlanStatus.ACTIVE)
    
    # JSON blob storing the full plan structure (milestones with nested tasks)
    plan_data = Column(Text)  # Will be JSON string
    
    goal = relationship("Goal", back_populates="plans")
    milestones = relationship("Milestone", back_populates="plan", cascade="all, delete-orphan")
    revisions = relationship("PlanRevision", back_populates="plan", cascade="all, delete-orphan")


class Milestone(Base):
    __tablename__ = "milestones"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    
    order = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    target_date = Column(DateTime(timezone=True))
    status = Column(Enum(MilestoneStatus), default=MilestoneStatus.PENDING)
    
    plan = relationship("Plan", back_populates="milestones")
    tasks = relationship("Task", back_populates="milestone", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    milestone_id = Column(Integer, ForeignKey("milestones.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    task_type = Column(Enum(TaskType), nullable=False)
    est_minutes = Column(Integer)
    description = Column(Text)
    status = Column(Enum(TaskStatus), default=TaskStatus.PENDING)
    due_date = Column(DateTime(timezone=True))
    
    milestone = relationship("Milestone", back_populates="tasks")
    attempts = relationship("Attempt", back_populates="task", cascade="all, delete-orphan")
    activity_logs = relationship("ActivityLog", back_populates="task", cascade="all, delete-orphan")


class Attempt(Base):
    __tablename__ = "attempts"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    
    attempt_type = Column(Enum(AttemptType), nullable=False)
    score = Column(Float)
    notes = Column(Text)
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    
    task = relationship("Task", back_populates="attempts")


class ActivityLog(Base):
    __tablename__ = "activity_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    task_id = Column(Integer, ForeignKey("tasks.id"), nullable=False)
    
    event_type = Column(Enum(ActivityEventType), nullable=False)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    time_spent_min = Column(Integer)
    
    user = relationship("User", back_populates="activity_logs")
    task = relationship("Task", back_populates="activity_logs")


class Nudge(Base):
    __tablename__ = "nudges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    trigger_type = Column(Enum(NudgeTriggerType), nullable=False)
    trigger_context = Column(Text)
    message = Column(Text, nullable=False)
    sent_at = Column(DateTime(timezone=True), server_default=func.now())
    dismissed = Column(Boolean, default=False)
    acted_on = Column(Boolean, default=False)
    
    user = relationship("User", back_populates="nudges")


class PlanRevision(Base):
    __tablename__ = "plan_revisions"

    id = Column(Integer, primary_key=True, index=True)
    plan_id = Column(Integer, ForeignKey("plans.id"), nullable=False)
    
    trigger = Column(String(100), nullable=False)
    trigger_data = Column(Text)  # JSON string with context
    diff_summary = Column(Text)  # JSON string with before/after changes
    reason = Column(Text)  # Human-readable explanation
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    plan = relationship("Plan", back_populates="revisions")