#### curl -i -X POST -H 'Content-Type: application/json' -d '{"model": "1", "quantity": "2"}' http://localhost:5000/instance
#### curl -i -X POST -H 'Content-Type: application/json' -d '{"username": "7", "email": "7"}' http://localhost:5000/user
#### to create SQLite and tables automatically: enter $ python to enter interactive mode, then
#### >>> from app import db [assuming file name is app.py]
#### >>> db.create_all()


import os
import docker

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Unicode, Binary, LargeBinary, Time, DateTime, Date, Text, Boolean, Float, JSON
from sqlalchemy.orm import relationship, backref, deferred
from sqlalchemy.orm import sessionmaker

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

Base = declarative_base()



class Customer (Base):
    __tablename__ = "customer"
    id = Column('id', Integer, primary_key = True)
    email = Column('email', Unicode)

class Instance (Base):
    __tablename__ = "instance"
    id = Column('id', Integer, primary_key = True)
    customer_id = Column('customer_id', Integer, ForeignKey('customer.id'))
    image_type_id = Column('image_type_id', Integer, ForeignKey('image_type.id'))
    start_dt = Column('start_dt', DateTime)
    end_dt = Column('end_dt', DateTime)
    proxy_ip = Column('proxy_ip', Unicode)

    customer = relationship('Customer', foreign_keys=customer_id)
    image_type = relationship('ImageType', foreign_keys=image_type_id)

class Gpu (Base):
    __tablename__ = "gpu"
    id = Column('id', Integer, primary_key = True)
    host_id = Column('host_id', Integer, ForeignKey('host.id'))
    gpu_type_id = Column('gpu_type_id', Integer, ForeignKey('gpu_type.id'))
    instance_id = Column('instance_id', Integer, ForeignKey('instance.id'))

    host = relationship('Host', foreign_keys=host_id)
    gpu_type = relationship('GpuType', foreign_keys=gpu_type_id)
    instance = relationship('Instance', foreign_keys=instance_id)

class Host (Base):
    __tablename__ = "host"
    id = Column('id', Integer, primary_key = True)
    vendor_id = Column('vendor_id', Integer, ForeignKey('vendor.id'))
    cpu_type_id = Column('cpu_type_id', Integer, ForeignKey('cpu_type.id'))
    country_type_id = Column('country_type_id', Integer, ForeignKey('country_type.id'))
    ip = Column('ip', Unicode)
    memory_mb = Column('memory_MB', Integer)

    vendor = relationship('Vendor', foreign_keys=vendor_id)
    cpu_type = relationship('CpuType', foreign_keys=cpu_type_id)
    country_type = relationship('CountryType', foreign_keys=country_type_id)

class Vendor (Base):
    __tablename__ = "vendor"
    id = Column('id', Integer, primary_key = True)
    email = Column('email', Unicode)

class GpuType (Base):
    __tablename__ = "gpu_type"
    id = Column('id', Integer, primary_key = True)
    name = Column('name', Unicode)
    price_minute_eur = Column('price_minute_eur', BigInteger)

class ImageType (Base):
    __tablename__ = "image_type"
    id = Column('id', Integer, primary_key = True)
    name = Column('name', Unicode)

class CpuType (Base):
    __tablename__ = "cpu_type"
    id = Column('id', Integer, primary_key = True)
    name = Column('name', Unicode)

class CountryType (Base):
    __tablename__ = "country_type"
    id = Column('id', Integer, primary_key = True)
    name = Column('name', Unicode)


#### =====

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
