from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_sqlalchemy import SQLAlchemy
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
    app.logger.info(f"Received meditation generation request with data: {data}")
    
    # Detailed validation with specific error messages
    if not data:
        app.logger.error("No JSON data received in request")
        return jsonify({'error': 'No data received. Please provide meditation parameters.'}), 400
    
    # Sanitize inputs
    try:
        emotions = [e.strip() for e in data.get('emotions', []) if e and e.strip()]
        goals = [g.strip() for g in data.get('goals', []) if g and g.strip()]
        outcomes = [o.strip() for o in data.get('outcomes', []) if o and o.strip()]
    except Exception as e:
        app.logger.error(f"Input data parsing error: {e}")
        return jsonify({'error': 'Invalid input format. Please refresh and try again.'}), 400

    # Check for empty values after sanitization
    validation_errors = []
    if not emotions:
        validation_errors.append("Please provide at least one emotion.")
    if not goals:
        validation_errors.append("Please provide at least one goal.")
    if not outcomes:
        validation_errors.append("Please provide at least one desired outcome.")
        
    # Check for too many selections
    total_selections = len(emotions) + len(goals) + len(outcomes)
    if total_selections > 15:  # Arbitrary limit to prevent overloading API
        validation_errors.append("Please select fewer options for better results (maximum 15 total selections).")
    
    if validation_errors:
        error_message = " ".join(validation_errors)
        app.logger.error(f"Validation error: {error_message}")
        return jsonify({
            'error': error_message,
            'validation_errors': validation_errors
        }), 400

    try:
        app.logger.info(f"Generating script with emotions: {emotions}, goals: {goals}, outcomes: {outcomes}")
        script = generate_script(goals, emotions, outcomes)
        app.logger.info(f"Script generated successfully ({len(script)} characters)")
        
        # Validate script length before audio generation to prevent issues with ElevenLabs
        if len(script) > 5000:  # ElevenLabs has character limits
            app.logger.warning(f"Script too long ({len(script)} chars), truncating")
            script = script[:4950] + "... [Truncated for length]"
        
        app.logger.info("Generating audio")
        audio_url = generate_audio(script)
        app.logger.info("Audio generated successfully")

        # Create meditation with all metadata
        meditation = Meditation(
            script=script, 
            audio_url=audio_url,
            # Approximate duration (1 word = ~0.4 seconds in spoken audio)
            duration_seconds=int(len(script.split()) * 0.4)
        )
        
        # Store selection metadata
        meditation.set_emotions(emotions)
        meditation.set_goals(goals)
        meditation.set_outcomes(outcomes)
        
        # Generate a title based on selections
        emotion_str = emotions[0] if emotions else "Calm"
        goal_str = goals[0] if goals else "Mindfulness"
        meditation.title = f"{emotion_str} {goal_str} Meditation"
        
        db.session.add(meditation)
        db.session.commit()
        app.logger.info(f"Meditation saved to database with ID: {meditation.id}")

        # Use the to_dict method to create a consistent response
        return jsonify(meditation.to_dict()), 201
    except ValueError as e:
        app.logger.error(f"Value error in generate_meditation: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_type': 'value_error'
        }), 400
    except RuntimeError as e:
        app.logger.error(f"Runtime error in generate_meditation: {str(e)}")
        return jsonify({
            'error': str(e),
            'error_type': 'runtime_error',
            'message': 'There was a problem with the meditation generation service.'
        }), 500
    except Exception as e:
        app.logger.error(f"Unexpected error in generate_meditation: {str(e)}", exc_info=True)
        return jsonify({
            'error': 'An unexpected error occurred. Please try again later.',
            'error_type': 'unexpected_error',
            'message': 'Our servers encountered an issue while generating your meditation.'
        }), 500

@app.route('/api/meditation/<int:meditation_id>', methods=['GET'])
def get_meditation(meditation_id):
    meditation = Meditation.query.get_or_404(meditation_id)
    return jsonify(meditation.to_dict())

@app.route('/static/audio/<path:filename>')
def serve_audio(filename):
    return send_from_directory('static/audio', filename)

@app.route('/api/reset-db', methods=['POST'])
def reset_db():
    """Reset the database (development only)"""
    try:
        with app.app_context():
            db.drop_all()
            db.create_all()
        app.logger.info("Database reset successfully")
        return jsonify({'message': 'Database reset successfully'}), 200
    except Exception as e:
        app.logger.error(f"Error resetting database: {str(e)}")
        return jsonify({'error': f"Error resetting database: {str(e)}"}), 500

if __name__ == '__main__':
    with app.app_context():
        # Just create tables that don't exist yet
        db.create_all()
    app.run(host='0.0.0.0', port=5000)
