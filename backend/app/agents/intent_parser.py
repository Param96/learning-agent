from app.schemas.schemas import ParsedIntent
from app.agents.llm_client import call_gemini

async def parse_intent(raw_goal: str) -> ParsedIntent:
    """Parse raw goal text into structured intent using NVIDIA API."""
    system_instruction = (
        "You are an expert educational consultant. Your job is to extract and structure "
        "the user's learning goal into a specific domain, their current skill level, "
        "the target outcome, a realistic timeline in weeks, and any constraints they mention. "
        "You MUST extract the domain from the user's input. "
        "You must return ONLY a JSON object that matches exactly this structure:\n"
        "{\n"
        "  \"domain\": \"string\",\n"
        "  \"current_skill_level\": \"string\",\n"
        "  \"target_outcome\": \"string\",\n"
        "  \"timeline_weeks\": 8,\n"
        "  \"constraints\": [\"string\"]\n"
        "}\n"
        "Do NOT return the schema itself. Return the populated data."
    )
    
    user_message = f"Please parse this learning goal:\n{raw_goal}"
    
    return await call_gemini(
        system_instruction=system_instruction,
        user_message=user_message,
        response_schema=ParsedIntent,
        temperature=0.1
    )