from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
import json

from app.core.database import get_db
from app.schemas.schemas import (
    PlanRevisionResponse, PlanResponse
)
from app.models.models import (
    Plan, PlanRevision, Milestone, Task,
    PlanStatus, MilestoneStatus, TaskStatus
)
from app.agents.plan_reviser import revise_plan

router = APIRouter(prefix="/plans", tags=["plans"])


@router.post("/{plan_id}/revise", response_model=PlanRevisionResponse)
async def revise_plan_endpoint(plan_id: int, trigger: str, trigger_data: dict, db: Session = Depends(get_db)):
    """Revise a plan based on trigger (quiz failure, schedule slip, etc.)."""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    # Get current plan structure
    current_plan_data = json.loads(plan.plan_data)
    
    # Call LLM to get revision
    try:
        revision_response = await revise_plan(current_plan_data, trigger, trigger_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to revise plan: {str(e)}")
    
    # Create revision record
    revision = PlanRevision(
        plan_id=plan_id,
        trigger=trigger,
        trigger_data=json.dumps(trigger_data),
        diff_summary=json.dumps(revision_response.changes),
        reason=revision_response.diff_summary
    )
    
    db.add(revision)
    
    # Apply changes to create new plan version
    new_version = Plan(
        goal_id=plan.goal_id,
        version=plan.version + 1,
        status=PlanStatus.ACTIVE,
        plan_data=apply_plan_changes(plan.plan_data, revision_response.changes)
    )
    
    db.add(new_version)
    
    # Mark old plan as superseded
    plan.status = PlanStatus.SUPERSEDED
    
    db.commit()
    db.refresh(revision)
    
    return revision


def apply_plan_changes(current_plan_json: str, changes: list) -> str:
    """Apply changes to plan data and return updated JSON."""
    import json
    
    plan_data = json.loads(current_plan_json)
    
    for change in changes:
        if change.change_type == "add" and change.entity_type == "task":
            # Add task to appropriate milestone
            # Simplified: add to first milestone
            if plan_data["milestones"]:
                new_task = {
                    "title": change.entity_data.get("title", "Remedial task"),
                    "task_type": change.entity_data.get("task_type", "reading"),
                    "est_minutes": change.entity_data.get("est_minutes", 30),
                    "description": change.entity_data.get("description", "")
                }
                plan_data["milestones"][0]["tasks"].append(new_task)
        
        elif change.change_type == "delay" and change.entity_type == "milestone":
            # Delay milestone by specified days
            # Simplified implementation
            pass
        
        elif change.change_type == "remove" and change.entity_type == "task":
            # Remove task (simplified)
            pass
    
    return json.dumps(plan_data)


@router.get("/{plan_id}/revisions")
async def get_plan_revisions(plan_id: int, db: Session = Depends(get_db)):
    """Get all revisions for a plan."""
    plan = db.query(Plan).filter(Plan.id == plan_id).first()
    
    if not plan:
        raise HTTPException(status_code=404, detail="Plan not found")
    
    revisions = db.query(PlanRevision).filter(
        PlanRevision.plan_id == plan_id
    ).order_by(PlanRevision.created_at.desc()).all()
    
    return revisions


@router.get("/{plan_id}/diff/{revision_id}")
async def get_plan_diff(plan_id: int, revision_id: int, db: Session = Depends(get_db)):
    """Get diff between plan versions."""
    revision = db.query(PlanRevision).filter(
        PlanRevision.id == revision_id,
        PlanRevision.plan_id == plan_id
    ).first()
    
    if not revision:
        raise HTTPException(status_code=404, detail="Revision not found")
    
    # Get previous version
    prev_version = db.query(Plan).filter(
        Plan.goal_id == revision.plan_id,
        Plan.version == revision.plan.version - 1
    ).first()
    
    if not prev_version:
        return {
            "reason": revision.reason,
            "changes": json.loads(revision.diff_summary),
            "previous_plan": None,
            "new_plan": json.loads(revision.plan.plan_data)
        }
    
    return {
        "reason": revision.reason,
        "changes": json.loads(revision.diff_summary),
        "previous_plan": json.loads(prev_version.plan_data),
        "new_plan": json.loads(revision.plan.plan_data)
    }