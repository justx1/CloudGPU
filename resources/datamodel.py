# Source Entity Relationship Model: https://my.vertabelo.com/model/NrmpUj9pfdjahIJHoPzwMjjssJk6fDYt 


# -*- encoding: utf-8 -*-
# begin

import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, BigInteger, String, ForeignKey, Unicode, Binary, LargeBinary, Time, DateTime, Date, Text, Boolean, Float, JSON
from sqlalchemy.orm import relationship, backref, deferred
from sqlalchemy.orm import sessionmaker

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

# end
