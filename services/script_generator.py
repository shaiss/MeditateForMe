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
        
        # Try to create completion with extended timeout and error handling
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are a Wellness Coach specializing in creating meditation scripts."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.7,
                timeout=60,  # Extended timeout for API call
            )
            script = response.choices[0].message.content.strip()
            logger.info("Script generated successfully")
            return script
        except Exception as api_error:
            # Handle specific OpenAI API errors
            error_message = str(api_error)
            logger.error(f"OpenAI API error: {error_message}")
            
            if "rate limit" in error_message.lower():
                raise RuntimeError("Our meditation service is experiencing high demand. Please try again in a few minutes.")
            elif "timeout" in error_message.lower():
                raise RuntimeError("The request to our meditation service timed out. Please try again.")
            elif "token" in error_message.lower() and "maximum" in error_message.lower():
                raise RuntimeError("The meditation couldn't be generated due to complexity limits. Please try with fewer selections.")
            else:
                # Re-raise with more context
                raise RuntimeError(f"Problem generating meditation script: {error_message}")
                
    except ValueError as e:
        # Handle configuration/setup errors
        log_error = f"Configuration error in script generation: {e}"
        try:
            current_app.logger.error(log_error)
        except RuntimeError:
            logger.error(log_error)
        raise ValueError(f"Meditation service configuration error: {str(e)}")
        
    except RuntimeError as e:
        # Pass through runtime errors with logging
        log_error = f"Runtime error in script generation: {e}"
        try:
            current_app.logger.error(log_error)
        except RuntimeError:
            logger.error(log_error)
        raise
        
    except Exception as e:
        # Handle unexpected errors
        log_error = f"Unexpected error generating script: {e}"
        try:
            current_app.logger.error(log_error)
        except RuntimeError:
            logger.error(log_error)
        
        # Raise a more user-friendly error
        raise RuntimeError("An unexpected error occurred while creating your meditation script. Please try again later.")
