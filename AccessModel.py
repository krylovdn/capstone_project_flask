from flask_sqlalchemy import SQLAlchemy
import json
from settings import app

db = SQLAlchemy(app)

class Access(db.Model):
    __tablename__ = 'access'
    id = db.Column(db.Integer, primary_key=True)
    center_id = db.Column(db.Integer, nullable=False)
    access_timestamp = db.Column(db.DateTime, nullable=False)

    def add_record(_center_id, _access_timestamp):
        new_record = Access(center_id=_center_id, access_timestamp=_access_timestamp)
        db.session.add(new_record)
        db.session.commit()

    def json(self):
        return {'center_id': self.center_id, 'access_timestamp': self.access_timestamp}

    def get_all_records():
        return [Access.json(record) for record in Access.query.all()]