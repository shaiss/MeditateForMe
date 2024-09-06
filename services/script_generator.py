import os
from openai import OpenAI
from flask import current_app

def get_openai_client():
    api_key = current_app.config.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set in the application configuration")
    return OpenAI(api_key=api_key)

def generate_prompt(goals, emotions, outcomes):
    return f"""Create a meditation script addressing the following:
    Goals: {', '.join(goals)}
    Emotions: {', '.join(emotions)}
    Desired Outcomes: {', '.join(outcomes)}
    
    The script should be supportive and guide the listener through a mindful experience.
    Start with a warm welcome message about the purpose of the meditation.
    Keep the script concise, around 300-400 words."""

def generate_script(goals, emotions, outcomes):
    prompt = generate_prompt(goals, emotions, outcomes)
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a Wellness Coach specializing in creating meditation scripts."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Error generating script: {e}")
        raise
