import os
import logging
from openai import OpenAI
from flask import current_app

# Set up logger
logger = logging.getLogger(__name__)

def get_openai_client():
    """Get OpenAI client from environment or Flask context"""
    try:
        # Try to get from Flask context
        api_key = current_app.config.get('OPENAI_API_KEY')
    except RuntimeError:
        # Not in Flask context, try environment variables
        api_key = os.environ.get('OPENAI_API_KEY')
    
    if not api_key:
        raise ValueError("OPENAI_API_KEY is not set")
    
    return OpenAI(api_key=api_key)

def generate_prompt(goals, emotions, outcomes):
    """Generate a prompt for the meditation script"""
    return f"""Create a meditation script addressing the following:
    Goals: {', '.join(goals)}
    Emotions: {', '.join(emotions)}
    Desired Outcomes: {', '.join(outcomes)}
    
    The script should be supportive and guide the listener through a mindful experience.
    Start with a warm welcome message about the purpose of the meditation.
    Keep the script concise, around 300-400 words."""

def generate_script(goals, emotions, outcomes):
    """Generate a meditation script using OpenAI"""
    prompt = generate_prompt(goals, emotions, outcomes)
    try:
        logger.info(f"Generating script for goals: {goals}, emotions: {emotions}, outcomes: {outcomes}")
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
        script = response.choices[0].message.content.strip()
        logger.info("Script generated successfully")
        return script
    except Exception as e:
        log_error = f"Error generating script: {e}"
        try:
            # Try to log to Flask if in context
            current_app.logger.error(log_error)
        except RuntimeError:
            # Not in Flask context, use regular logger
            logger.error(log_error)
        
        # Re-raise the exception to be handled by caller
        raise
