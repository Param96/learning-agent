from typing import Dict, Any
from app.schemas.schemas import PlanGeneratorResponse
from app.agents.llm_client import call_gemini

async def generate_plan(parsed_intent: Dict[str, Any]) -> PlanGeneratorResponse:
    """Generate a learning plan from parsed intent using NVIDIA API."""
    system_instruction = (
        "You are an elite learning designer. Your job is to create a highly detailed, "
        "structured, and actionable learning plan based on the user's parsed intent. "
        "The plan should be broken down into weekly milestones. Each milestone should have "
        "a set of specific tasks. Task types can only be: 'video', 'reading', 'quiz', or 'project'. "
        "Ensure the timeline matches the user's requested timeline_weeks if possible. "
        "You must return ONLY a JSON object that matches exactly this structure:\n"
        "{\n"
        "  \"milestones\": [\n"
        "    {\n"
        "      \"title\": \"string\",\n"
        "      \"target_week\": 1,\n"
        "      \"tasks\": [\n"
        "        {\n"
        "          \"title\": \"string\",\n"
        "          \"task_type\": \"video\",\n"
        "          \"est_minutes\": 60,\n"
        "          \"description\": \"string (detailed description of what the task involves)\"\n"
        "        }\n"
        "      ]\n"
        "    }\n"
        "  ]\n"
        "}\n"
        "Do NOT return the schema itself. Return the populated data."
    )
    
    user_message = f"Please generate a learning plan for the following intent:\n{parsed_intent}"
    
    return await call_gemini(
        system_instruction=system_instruction,
        user_message=user_message,
        response_schema=PlanGeneratorResponse,
        temperature=0.3
    )