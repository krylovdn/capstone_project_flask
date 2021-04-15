from flask_sqlalchemy import SQLAlchemy
import json
from settings import app

db = SQLAlchemy(app)

class Center(db.Model):
    __tablename__ = 'center'
    id = db.Column(db.Integer, primary_key=True)
    login = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    address = db.Column(db.String(150), nullable=False)

    def short_json(self):
        return {'id': self.id, 'login': self.login}

    def detailed_json(self):
        return {'id': self.id, 'login': self.login, 'address': self.address}

    def add_center(_login, _password, _address):
        new_center = Center(login=_login, password=_password, address=_address)
        db.session.add(new_center)
        db.session.commit()
        return new_center.id

    def get_all_centers():
        return [Center.short_json(center) for center in Center.query.all()]

    def get_center_by_login(_login):
        return Center.query.filter_by(login=_login).first()

    def get_center_by_login_and_password(_login, _password):
        return Center.query.filter_by(login=_login).filter_by(password=_password).first()

    def get_center_by_id(_id):
        result = Center.query.filter_by(id=_id).first()
        return result
