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
        
        # Add timeout and error handling for the API call
        try:
            response = requests.post(
                url, 
                json=data, 
                headers=headers,
                timeout=90  # Extended timeout for audio generation
            )
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
            
        except requests.exceptions.Timeout:
            error_msg = "The audio generation service timed out. Please try again with a shorter meditation script."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
        except requests.exceptions.HTTPError as http_err:
            # Detailed error handling for different HTTP error codes
            error_response = http_err.response
            status_code = error_response.status_code
            error_detail = "Unknown error"
            
            try:
                error_json = error_response.json()
                error_detail = error_json.get('detail', error_json.get('message', 'Unknown error'))
            except:
                # If we can't parse JSON, use the text response
                error_detail = error_response.text[:100] if error_response.text else "Unknown error"
            
            log_message = f"ElevenLabs API HTTP Error {status_code}: {error_detail}"
            logger.error(log_message)
            
            if status_code == 401:
                raise ValueError("Authentication failed with the audio service. Please check your API key.")
            elif status_code == 429:
                raise RuntimeError("Audio generation quota exceeded. Please try again later.")
            elif status_code >= 500:
                raise RuntimeError("The audio service is currently experiencing issues. Please try again later.")
            else:
                raise RuntimeError(f"Failed to generate audio: {error_detail}")
                
        except requests.exceptions.ConnectionError:
            error_msg = "Could not connect to the audio generation service. Please check your internet connection and try again."
            logger.error(error_msg)
            raise RuntimeError(error_msg)
            
    except ValueError as e:
        # Handle configuration errors
        log_error = f"Configuration error in audio generation: {e}"
        try:
            current_app.logger.error(log_error)
        except RuntimeError:
            logger.error(log_error)
        raise
        
    except RuntimeError as e:
        # Pass through runtime errors with logging
        log_error = f"Runtime error in audio generation: {e}"
        try:
            current_app.logger.error(log_error)
        except RuntimeError:
            logger.error(log_error)
        raise
        
    except Exception as e:
        # Handle unexpected errors
        log_error = f"Unexpected error generating audio: {str(e)}"
        try:
            current_app.logger.error(log_error)
        except RuntimeError:
            logger.error(log_error)
        
        raise RuntimeError("An unexpected error occurred while creating your meditation audio. Please try again later.")
