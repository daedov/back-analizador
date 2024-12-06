from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Transcription(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.Text, nullable=False)  # Sin límite de caracteres
    text = db.Column(db.Text, nullable=False)  # También sin límite de caracteres
