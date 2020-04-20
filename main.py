#!/usr/bin/env python3

import os

from flask import Flask, jsonify, url_for, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests

app = Flask(__name__)
db = SQLAlchemy(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///elephant.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config.update(dict(DEBUG=True))
CORS(app)

class Elephant(db.Model):
   id = db.Column('elephant_id', db.Integer, primary_key = True)
   name = db.Column(db.String(100))
   url = db.Column(db.String(250), nullable=True)
   sex = db.Column(db.String(10), nullable=True)
   species = db.Column(db.String(10), nullable=True)

   def __init__(self, name, url="", sex="", species=""):
       self.name = name
       self.url = url
       self.sex = sex
       self.species = species


@app.errorhandler(404)
def page_not_found(e):
    #snip
    return jsonify({"response": 'Page does not exist!'}), 404

@app.route("/", methods=['GET'])
def home_page():
    data = []
    for rule in app.url_map.iter_rules():
        data.append({'url': rule.rule, 'methods': list(rule.methods)})
    data = {"api_list": data}
    return jsonify(data), 200


def extract_from_url(obj):
    data = {'data': 'No data available.'}
    if len(obj.content) > 0:
        data['data'] = obj.json()
    return data

@app.route("/create_db", methods=['GET'])
def create_db():
    db.create_all()
    data = {"response": "Database created"}
    return jsonify(data), 200


@app.route("/elephant/random", methods=['GET'])
def random_elephant():
    data = requests.get('https://elephant-api.herokuapp.com/elephants/random')
    data = extract_from_url(data)
    return jsonify(data), 200


@app.route("/elephant/name/<name>", methods=['GET'])
def name_search(name):
    data = requests.get('https://elephant-api.herokuapp.com/elephants/name/'+name)
    data = extract_from_url(data)
    return jsonify(data), 200


@app.route("/elephant/sex/<sex>", methods=['GET'])
def search_sex(sex):
    data = requests.get('https://elephant-api.herokuapp.com/elephants/sex/'+sex)
    data = extract_from_url(data)
    return jsonify(data), 200


@app.route("/elephant/species/<species>", methods=['GET'])
def search_species(species):
    data = requests.get('https://elephant-api.herokuapp.com/elephants/species/'+species)
    data = extract_from_url(data)
    return jsonify(data), 200

def save_obj(obj):
    db.session.add(obj)
    db.session.commit()

@app.route("/elephant/add", methods=['POST', 'GET'])
def add_elephant():
    if request.method == 'GET':
        new_ele = Elephant(name='sreehari', url='http://www.example.com')
        save_obj(new_ele)
    return jsonify({'response': 'Elephant has been added.'}), 200




# https://elephant-api.herokuapp.com/elephants

# https://elephant-api.herokuapp.com/elephants/random

# https://elephant-api.herokuapp.com/elephants/sex/{SEX}

# https://elephant-api.herokuapp.com/elephants/name/{NAME}

# https://elephant-api.herokuapp.com/species/{SPECIES}






if __name__ == "__main__":
    app.run()