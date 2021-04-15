from flask_sqlalchemy import SQLAlchemy
import json
from settings import app

db = SQLAlchemy(app)

class Animal(db.Model):
    __tablename__ = 'animals'
    id = db.Column(db.Integer, primary_key=True)
    center_id = db.Column(db.Integer, nullable=False)
    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(180), nullable=True)
    age = db.Column(db.Integer, nullable=False)
    species = db.Column(db.String(80), nullable=False)
    price = db.Column(db.Float, nullable=True)

    def detailed_json(self):
        return {'id': self.id, 'center_id': self.center_id, 'name': self.name, 'description': self.description,
                'age': self.age, 'species': self.species, 'price': self.price}

    def short_json(self):
        return {'name': self.name, 'id': self.id, 'species': self.species}

    def get_all_animals():
        return [Animal.short_json(animal) for animal in Animal.query.all()]

    def get_animal_by_id(_id):
        return Animal.query.filter_by(id=_id).first()

    def get_animals_by_center_id(_center_id):
        return [Animal.short_json(animal) for animal in Animal.query.filter_by(center_id=_center_id).all()]

    def get_animals_count_by_species(_species):
        count = Animal.query.filter_by(species=_species).count()
        return count

    def get_animals_by_species(_species):
        result = []
        for animal in Animal.query.filter_by(species=_species).all():
            result.append({'animal name': animal.name, 'id': animal.id, 'specie': _species})
        return result

    def add_animal(_center_id, _name, _description, _age, _species, _price):
        new_animal = Animal(center_id=_center_id, name=_name, description=_description, age=_age, species=_species,
                            price=_price)
        db.session.add(new_animal)
        db.session.commit()
        return new_animal.id

    def update_animal(_id, _center_id, _name, _description, _age, _species, _price):
        animal_for_update = Animal.query.filter_by(id=_id).first()
        animal_for_update.center_id = _center_id
        animal_for_update.name = _name
        animal_for_update.description = _description
        animal_for_update.age = _age
        animal_for_update.species = _species
        animal_for_update.price = _price
        db.session.commit()

    def delete_animal(_id):
        is_successful = Animal.query.filter_by(id=_id).delete()
        db.session.commit()
        return bool(is_successful)
