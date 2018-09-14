#### curl -i -X POST -H 'Content-Type: application/json' -d '{"model": "1", "quantity": "2"}' http://localhost:5000/instance
#### curl -i -X POST -H 'Content-Type: application/json' -d '{"username": "7", "email": "7"}' http://localhost:5000/user
#### to create SQLite and tables automatically: enter $ python to enter interactive mode, then
#### >>> from app import db [assuming file name is app.py]
#### >>> db.create_all()

import os
import docker
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'app.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
ma = Marshmallow(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

class Instance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(80), unique=False)
    
    def __init__(self, type):
        self.type = type


class UserSchema(ma.Schema):
    class Meta:
        # Fields to expose
        fields = ('username', 'email')


user_schema = UserSchema()
users_schema = UserSchema(many=True)


# endpoint to create new user
@app.route("/user", methods=["POST"])
def add_user():
    username = request.json['username']
    email = request.json['email']
    
    new_user = User(username, email)

    db.session.add(new_user)
    db.session.commit()

    return user_schema.jsonify(new_user)



#import redis
#cache = redis.Redis(host='redis', port=6379)

#import time
#def get_hit_count():
#    retries = 5
#    while True:
#        try:
#            return cache.incr('hits')
#        except redis.exceptions.ConnectionError as exc:
#            if retries == 0:
#                raise exc
#            retries -= 1
#            time.sleep(0.5)


@app.route('/')
def hello():
#    count = get_hit_count()
#    return 'Hello World! I have been seen {} times.\n'.format(count)
    return 'Hello Worldixi'

# API endpoint to launch new GPU instance
@app.route('/instance', methods=['POST'])
def add_instance():
    model = request.json['model']
    quantity = request.json['quantity']
    
    #client = docker.from_env()
    #client.containers.run("ubuntu:latest", "echo hello world")

    #return jsonify(model)
    return jsonify('hallo')


if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
