"""
Seed script for demo data - creates a realistic AWS Solutions Architect scenario
with pre-loaded history to demonstrate triggers instantly.
"""
import json
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.core.database import Base
from app.models.models import (
    User, Goal, Plan, Milestone, Task, Attempt,
    ActivityLog, Nudge, PlanRevision,
    GoalStatus, PlanStatus, MilestoneStatus, TaskStatus,
    TaskType, ActivityEventType, AttemptType, NudgeTriggerType
)
from app.core.security import get_password_hash

DATABASE_URL = "sqlite:///./learning_agent.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def seed():
    db = SessionLocal()
    
    try:
        # Create user
        user = User(
            email="demo@learning.agent",
            hashed_password=get_password_hash("demo123")
        )
        db.add(user)
        db.flush()
        print(f"Created user: {user.email}")
        
        # Create goal
        goal = Goal(
            user_id=user.id,
            raw_input="I want to pass the AWS Solutions Architect Associate exam in 8 weeks. I can study 10 hours per week, mainly on evenings and weekends.",
            domain="AWS Cloud",
            current_level="beginner",
            target_outcome="AWS Solutions Architect Associate certification",
            deadline=datetime.now() + timedelta(weeks=8),
            status=GoalStatus.ACTIVE
        )
        db.add(goal)
        db.flush()
        print(f"Created goal: {goal.target_outcome}")
        
        # Create plan with milestones
        plan_data = {
            "milestones": [
                {
                    "title": "Week 1-2: Cloud Foundations",
                    "target_week": 2,
                    "tasks": [
                        {"title": "Introduction to Cloud Computing", "task_type": "video", "est_minutes": 60},
                        {"title": "AWS Global Infrastructure", "task_type": "reading", "est_minutes": 45},
                        {"title": "Cloud Foundations Quiz", "task_type": "quiz", "est_minutes": 30}
                    ]
                },
                {
                    "title": "Week 3-4: Core AWS Services",
                    "target_week": 4,
                    "tasks": [
                        {"title": "EC2 Fundamentals", "task_type": "video", "est_minutes": 90},
                        {"title": "VPC and Networking", "task_type": "video", "est_minutes": 90},
                        {"title": "S3 Storage Options", "task_type": "reading", "est_minutes": 45},
                        {"title": "Core Services Quiz", "task_type": "quiz", "est_minutes": 30}
                    ]
                },
                {
                    "title": "Week 5-6: Advanced Topics",
                    "target_week": 6,
                    "tasks": [
                        {"title": "IAM and Security", "task_type": "video", "est_minutes": 75},
                        {"title": "Database Services", "task_type": "video", "est_minutes": 60},
                        {"title": "Load Balancing & Auto Scaling", "task_type": "project", "est_minutes": 120},
                        {"title": "Advanced Topics Quiz", "task_type": "quiz", "est_minutes": 30}
                    ]
                },
                {
                    "title": "Week 7-8: Exam Prep",
                    "target_week": 8,
                    "tasks": [
                        {"title": "Practice Exam 1", "task_type": "quiz", "est_minutes": 90},
                        {"title": "Review Weak Areas", "task_type": "reading", "est_minutes": 60},
                        {"title": "Practice Exam 2", "task_type": "quiz", "est_minutes": 90},
                        {"title": "Final Review", "task_type": "project", "est_minutes": 120}
                    ]
                }
            ]
        }
        
        plan = Plan(
            goal_id=goal.id,
            version=1,
            status=PlanStatus.ACTIVE,
            plan_data=json.dumps(plan_data)
        )
        db.add(plan)
        db.flush()
        print(f"Created plan version {plan.version}")
        
        # Create milestones and tasks
        for milestone_data in plan_data["milestones"]:
            milestone = Milestone(
                plan_id=plan.id,
                order=milestone_data["target_week"],
                title=milestone_data["title"],
                target_date=datetime.now() + timedelta(weeks=milestone_data["target_week"]),
                status=MilestoneStatus.ACTIVE if milestone_data["target_week"] <= 2 else MilestoneStatus.PENDING
            )
            db.add(milestone)
            db.flush()
            
            for task_data in milestone_data["tasks"]:
                task = Task(
                    milestone_id=milestone.id,
                    title=task_data["title"],
                    task_type=task_data["task_type"],
                    est_minutes=task_data["est_minutes"],
                    status=TaskStatus.COMPLETED if "Quiz" in task_data["title"] and "Core" in milestone_data["title"] else TaskStatus.PENDING
                )
                db.add(task)
        
        # Add some activity history
        # Completed tasks
        core_quiz = db.query(Task).filter(Task.title == "Core Services Quiz").first()
        if core_quiz:
            activity = ActivityLog(
                user_id=user.id,
                task_id=core_quiz.id,
                event_type=ActivityEventType.COMPLETED,
                timestamp=datetime.now() - timedelta(days=1),
                time_spent_min=35
            )
            db.add(activity)
            
            # Low quiz score attempt
            attempt = Attempt(
                task_id=core_quiz.id,
                attempt_type=AttemptType.QUIZ,
                score=45.0,
                notes="Struggled with VPC concepts - need to review networking",
                submitted_at=datetime.now() - timedelta(days=1)
            )
            db.add(attempt)
            
            # Create nudge for quiz failure
            nudge = Nudge(
                user_id=user.id,
                trigger_type=NudgeTriggerType.QUIZ_FAILURE,
                trigger_context=json.dumps({"task": "Core Services Quiz", "score": 45}),
                message="The VPC concepts can be tricky. Let's add some remedial content to build confidence before moving forward.",
                acted_on=False
            )
            db.add(nudge)
        
        # Recent activity
        recent_task = db.query(Task).filter(Task.title == "EC2 Fundamentals").first()
        if recent_task:
            activity = ActivityLog(
                user_id=user.id,
                task_id=recent_task.id,
                event_type=ActivityEventType.STARTED,
                timestamp=datetime.now() - timedelta(hours=2),
                time_spent_min=0
            )
            db.add(activity)
        
        db.commit()
        print("\n✅ Seed data created successfully!")
        print(f"\nDemo scenario: AWS Solutions Architect preparation")
        print(f"  - User has completed some foundational content")
        print(f"  - Scored 45% on Core Services Quiz (below 60% threshold)")
        print(f"  - Nudge created for VPC remediation")
        print(f"\nUse the debug controls to simulate additional triggers.")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error seeding database: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()