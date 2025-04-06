from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

db = SQLAlchemy()

class Meditation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=True)  # Optional title for saved meditations
    script = db.Column(db.Text, nullable=False)
    audio_url = db.Column(db.String(255), nullable=False)
    duration_seconds = db.Column(db.Integer, nullable=True)  # Duration in seconds
    
    # Metadata fields for user selections
    emotions = db.Column(db.Text, nullable=True)  # JSON string of emotions
    goals = db.Column(db.Text, nullable=True)     # JSON string of goals
    outcomes = db.Column(db.Text, nullable=True)  # JSON string of outcomes
    
    # Save this in library
    saved = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Meditation {self.id}>'
    
    def set_emotions(self, emotions_list):
        """Store emotions as JSON string"""
        if emotions_list:
            self.emotions = json.dumps(emotions_list)
    
    def get_emotions(self):
        """Get emotions as Python list"""
        if self.emotions:
            return json.loads(self.emotions)
        return []
    
    def set_goals(self, goals_list):
        """Store goals as JSON string"""
        if goals_list:
            self.goals = json.dumps(goals_list)
    
    def get_goals(self):
        """Get goals as Python list"""
        if self.goals:
            return json.loads(self.goals)
        return []
    
    def set_outcomes(self, outcomes_list):
        """Store outcomes as JSON string"""
        if outcomes_list:
            self.outcomes = json.dumps(outcomes_list)
    
    def get_outcomes(self):
        """Get outcomes as Python list"""
        if self.outcomes:
            return json.loads(self.outcomes)
        return []
    
    def to_dict(self):
        """Convert meditation to dictionary for API responses"""
        return {
            'id': self.id,
            'title': self.title,
            'script': self.script,
            'audio_url': self.audio_url,
            'duration_seconds': self.duration_seconds,
            'emotions': self.get_emotions(),
            'goals': self.get_goals(),
            'outcomes': self.get_outcomes(),
            'saved': self.saved,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
