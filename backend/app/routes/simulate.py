from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.core.database import get_db
from app.models.models import Milestone, MilestoneStatus

router = APIRouter(prefix="/activity", tags=["activity"])


@router.post("/simulate-slip")
async def simulate_schedule_slip(db: Session = Depends(get_db)):
    """Simulate a schedule slip by marking a milestone as overdue."""
    # Find the first pending milestone and set its date to yesterday
    milestone = db.query(Milestone).filter(
        Milestone.status == MilestoneStatus.PENDING
    ).first()
    
    if milestone:
        milestone.target_date = datetime.now() - timedelta(days=1)
        milestone.status = MilestoneStatus.DELAYED
        db.commit()
    
    return {"status": "success", "milestone_id": milestone.id if milestone else None}