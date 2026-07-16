from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
import json

from app.core.database import get_db
from app.schemas.schemas import (
    GoalCreate, GoalResponse, GoalWithIntent, ParsedIntent
)
from app.models.models import Goal, GoalStatus, User
from app.agents.intent_parser import parse_intent

router = APIRouter(prefix="/goals", tags=["goals"])


@router.post("/", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal(goal_create: GoalCreate, db: Session = Depends(get_db)):
    """Create a new goal and parse the intent."""
    # Parse intent using LLM
    try:
        parsed_intent = await parse_intent(goal_create.raw_input)
    except Exception as e:
        print(f"ERROR: LLM parsing failed: {str(e)}")
        raise HTTPException(status_code=400, detail=f"LLM Error: {str(e)}")
    
    # Create goal record
    goal = Goal(
        user_id=1,  # TODO: Get from auth
        raw_input=goal_create.raw_input,
        domain=parsed_intent.domain if parsed_intent else None,
        current_level=parsed_intent.current_skill_level if parsed_intent else None,
        target_outcome=parsed_intent.target_outcome if parsed_intent else None,
        status=GoalStatus.DRAFT
    )
    
    db.add(goal)
    db.commit()
    db.refresh(goal)
    
    return goal


@router.get("/", response_model=List[GoalResponse])
async def list_goals(db: Session = Depends(get_db)):
    """List all goals for the current user."""
    goals = db.query(Goal).filter(Goal.user_id == 1).all()  # TODO: Get from auth
    return goals


@router.get("/{goal_id}", response_model=GoalWithIntent)
async def get_goal(goal_id: int, db: Session = Depends(get_db)):
    """Get a specific goal with its parsed intent."""
    goal = db.query(Goal).filter(Goal.id == goal_id, Goal.user_id == 1).first()  # TODO: Get from auth
    
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")
    
    return goal