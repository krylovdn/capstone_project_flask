from flask_sqlalchemy import SQLAlchemy
import json
from settings import app

db = SQLAlchemy(app)

class Species(db.Model):
    __tablename__ = 'species'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    description = db.Column(db.String(180), nullable=False)
    price = db.Column(db.Float, nullable=False)

    def get_all_species():
        return Species.query.all()

    def get_species_by_id(_id):
        return Species.query.filter_by(id=_id).first()

    def get_species_by_name(_name):
        return Species.query.filter_by(name=_name).first()

    def add_specie(_name, _description, _price):
        new_specie = Species(name=_name, description=_description, price=_price)
        db.session.add(new_specie)
        db.session.commit()
        return new_specie.id