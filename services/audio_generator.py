import os
import requests
import logging
from flask import current_app
from functools import lru_cache

# Set up logger
logger = logging.getLogger(__name__)

def get_elevenlabs_config():
    """Get ElevenLabs config from environment or Flask context"""
    try:
        # Try to get from Flask context
        elevenlabs_api_key = current_app.config.get('ELEVENLABS_API_KEY')
        voice_id = current_app.config.get('ELEVENLABS_VOICE_ID', 'sX7PMBZDfORL1SPZi4XW')
    except RuntimeError:
        # Not in Flask context, try environment variables
        elevenlabs_api_key = os.environ.get('ELEVENLABS_API_KEY')
        voice_id = os.environ.get('ELEVENLABS_VOICE_ID', 'sX7PMBZDfORL1SPZi4XW')
    
    if not elevenlabs_api_key:
        raise ValueError("ELEVENLABS_API_KEY is not set")
    
    return elevenlabs_api_key, voice_id

def generate_audio(text):
    """Generate audio from text using ElevenLabs API"""
    elevenlabs_api_key, voice_id = get_elevenlabs_config()
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": elevenlabs_api_key
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    try:
        logger.info("Sending request to ElevenLabs API")
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

        # In a production environment, you'd save this file to a cloud storage service
        # and return the URL. For this MVP, we'll save it locally.
        file_name = f"meditation_{os.urandom(8).hex()}.mp3"
        file_path = os.path.join('static', 'audio', file_name)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(response.content)

        logger.info(f"Audio saved to {file_path}")
        return f"/static/audio/{file_name}"
    except requests.exceptions.RequestException as e:
        log_error = f"Error generating audio: {e}"
        try:
            # Try to log to Flask if in context
            current_app.logger.error(log_error)
            if isinstance(e, requests.exceptions.HTTPError):
                current_app.logger.error(f"ElevenLabs API response: {e.response.text}")
        except RuntimeError:
            # Not in Flask context, use regular logger
            logger.error(log_error)
            if isinstance(e, requests.exceptions.HTTPError):
                logger.error(f"ElevenLabs API response: {e.response.text}")
        
        raise RuntimeError("Failed to generate audio. Please try again later.")
