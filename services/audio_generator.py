import os
import requests
from flask import current_app

def generate_audio(text):
    elevenlabs_api_key = current_app.config.get('ELEVENLABS_API_KEY')
    voice_id = current_app.config.get('ELEVENLABS_VOICE_ID', 'sX7PMBZDfORL1SPZi4XW')
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
        response = requests.post(url, json=data, headers=headers)
        response.raise_for_status()

        # In a production environment, you'd save this file to a cloud storage service
        # and return the URL. For this MVP, we'll save it locally.
        file_name = f"meditation_{os.urandom(8).hex()}.mp3"
        file_path = os.path.join('static', 'audio', file_name)
        
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            f.write(response.content)

        return f"/static/audio/{file_name}"
    except requests.exceptions.RequestException as e:
        current_app.logger.error(f"Error generating audio: {e}")
        if isinstance(e, requests.exceptions.HTTPError):
            current_app.logger.error(f"ElevenLabs API response: {e.response.text}")
        raise RuntimeError("Failed to generate audio. Please try again later.")
