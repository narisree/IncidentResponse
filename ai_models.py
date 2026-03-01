import anthropic
from google import genai
from google.genai import types
from prompt_template import SYSTEM_PROMPT, build_user_prompt


def generate_with_claude(api_key: str, spl_query: str, description: str, log_sources: list, severity: str) -> str:
    """Generate IR plan using Claude API."""
    client = anthropic.Anthropic(api_key=api_key)
    
    user_prompt = build_user_prompt(spl_query, description, log_sources, severity)
    
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": user_prompt}
        ]
    )
    
    return message.content[0].text


def generate_with_gemini(api_key: str, spl_query: str, description: str, log_sources: list, severity: str) -> str:
    """Generate IR plan using Google Gemini API (new SDK)."""
    client = genai.Client(api_key=api_key)
    
    user_prompt = build_user_prompt(spl_query, description, log_sources, severity)
    
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            max_output_tokens=8000,
            temperature=0.3,
        )
    )
    
    return response.text
