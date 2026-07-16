from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List

from app.core.database import get_db
from app.schemas.schemas import (
    ActivityLogCreate, ActivityLogResponse,
    AttemptCreate, AttemptResponse,
    NudgeResponse
)
from app.models.models import (
    ActivityLog, ActivityEventType, Task, TaskStatus, Milestone, MilestoneStatus,
    Attempt, AttemptType, Nudge, NudgeTriggerType, User
)
from app.agents.nudge_composer import compose_nudge
from app.core.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/activity", tags=["activity"])


@router.post("/log", response_model=ActivityLogResponse, status_code=status.HTTP_201_CREATED)
async def log_activity(log_create: ActivityLogCreate, db: Session = Depends(get_db)):
    """Log a task activity event."""
    # Verify task exists
    task = db.query(Task).filter(Task.id == log_create.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Create activity log
    activity_log = ActivityLog(
        user_id=1,  # TODO: Get from auth
        task_id=log_create.task_id,
        event_type=log_create.event_type,
        time_spent_min=log_create.time_spent_min
    )
    
    db.add(activity_log)
    
    # Update task status if completed
    if log_create.event_type == ActivityEventType.COMPLETED:
        task.status = TaskStatus.COMPLETED
        # Update milestone status if all tasks done
        _update_milestone_status(task.milestone_id, db)
    
    db.commit()
    db.refresh(activity_log)
    
    return activity_log


def _update_milestone_status(milestone_id: int, db: Session):
    """Update milestone status based on task completion."""
    milestone = db.query(Milestone).filter(Milestone.id == milestone_id).first()
    if not milestone:
        return
    
    tasks = db.query(Task).filter(Task.milestone_id == milestone_id).all()
    completed_tasks = [t for t in tasks if t.status == TaskStatus.COMPLETED]
    
    if len(completed_tasks) == len(tasks) and len(tasks) > 0:
        milestone.status = MilestoneStatus.DONE
    elif len(completed_tasks) > 0:
        milestone.status = MilestoneStatus.ACTIVE
    
    db.commit()


@router.post("/attempts", response_model=AttemptResponse, status_code=status.HTTP_201_CREATED)
async def submit_attempt(attempt_create: AttemptCreate, db: Session = Depends(get_db)):
    """Submit a quiz or self-assessment attempt."""
    task = db.query(Task).filter(Task.id == attempt_create.task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    attempt = Attempt(
        task_id=attempt_create.task_id,
        attempt_type=attempt_create.attempt_type,
        score=attempt_create.score,
        notes=attempt_create.notes
    )
    
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    # Check if this triggers a nudge (low score)
    if attempt.score is not None and attempt.score < (settings.QUIZ_FAILURE_THRESHOLD * 100):
        await _create_quiz_failure_nudge(attempt, task, db)
    
    return attempt


async def _create_quiz_failure_nudge(attempt: Attempt, task: Task, db: Session):
    """Create a nudge when quiz score is below threshold."""
    trigger_context = {
        "task_id": task.id,
        "task_title": task.title,
        "score": attempt.score,
        "threshold": settings.QUIZ_FAILURE_THRESHOLD * 100
    }
    
    recent_history = f"Scored {attempt.score}% on {task.title}"
    
    try:
        nudge_response = await compose_nudge(
            trigger_type="quiz_failure",
            trigger_context=trigger_context,
            recent_history=recent_history
        )
    except Exception:
        nudge_response = None
    
    nudge = Nudge(
        user_id=1,  # TODO: Get from auth
        trigger_type=NudgeTriggerType.QUIZ_FAILURE,
        trigger_context=str(trigger_context),
        message=nudge_response.message if nudge_response else f"You scored {attempt.score}% on {task.title}. Let's review the material.",
        acted_on=False
    )
    
    db.add(nudge)
    db.commit()
    
    return nudge


@router.get("/nudges", response_model=List[NudgeResponse])
async def get_nudges(db: Session = Depends(get_db)):
    """Get all nudges for the current user."""
    nudges = db.query(Nudge).filter(
        Nudge.user_id == 1  # TODO: Get from auth
    ).order_by(Nudge.sent_at.desc()).all()
    
    return nudges


@router.post("/nudges/{nudge_id}/dismiss", response_model=NudgeResponse)
async def dismiss_nudge(nudge_id: int, db: Session = Depends(get_db)):
    """Dismiss a nudge."""
    nudge = db.query(Nudge).filter(Nudge.id == nudge_id).first()
    
    if not nudge:
        raise HTTPException(status_code=404, detail="Nudge not found")
    
    nudge.dismissed = True
    db.commit()
    db.refresh(nudge)
    
    return nudge


@router.post("/nudges/{nudge_id}/act", response_model=NudgeResponse)
async def act_on_nudge(nudge_id: int, db: Session = Depends(get_db)):
    """Mark a nudge as acted upon."""
    nudge = db.query(Nudge).filter(Nudge.id == nudge_id).first()
    
    if not nudge:
        raise HTTPException(status_code=404, detail="Nudge not found")
    
    nudge.acted_on = True
    db.commit()
    db.refresh(nudge)
    
    return nudge


@router.post("/check-triggers")
async def check_triggers(db: Session = Depends(get_db)):
    """Manually trigger check for all trigger conditions (for demo/testing)."""
    user_id = 1  # TODO: Get from auth
    triggers_found = []
    
    # Check inactivity
    last_activity = db.query(ActivityLog).filter(
        ActivityLog.user_id == user_id
    ).order_by(ActivityLog.timestamp.desc()).first()
    
    days_since_activity = 0
    if last_activity:
        days_since_activity = (datetime.now() - last_activity.timestamp).days
    
    if days_since_activity >= settings.NUDGE_INACTIVITY_DAYS:
        nudge = Nudge(
            user_id=user_id,
            trigger_type=NudgeTriggerType.INACTIVITY,
            trigger_context=f"{days_since_activity} days since last activity",
            message=f"Welcome back! It's been {days_since_activity} days. Ready to continue your learning journey?",
            acted_on=False
        )
        db.add(nudge)
        triggers_found.append({"type": "inactivity", "days": days_since_activity})
    
    # Check schedule slips (overdue milestones)
    overdue_milestones = db.query(Milestone).join(Task).filter(
        Milestone.target_date < datetime.now(),
        Milestone.status != MilestoneStatus.DONE
    ).all()
    
    for milestone in overdue_milestones:
        nudge = Nudge(
            user_id=user_id,
            trigger_type=NudgeTriggerType.SCHEDULE_SLIP,
            trigger_context=f"Milestone '{milestone.title}' was due on {milestone.target_date}",
            message=f"The '{milestone.title}' milestone is overdue. Let's adjust your plan.",
            acted_on=False
        )
        db.add(nudge)
        triggers_found.append({"type": "schedule_slip", "milestone": milestone.title})
    
    db.commit()
    
    return {"triggers_found": triggers_found, "nudges_created": len(triggers_found)}