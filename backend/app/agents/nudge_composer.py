import json
from typing import Any, Optional
from app.core.config import get_settings
from app.schemas.schemas import NudgeComposerResponse

settings = get_settings()


async def compose_nudge(trigger_type: str, trigger_context: dict, recent_history: str) -> NudgeComposerResponse:
    """Compose a contextual nudge message."""
    # Mock response for MVP
    return NudgeComposerResponse(
        message=f"Welcome back! {recent_history}. Ready to continue?",
        suggested_action="Continue learning"
    )