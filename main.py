from flask import Flask, jsonify, request, Response
import json
from settings import *
import jwt
import datetime
from functools import wraps
from CenterModel import Center
from AccessModel import Access
from AnimalsModel import Animal
from SpeciesModel import Species
import logging


logging.basicConfig(level=logging.INFO, filename=app.config['LOG_FILE_NAME'], format='%(asctime)s:%(message)s')


@app.route('/register', methods=['POST'])
def register():
    request_data = request.get_json()
    if not validate_register_request(request_data):
        invalid_register_request_error_message = {
            "error": "invalid center",
            "helpString": "Register request should contain login, password and address values"
        }
        response = Response(json.dumps(invalid_register_request_error_message), 400, mimetype='application/json')
        return response

    if Center.get_center_by_login(request_data['login']) is None:
        new_id = Center.add_center(request_data['login'], request_data['password'], request_data['address'])
        response = Response("", 201, mimetype='application/json')
        logging.info('POST /register centers id:{}'.format(new_id))
        return response
    else:
        duplicate_login_error_message = {
            "error": "invalid center",
            "helpString": "center with same login already exists"
        }
        response = Response(json.dumps(duplicate_login_error_message), 400, mimetype='application/json')
        return response


@app.route('/login', methods=['POST'])
def get_token():
    request_data = request.get_json()
    login = str(request_data['login'])
    password = str(request_data['password'])
    center = Center.get_center_by_login_and_password(login, password)
    if center is None:
        return Response('', 401, mimetype='application/json')
    else:
        expiration_date = datetime.datetime.utcnow() + datetime.timedelta(seconds=100)
        token = jwt.encode({'exp': expiration_date, 'center_id': center.id}, app.config['SECRET_KEY'], algorithm='HS256')
        Access.add_record(center.id, datetime.datetime.utcnow())
        return token


@app.route('/centers', methods=['GET'])
def get_all_centers():
    return jsonify({'centers': Center.get_all_centers()})


@app.route('/centers/<int:id>')
def get_center_by_id(id):
    center = Center.get_center_by_id(id)
    if center is None:
        no_such_center_error_message = {
            "error": "center not found",
            "helpString": "there is no center with such id in database"
        }
        response = Response(json.dumps(no_such_center_error_message), 404, mimetype='application/json')
        return response
    else:
        return jsonify({'id': center.id, 'login': center.login, 'address': center.address,
                        'animals': Animal.get_animals_by_center_id(id)})


@app.route('/animals', methods=['GET'])
def get_all_animals():
    return jsonify({'animals': Animal.get_all_animals()})


@app.route('/animals/<int:id>')
def get_animal_by_id(id):
    animal = Animal.get_animal_by_id(id)
    if animal is None:
        no_such_animal_error_message = {
            "error": "animal not found",
            "helpString": "there is no animal with such id in database"
        }
        response = Response(json.dumps(no_such_animal_error_message), 404, mimetype='application/json')
        return response
    else:
        return jsonify(Animal.detailed_json(animal))


@app.route('/species', methods=['GET'])
def get_all_species():
    species = Species.get_all_species()
    result = {}
    for specie in species:
        result[specie.name] = Animal.get_animals_count_by_species(specie.name)
    return jsonify(result)


@app.route('/species/<int:id>')
def get_specie_by_id(id):
    specie = Species.get_species_by_id(id)
    if specie is None:
        no_such_specie_error_message = {
            "error": "specie not found",
            "helpString": "there is no specie with such id in database"
        }
        response = Response(json.dumps(no_such_specie_error_message), 404, mimetype='application/json')
        return response
    else:
        return jsonify(Animal.get_animals_by_species(specie.name))


@app.route('/species', methods=['POST'])
def add_specie():
    center_id = get_id_from_token(request.args.get('token'))
    if center_id is None:
        return jsonify({'error': 'invalid token'}), 401
    request_data = request.get_json()
    if not validate_specie(request_data):
        invalid_specie_creation_request_error_message = {
            "error": "invalid specie",
            "helpString": "specie request should contain name, description and price (flat format) values"
        }
        response = Response(json.dumps(invalid_specie_creation_request_error_message), 400, mimetype='application/json')
        return response
    if Species.get_species_by_name(request_data['name']) is None:
        new_id = Species.add_specie(request_data['name'], request_data['description'], float(request_data['price']))
        response = Response("", 201, mimetype='application/json')
        logging.info('POST /species specie_id:{} center_id:{}'.format(new_id, center_id))
        return response
    else:
        duplicate_specie_error_message = {
            "error": "invalid specie",
            "helpString": "specie with same name already exists"
        }
        response = Response(json.dumps(duplicate_specie_error_message), 400, mimetype='application/json')
        return response


