from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional
import json
from datetime import datetime, timedelta

from app.core.database import get_db
from app.schemas.schemas import (
    PlanCreate, PlanResponse, PlanStatus,
    MilestoneResponse, TaskResponse, TaskStatus, MilestoneStatus,
    DashboardStats, PlanOverviewResponse
)
from app.models.models import (
    Plan, Goal, Milestone, Task, User, ActivityLog, Nudge, PlanRevision,
    GoalStatus
)
from app.agents.plan_generator import generate_plan

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("/", response_model=PlanResponse, status_code=status.HTTP_201_CREATED)
async def create_plan(plan_create: PlanCreate, db: Session = Depends(get_db)):
    """Generate a learning plan for a goal."""
    # Get the goal
    goal = db.query(Goal).filter(
        Goal.id == plan_create.goal_id,
        Goal.user_id == 1  # TODO: Get from auth
    ).first()
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    # Mark previous active plans as superseded
    db.query(Plan).filter(
        Plan.goal_id == plan_create.goal_id,
        Plan.status == PlanStatus.ACTIVE
    ).update({"status": PlanStatus.SUPERSEDED})
    
    # Generate plan using LLM
    intent_data = {
        "domain": goal.domain,
        "current_skill_level": goal.current_level,
        "target_outcome": goal.target_outcome,
        "timeline_weeks": 8,  # Default or calculate from deadline
        "constraints": []
    }
    
    try:
        plan_response = await generate_plan(intent_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate plan: {str(e)}")
    
    # Create plan record
    plan = Plan(
        goal_id=plan_create.goal_id,
        version=1,
        status=PlanStatus.ACTIVE,
        plan_data=json.dumps(plan_response.model_dump())
    )
    
    db.add(plan)
    db.flush()  # Get plan ID
    
    # Create milestones and tasks from plan data
    for milestone_data in plan_response.milestones:
        milestone = Milestone(
            plan_id=plan.id,
            order=milestone_data.target_week,
            title=milestone_data.title,
            target_date=datetime.now() + timedelta(weeks=milestone_data.target_week),
            status=MilestoneStatus.PENDING
        )
        db.add(milestone)
        db.flush()
        
        for task_data in milestone_data.tasks:
            task = Task(
                milestone_id=milestone.id,
                title=task_data.title,
                task_type=task_data.task_type,
                est_minutes=task_data.est_minutes,
                description=task_data.description,
                status=TaskStatus.PENDING
            )
            db.add(task)
    
    db.commit()
    db.refresh(plan)
    
    # Update goal status
    goal.status = GoalStatus.ACTIVE
    db.commit()
    
    return plan


@router.get("/overview", response_model=List[PlanOverviewResponse])
async def get_plans_overview(db: Session = Depends(get_db)):
    """Get overview of all active plans for the user."""
    user_id = 1
    active_plans = db.query(Plan).filter(
        Plan.status == PlanStatus.ACTIVE,
        Plan.goal_id == Goal.id
    ).join(Goal).filter(Goal.user_id == user_id).order_by(Plan.id.desc()).all()
    
    result = []
    for plan in active_plans:
        # Calculate completion %
        tasks = db.query(Task).join(Milestone).filter(Milestone.plan_id == plan.id).all()
        completed_tasks = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
        total_tasks = len(tasks)
        completion_percent = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
        
        result.append({
            "plan_id": plan.id,
            "domain": plan.goal.domain or "Custom Plan",
            "target_outcome": plan.goal.target_outcome or "General",
            "completion_percent": completion_percent,
            "status": plan.status
        })
    return result


@router.get("/active/milestones", response_model=List[MilestoneResponse])
async def get_active_plan_milestones(plan_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all milestones for the active plan or a specific plan."""
    user_id = 1
    if plan_id:
        active_plan = db.query(Plan).filter(Plan.id == plan_id).join(Goal).filter(Goal.user_id == user_id).first()
    else:
        active_plan = db.query(Plan).filter(
            Plan.status == PlanStatus.ACTIVE,
            Plan.goal_id == Goal.id
        ).join(Goal).filter(Goal.user_id == user_id).order_by(Plan.id.desc()).first()
    
    if not active_plan:
        return []
        
    milestones = db.query(Milestone).filter(Milestone.plan_id == active_plan.id).order_by(Milestone.order).all()
    return milestones


@router.get("/active/revisions", response_model=List[dict])
async def get_active_plan_revisions(plan_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get all revisions for the active plan or a specific plan."""
    user_id = 1
    if plan_id:
        active_plan = db.query(Plan).filter(Plan.id == plan_id).join(Goal).filter(Goal.user_id == user_id).first()
    else:
        active_plan = db.query(Plan).filter(
            Plan.status == PlanStatus.ACTIVE,
            Plan.goal_id == Goal.id
        ).join(Goal).filter(Goal.user_id == user_id).order_by(Plan.id.desc()).first()
    
    if not active_plan:
        return []
        
    from app.schemas.schemas import PlanRevisionResponse
    revisions = db.query(PlanRevision).filter(PlanRevision.plan_id == active_plan.id).order_by(PlanRevision.created_at.desc()).all()
    
    # Quick serialization to dict to avoid circular imports / missing response models if needed
    result = []
    for r in revisions:
        result.append({
            "id": r.id,
            "plan_id": r.plan_id,
            "trigger": r.trigger,
            "diff_summary": json.loads(r.diff_summary) if r.diff_summary else [],
            "reason": r.reason,
            "created_at": r.created_at.isoformat()
        })
    return result


@router.get("/{plan_id}", response_model=PlanResponse)
async def get_plan(plan_id: int, db: Session = Depends(get_db)):
    """Get a specific plan with milestones and tasks."""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    return plan


@router.get("/{plan_id}/milestones", response_model=List[MilestoneResponse])
async def get_plan_milestones(plan_id: int, db: Session = Depends(get_db)):
    """Get all milestones for a plan."""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    milestones = db.query(Milestone).filter(Milestone.plan_id == plan_id).order_by(Milestone.order).all()
    return milestones


@router.get("/active/dashboard", response_model=DashboardStats)
async def get_dashboard_stats(plan_id: Optional[int] = None, db: Session = Depends(get_db)):
    """Get dashboard statistics for active plan or a specific plan."""
    user_id = 1  # TODO: Get from auth
    
    # Get active plan
    if plan_id:
        active_plan = db.query(Plan).filter(Plan.id == plan_id).join(Goal).filter(Goal.user_id == user_id).first()
    else:
        active_plan = db.query(Plan).filter(
            Plan.status == PlanStatus.ACTIVE,
            Plan.goal_id == Goal.id
        ).join(Goal).filter(Goal.user_id == user_id).order_by(Plan.id.desc()).first()
    
    if not active_plan:
        return DashboardStats(
            completion_percent=0.0,
            current_streak_days=0,
            time_spent_min=0,
            time_planned_min=0,
            upcoming_tasks_count=0,
            active_milestones_count=0
        )
    
    # Calculate stats
    milestones = db.query(Milestone).filter(Milestone.plan_id == active_plan.id).all()
    tasks = db.query(Task).join(Milestone).filter(Milestone.plan_id == active_plan.id).all()
    
    completed_tasks = db.query(Task).join(Milestone).filter(
        Milestone.plan_id == active_plan.id,
        Task.status == TaskStatus.COMPLETED
    ).count()
    
    total_tasks = len(tasks)
    completion_percent = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0.0
    
    # Time spent
    time_spent = db.query(func.sum(ActivityLog.time_spent_min)).filter(
        ActivityLog.user_id == user_id
    ).scalar() or 0
    
    # Time planned
    time_planned = sum(t.est_minutes for t in tasks if t.est_minutes)
    
    # Upcoming tasks
    upcoming_tasks = db.query(Task).join(Milestone).filter(
        Milestone.plan_id == active_plan.id,
        Task.status.in_([TaskStatus.PENDING, TaskStatus.IN_PROGRESS])
    ).count()
    
    # Active milestones
    active_milestones = db.query(Milestone).filter(
        Milestone.plan_id == active_plan.id,
        Milestone.status == MilestoneStatus.ACTIVE
    ).count()
    
    # Streak calculation
    from datetime import timedelta
    dates_query = db.query(func.date(ActivityLog.timestamp)).filter(
        ActivityLog.user_id == user_id
    ).distinct().order_by(func.date(ActivityLog.timestamp).desc()).all()
    
    dates = [datetime.strptime(d[0], '%Y-%m-%d').date() for d in dates_query if d[0]]
    
    current_streak = 0
    today = datetime.now().date()
    
    if dates:
        # If the most recent activity was today or yesterday, we have an active streak
        if dates[0] == today or dates[0] == today - timedelta(days=1):
            current_streak = 1
            current_date = dates[0]
            for d in dates[1:]:
                if d == current_date - timedelta(days=1):
                    current_streak += 1
                    current_date = d
                else:
                    break
    
    return DashboardStats(
        completion_percent=completion_percent,
        current_streak_days=current_streak,
        time_spent_min=time_spent,
        time_planned_min=time_planned,
        upcoming_tasks_count=upcoming_tasks,
        active_milestones_count=active_milestones
    )

@router.delete("/{plan_id}")
def delete_plan(plan_id: int, db: Session = Depends(get_db)):
    """Delete a plan and all its associated milestones and tasks."""
    user_id = 1  # TODO: Get from auth
    
    # Ensure the plan belongs to the user
    plan = db.query(Plan).join(Goal).filter(
        Plan.id == plan_id,
        Goal.user_id == user_id
    ).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
        
    db.delete(plan)
    db.commit()
    
    return {"message": "Plan deleted successfully"}