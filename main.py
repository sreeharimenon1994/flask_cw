#!/usr/bin/env python3

import os

from flask import Flask, jsonify, url_for, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import requests
import json
import hashlib
import time

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

class User(db.Model):
   id = db.Column('elephant_id', db.Integer, primary_key = True)
   username = db.Column(db.String(100))
   password = db.Column(db.String(250))
   token = db.Column(db.String(250))

   def __init__(self, username, password, token):
       self.username = username
       self.password = password
       self.token = token



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


@app.route("/elephant/", methods=['POST', "DELETE", "PATCH"])
def add_elephant():
    if request.method == 'POST':
        data = json.loads(request.data)
        if 'url' not in data:
            data['url'] = ''
        if 'sex' not in data:
            data['sex'] = ''
        if 'species' not in data:
            data['species'] = ''
        res = 'Please provide a name.'
        if 'name' in data and data['name'] != '':
            new_ele = Elephant(name=data['name'], sex=data['sex'], url=data['url'], species=data['species'])
            save_obj(new_ele)
            res = 'Elephant has been added.'
    
    if request.method == 'DELETE':
        data = json.loads(request.data)
        res = 'Please provide a name.'
        if 'name' in data and data['name'] != '':
            a = Elephant.query.all()
            res = False
            for x in a:
                if x.name == data['name']:
                    res = x
                    break
            if res:
                db.session.delete(res)
                db.session.commit()
                res = 'Elephant has been deleted.'
            else:
                res = "Request not complete."

    if request.method == 'PATCH':
        data = json.loads(request.data)
        res = 'Please provide a name.'
        print("\n\n\nkerypoyi", data)
        if 'name' in data and data['name'] != '' and 'prev_name' in data and data['prev_name'] != '':
            if 'url' not in data:
                data['url'] = ''
            if 'sex' not in data:
                data['sex'] = ''
            if 'species' not in data:
                data['species'] = ''
            a = Elephant.query.all()
            res = False
            for x in a:
                # print(x.name, data['prev_name'], x.name == data['prev_name'])
                if x.name == data['prev_name']:
                    res = x
                    break
            if res:
                print("pinnem kery\n\n\n\n", res.name)
                res.name = data['name']
                res.sex = data['sex']
                res.url = data['url']
                res.species = data['species']
                # admin = Elephant.query.filter_by(name=data['prev_name']).update(dict(url=data['url'], sex=data['sex'], name=data['name'], species=data['species']))
                db.session.commit()
                res = 'Elephant has been updated.'
            else:
                res = "Request not complete."
    return jsonify({'response': res}), 200


@app.route("/elephant/from_db/<name>", methods=['GET'])
def read_elephant(name):
    if request.method == 'GET':
        res = 'Please provide different a name.'
        a = Elephant.query.all()
        for x in a:
            # print(x.name)
            if x.name == name:
                res = {"name": x.name, "url": x.url, "sex": x.sex, "species": x.species}
                break

    return jsonify({"data": res}), 200

# 
# -------------------------- user --------------------------
# 

@app.route("/user", methods=['POST', 'DELETE'])
def user_add_delete():
    if request.method == 'POST':
        data = json.loads(request.data)
        if 'username' in data and data['username'] != '' and 'password' in data and data['password'] != '':
            token = str(time.time())
            token = hashlib.md5(token.encode()).hexdigest()
            data['password'] = hashlib.md5(data['password'].encode()).hexdigest()
            a = User.query.all()
            flag = True
            for x in a:
                if x.username == data['username']:
                    flag = False
                    break
            if flag:
                new_ele = User(username=data['username'], password=data['password'], token=token)
                save_obj(new_ele)
                res = {"res":'User has been added.', "token": token}
            else:
                res = 'User exists.'
    
    if request.method == 'DELETE':
        data = json.loads(request.data)
        res = 'Please provide a correct credetials.'
        if 'username' in data and data['username'] != '' and 'password' in data and data['password'] != '':
            data['password'] = hashlib.md5(data['password'].encode()).hexdigest()
            a = User.query.all()
            res = False
            # print('\n\ntoken\n\n', request.headers.get('token'))
            for x in a:
                if x.username == data['username'] and x.password == data['password']:
                    res = x
                    break
            if res:
                db.session.delete(res)
                db.session.commit()
                res = 'User has been deleted.'
            else:
                res = "Request failed."

    return jsonify({'response': res}), 200


@app.route("/authenticate", methods=['POST'])
def authenticate():
    if request.method == 'POST':
        data = json.loads(request.data)
        res = 'Please provide correct credentials.'
        if 'username' in data and data['username'] != '' and 'password' in data and data['password'] != '':
            data['password'] = hashlib.md5(data['password'].encode()).hexdigest()
            a = User.query.all()
            for x in a:
                if x.username == data['username'] and x.password == data['password']:
                    res = 'User credentials are correct.'
                    break
    return jsonify({'response': res}), 200

if __name__ == "__main__":
    app.run()





# https://elephant-api.herokuapp.com/elephants

# https://elephant-api.herokuapp.com/elephants/random

# https://elephant-api.herokuapp.com/elephants/sex/{SEX}

# https://elephant-api.herokuapp.com/elephants/name/{NAME}

# https://elephant-api.herokuapp.com/species/{SPECIES}



