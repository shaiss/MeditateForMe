from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Meditation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    script = db.Column(db.Text, nullable=False)
    audio_url = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Meditation {self.id}>'