@app.route('/animals', methods=['POST'])
def add_animal():
    center_id = get_id_from_token(request.args.get('token'))
    if center_id is None:
        return jsonify({'error': 'invalid token'}), 401
    request_data = request.get_json()
    if not validate_animal(request_data):
        invalid_animal_creation_request_error_message = {
            "error": "invalid animal",
            "helpString": "animal request should contain center_id, name, age and species values. "
                          "Price and age should be correct formatted"
        }
        response = Response(json.dumps(invalid_animal_creation_request_error_message), 400, mimetype='application/json')
        return response
    if Center.get_center_by_id(int(request_data['center_id'])) is None:
        no_such_center_id_error_message = {
            "error": "invalid center",
            "helpString": "center with such id does not exists"
        }
        response = Response(json.dumps(no_such_center_id_error_message), 400, mimetype='application/json')
        return response
    elif Species.get_species_by_name(request_data['species']) is None:
        no_such_specie_error_message = {
            "error": "invalid specie",
            "helpString": "specie with such name does not exists"
        }
        response = Response(json.dumps(no_such_specie_error_message), 400, mimetype='application/json')
        return response
    else:
        new_id = Animal.add_animal(request_data['center_id'], request_data['name'], request_data['description'],
                          int(request_data['age']), request_data['species'], float(request_data['price']))
        response = Response("", 201, mimetype='application/json')
        logging.info('POST /animals animal_id:{} center_id:{}'.format(new_id, center_id))
        return response


@app.route('/animals/<int:id>', methods=['PUT'])
def update_animal(id):
    request_data = request.get_json()
    center_id = get_id_from_token(request.args.get('token'))
    if center_id is None:
        return jsonify({'error': 'invalid token'}), 401
    if not validate_animal(request_data):
        invalid_animal_creation_request_error_message = {
            "error": "invalid animal",
            "helpString": "animal request should contain center_id, name, age and species values. "
                          "Price and age should be correct formatted"
        }
        response = Response(json.dumps(invalid_animal_creation_request_error_message), 400, mimetype='application/json')
        return response
    if Center.get_center_by_id(int(request_data['center_id'])) is None:
        no_such_center_id_error_message = {
            "error": "invalid center",
            "helpString": "center with such id does not exists"
        }
        response = Response(json.dumps(no_such_center_id_error_message), 400, mimetype='application/json')
        return response
    elif Species.get_species_by_name(request_data['species']) is None:
        no_such_specie_error_message = {
            "error": "invalid specie",
            "helpString": "specie with such name does not exists"
        }
        response = Response(json.dumps(no_such_specie_error_message), 400, mimetype='application/json')
        return response
    elif Animal.get_animal_by_id(id) is None:
        no_such_animal_error_message = {
            "error": "invalid animal",
            "helpString": "animal with such id does not exists"
        }
        response = Response(json.dumps(no_such_animal_error_message), 400, mimetype='application/json')
        return response
    else:
        Animal.update_animal(id, request_data['center_id'], request_data['name'], request_data['description'],
                             int(request_data['age']), request_data['species'], float(request_data['price']))
        response = Response("", 204, mimetype='application/json')
        logging.info('PUT /animals animal_id:{} center_id:{}'.format(id, center_id))
        return response


@app.route('/animals/<int:id>', methods=['DELETE'])
def delete_animal(id):
    center_id = get_id_from_token(request.args.get('token'))
    if center_id is None:
        return jsonify({'error': 'invalid token'}), 401
    animal = Animal.get_animal_by_id(id)
    if animal.center_id != center_id:
        wrong_center_id_error_message = {
            "error": "wrong_center_id",
            "helpString": "You cant delete animals not from your center"
        }
        response = Response(json.dumps(wrong_center_id_error_message), 400, mimetype='application/json')
        return response
    if Animal.delete_animal(id):
        logging.info('DELETE /animals animal_id:{} center_id:{}'.format(id, center_id))
        return Response("", status=204)
    else:
        return Response("", status=404)


# @app.route('/records', methods=['GET'])
# def get_all_records():
#     return jsonify({'centers': Access.get_all_records()})


def validate_register_request(register_request):
    if "login" in register_request and "password" in register_request and "address" in register_request:
        return True
    else:
        return False


def validate_specie(specie):
    if "name" in specie and "description" in specie and "price" in specie:
        try:
            price = float(specie['price'])
            return True
        except ValueError:
            return False
    else:
        return False


def validate_animal(animal):
    if "center_id" in animal and "name" in animal and "age" in animal and "species" in animal:
        try:
            if animal['age'] is not None:
                age = int(animal['age'])
            if animal['price'] is not None:
                price = float(animal['price'])
            center_id = int(animal['center_id'])
            return True
        except ValueError:
            return False
    else:
        return False


def get_id_from_token(token):
    try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        return data['center_id']
    except:
        return None


app.run(port=5000)
