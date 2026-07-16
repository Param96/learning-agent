import os
import json
from typing import Any, TypeVar, Type
from openai import AsyncOpenAI
from app.schemas.schemas import ParsedIntent, PlanGeneratorResponse, PlanReviserResponse, NudgeComposerResponse
from app.core.config import get_settings

T = TypeVar('T')

settings = get_settings()

# Ensure base_url doesn't have a trailing slash which causes 404s with NVIDIA API
base_url = settings.LLM_BASE_URL
if base_url and base_url.endswith("/"):
    base_url = base_url[:-1]

client = AsyncOpenAI(
    base_url=base_url,
    api_key=settings.LLM_API_KEY or "dummy-key"
)

async def call_gemini(
    system_instruction: str,
    user_message: str,
    response_schema: Type[T],
    temperature: float = 0.2
) -> T:
    """Call NVIDIA API with structured output (named call_gemini for backward compatibility)."""
    try:
        # Append JSON instruction to ensure the model returns JSON
        system_instruction += "\nYou MUST respond in valid JSON format matching the requested schema. Do not include any other text."
        
        completion = await client.chat.completions.create(
            model=settings.LLM_MODEL,
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_message}
            ],
            temperature=temperature,
            top_p=1,
            max_tokens=2048
        )
        
        content = completion.choices[0].message.content
        
        # Clean markdown if present
        if content.startswith("```json"):
            content = content.split("```json")[1].split("```")[0]
        elif content.startswith("```"):
            content = content.split("```")[1].split("```")[0]
            
        return response_schema.model_validate_json(content.strip())
        
    except Exception as e:
        print(f"Error calling NVIDIA API: {e}")
        raise e

def _get_mock_response(response_model: Type[T]) -> T:
    """Return mock response for testing without API."""
    if response_model == ParsedIntent:
        return ParsedIntent(
            domain="AWS Cloud Architecture",
            current_skill_level="beginner",
            target_outcome="AWS Solutions Architect Certification",
            timeline_weeks=8,
            constraints=["10 hours a week max"]
        )
    elif response_model == PlanGeneratorResponse:
        return PlanGeneratorResponse(
            milestones=[
                {
                    "title": "Week 1: Cloud Foundations",
                    "target_week": 1,
                    "tasks": [
                        {"title": "Introduction to Cloud Computing", "task_type": "video", "est_minutes": 45},
                        {"title": "AWS Global Infrastructure", "task_type": "reading", "est_minutes": 60},
                        {"title": "Foundations Quiz", "task_type": "quiz", "est_minutes": 30}
                    ]
                },
                {
                    "title": "Week 2: Core Concepts (Compute & Storage)",
                    "target_week": 2,
                    "tasks": [
                        {"title": "EC2 Deep Dive", "task_type": "video", "est_minutes": 60},
                        {"title": "S3 and Storage Solutions", "task_type": "project", "est_minutes": 90},
                        {"title": "Core Concepts Quiz", "task_type": "quiz", "est_minutes": 30}
                    ]
                }
            ]
        )
    elif response_model == PlanReviserResponse:
        return PlanReviserResponse(
            trigger_reason="quiz_failure",
            diff_summary="Added remedial tasks for weak areas",
            changes=[
                {
                    "change_type": "add",
                    "entity_type": "task",
                    "reason": "Add remedial content due to low quiz score"
                }
            ]
        )
    elif response_model == NudgeComposerResponse:
        return NudgeComposerResponse(
            message="Welcome back! You've made solid progress. Ready to conquer your next task?",
            suggested_action="Continue learning"
        )
    return None