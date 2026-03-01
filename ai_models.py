import anthropic
from groq import Groq
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


def generate_with_groq(api_key: str, spl_query: str, description: str, log_sources: list, severity: str, model: str = "llama-3.3-70b-versatile") -> str:
    """Generate IR plan using Groq API (free tier)."""
    client = Groq(api_key=api_key)
    
    user_prompt = build_user_prompt(spl_query, description, log_sources, severity)
    
    chat_completion = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=0.3,
        max_tokens=8000,
    )
    
    return chat_completion.choices[0].message.content
