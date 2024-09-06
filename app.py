from flask import Flask, render_template, request, jsonify, send_from_directory
from models import db, Meditation
from services.script_generator import generate_script
from services.audio_generator import generate_audio
from config import Config
import os
import logging

app = Flask(__name__)
app.config.from_object(Config)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Ensure OPENAI_API_KEY is set in the app config
if 'OPENAI_API_KEY' not in app.config or not app.config['OPENAI_API_KEY']:
    app.config['OPENAI_API_KEY'] = os.environ.get('OPENAI_API_KEY')
    if not app.config['OPENAI_API_KEY']:
        app.logger.error("OPENAI_API_KEY is not set in the environment or app configuration")
        raise ValueError("OPENAI_API_KEY is not set in the environment or app configuration")

# Ensure ELEVENLABS_API_KEY is set in the app config
if 'ELEVENLABS_API_KEY' not in app.config or not app.config['ELEVENLABS_API_KEY']:
    app.config['ELEVENLABS_API_KEY'] = os.environ.get('ELEVENLABS_API_KEY')
    if not app.config['ELEVENLABS_API_KEY']:
        app.logger.error("ELEVENLABS_API_KEY is not set in the environment or app configuration")
        raise ValueError("ELEVENLABS_API_KEY is not set in the environment or app configuration")

# Ensure ELEVENLABS_VOICE_ID is set in the app config
if 'ELEVENLABS_VOICE_ID' not in app.config or not app.config['ELEVENLABS_VOICE_ID']:
    app.config['ELEVENLABS_VOICE_ID'] = os.environ.get('ELEVENLABS_VOICE_ID', 'sX7PMBZDfORL1SPZi4XW')

db.init_app(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate-meditation', methods=['POST'])
def generate_meditation():
    data = request.json
    emotions = data.get('emotions', [])
    goals = data.get('goals', [])
    outcomes = data.get('outcomes', [])

    if not emotions or not goals or not outcomes:
        return jsonify({'error': 'Please provide at least one emotion, goal, and outcome.'}), 400

    try:
        script = generate_script(goals, emotions, outcomes)
        audio_url = generate_audio(script)

        meditation = Meditation(script=script, audio_url=audio_url)
        db.session.add(meditation)
        db.session.commit()

        return jsonify({
            'id': meditation.id,
            'script': script,
            'audio_url': audio_url
        }), 201
    except ValueError as e:
        app.logger.error(f"Value error in generate_meditation: {str(e)}")
        return jsonify({'error': str(e)}), 400
    except RuntimeError as e:
        app.logger.error(f"Runtime error in generate_meditation: {str(e)}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in generate_meditation: {str(e)}")
        return jsonify({'error': 'An unexpected error occurred. Please try again later.'}), 500

@app.route('/api/meditation/<int:meditation_id>', methods=['GET'])
def get_meditation(meditation_id):
    meditation = Meditation.query.get_or_404(meditation_id)
    return jsonify({
        'id': meditation.id,
        'script': meditation.script,
        'audio_url': meditation.audio_url
    })

@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
