# Source Entity Relationship Model: https://my.vertabelo.com/model/NrmpUj9pfdjahIJHoPzwMjjssJk6fDYt 

# Do POSTs through curl: #### curl -i -X POST -H 'Content-Type: application/json' -d '{"foo": "7", "bar": "7"}' http://localhost:5000/

#### Initialize DB
# python
# >>> from cloudgpu import db
# >>> db.create_all()
# >>> exit()


# -*- encoding: utf-8 -*-
# begin

import os # for OS-based operations, i.e. get path of app for sqlite basedir
import docker
import logging
from datetime import datetime

from flask import Flask
from flask import render_template
from flask import request
from flask import redirect
#from flask import flash

from flask_sqlalchemy import SQLAlchemy

# Application
app = Flask(__name__)
# app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' ### TO DO - what is rge secret_key thing
logger = logging.getLogger()

# Database
basedir = os.path.dirname(os.path.abspath(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'cloudgpu.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Exception handling
class AppError(Exception):
	pass

# Display error messages - Class instance behaves like a function
class DisplayError(object):
	def __init__( self ):
		self.public_value = None

	def __call__( self ):
		return self.public_value

error_message = DisplayError() #error_message.public_value can be set to display error messages on UI

class Instance(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	start_dt = db.Column(db.DateTime, nullable=False)
	end_dt = db.Column(db.DateTime, nullable=True)
	proxy_ip = db.Column(db.String(15), nullable=False)
	gpu_count = db.Column(db.Integer, nullable=False)
	price_gpu_minute_eur = db.Column(db.Numeric(precision=8, asdecimal=True), nullable=False)
	docker_container_id = db.Column(db.String(256), nullable=False)

	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	image_type_id = db.Column(db.Integer, db.ForeignKey('image_type.id'), nullable=False)
	gpu_type_id = db.Column(db.Integer, db.ForeignKey('gpu_type.id'), nullable=False)

	user = db.relationship('User', foreign_keys=user_id)
	image_type = db.relationship('ImageType', foreign_keys=image_type_id)
	gpu_type = db.relationship('GpuType', foreign_keys=gpu_type_id)

class Gpu(db.Model):
	id = db.Column(db.Integer, primary_key=True)

	host_id = db.Column(db.Integer, db.ForeignKey('host.id'), nullable=False)
	gpu_type_id = db.Column(db.Integer, db.ForeignKey('gpu_type.id'), nullable=False)
	instance_id = db.Column(db.Integer, db.ForeignKey('instance.id'), nullable=True)

	host = db.relationship('Host', foreign_keys=host_id)
	gpu_type = db.relationship('GpuType', foreign_keys=gpu_type_id)
	instance = db.relationship('Instance', foreign_keys=instance_id)

class Host(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	ip = db.Column(db.String(15), unique=True, nullable=False)
	memory_mb = db.Column(db.Integer, nullable=False)

	#vendor_id = db.Column(db.Integer, db.ForeignKey('vendor.id'))
	user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
	cpu_type_id = db.Column(db.Integer, db.ForeignKey('cpu_type.id'), nullable=False)
	country_type_id = db.Column(db.Integer, db.ForeignKey('country_type.id'), nullable=False)

	#vendor = db.relationship('Vendor', foreign_keys=vendor_id)
	user = db.relationship('User', foreign_keys=user_id)
	cpu_type = db.relationship('CpuType', foreign_keys=cpu_type_id)
	country_type = db.relationship('CountryType', foreign_keys=country_type_id)

class User(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	email = db.Column(db.String(120), unique=True, nullable=False)

class GpuType(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), unique=True, nullable=False)
	price_minute_eur = db.Column(db.Numeric(precision=8, asdecimal=True), nullable=False)

class ImageType(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), unique=True, nullable=False)

class CpuType(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), unique=True, nullable=False)

class CountryType(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120), unique=True, nullable=False)

'''
class Vendor (Base):
	__tablename__ = "vendor"
	id = Column('id', Integer, primary_key = True)
	email = Column('email', Unicode, nullable=False)
'''

###
### Routes for class Instance
###

@app.route('/', methods=['GET', 'POST'])
def create_instance():
	error_message.public_value = None
	if request.form:
		try:
			user_id=int(request.form.get("user_id"))
			image_type_id=int(request.form.get("image_type_id"))
			gpu_request_type_id=int(request.form.get("gpu_request_type_id"))
			gpu_request_count=int(request.form.get("gpu_request_count"))

			host_id=find_available_host(gpu_request_type_id, gpu_request_count)
			book_gpu(host_id, gpu_request_type_id, gpu_request_count, instance_id=None) # Reserve GPUs
			proxy_ip=set_proxy(host_id)
			docker_container_id=start_container(user_id, image_type_id, proxy_ip, host_id)
			print(docker_container_id)

			try:
				start_dt=datetime.utcnow()
				instance = Instance(
					user_id=user_id,
					image_type_id=image_type_id,
					start_dt=start_dt,
					proxy_ip=proxy_ip,
					gpu_count=gpu_request_count,
					gpu_type_id=gpu_request_type_id,
					price_gpu_minute_eur=0, ### Missing code
					docker_container_id=docker_container_id)
				db.session.add(instance)
				db.session.commit()
			except Exception as e:
				raise AppError("DB issue: Unable to commit Instance", e)

		except AppError as e:
			print("Error: Failed to create Instance.", e)
			logger.exception(e)
	
	instances = Instance.query.all()
	return render_template("instance.html", instances = instances, error = error_message())

def find_available_host(gpu_request_type_id, gpu_request_count):
	gpu_count = Gpu.query.filter_by(gpu_type_id = gpu_request_type_id, instance_id = '').count()
	print("WARNING: Missing aggregation by host_id in find_available_host. Needs to be fixed when second host is added.")
	if gpu_count >= int(gpu_request_count):
		host_id = Gpu.query.filter_by(gpu_type_id = gpu_request_type_id, instance_id = '').first().host_id
		return host_id
	else:
		error_message.public_value = 'There is no host with the number of requested GPUs available. Please select fewer GPUs or try again later.'
		raise AppError('Validation issue: gpu_request_count > gpu_count')

def book_gpu(host_id, gpu_request_type_id, gpu_request_count, instance_id):
	try:
		for x in range(int(gpu_request_count)):
			gpu = Gpu.query.filter_by(gpu_type_id = gpu_request_type_id, host_id = host_id, instance_id = '').first()
			if instance_id:
				gpu.instance_id = instance_id
			else:
				gpu.instance_id = 999999999 # Reserve only with triple-triple-9
		db.session.commit()
	except Exception as e:
		error_message.public_value = 'Oops... something went wrong. The team has been notified.'
		raise AppError('DB issue: Unable to reserve/book GPUs', e)

def set_proxy(host_id):
	try:
		return "999.999.999.999"
	except Exception as e:
		error_message.public_value = 'Oops... something went wrong. The team has been notified.'
		raise AppError("Proxy issue: unknown", e)

def start_container(user_id, image_type_id, proxy_ip, host_id):
	try:
		print("(dummy) Starting docker container with user_id: " + str(user_id) + " image_type_id: " + str(image_type_id) + " host_id: " + str(host_id) + " proxy_ip: " + proxy_ip)
		docker_client = docker.from_env()
		docker_container = docker_client.containers.run("alpine", ["echo", "hello", "world"], detach=True)
		return docker_container.id
	except Exception as e:
		error_message.public_value = 'Oops... something went wrong. The team has been notified.'
		raise AppError("Docker issue: Unable to run docker container", e)

@app.route("/delete", methods=["POST"])
def delete_instance():
	try:
		id = request.form.get("id")
		instance = Instance.query.filter_by(id=id).first()
		db.session.delete(instance)
		db.session.commit()
	except Exception as e:
		print("Error: Failed to delete Instance")
		print(e)  
	return redirect("/")

###
### Routes for class Gpu
###

@app.route('/admin/gpu/', methods=['GET', 'POST'])
def create_gpu():
	if request.form:
		try:
			gpu = Gpu(host_id=request.form.get("host_id"), gpu_type_id=request.form.get("gpu_type_id"), instance_id=request.form.get("instance_id"))
			db.session.add(gpu)
			db.session.commit()
		except Exception as e:
			print("Error: Failed to create Gpu")
			print(e)
	gpus = Gpu.query.all()
	return render_template("gpu.html", gpus=gpus)

@app.route("/admin/gpu/delete", methods=["POST"])
def delete_gpu():
	try:
		id = request.form.get("id")
		gpu = Gpu.query.filter_by(id=id).first()
		db.session.delete(gpu)
		db.session.commit()
	except Exception as e:
		print("Error: Failed to delete Gpu")
		print(e)  
	return redirect("/admin/gpu/")

###
### Routes for class Host
###

@app.route('/admin/host/', methods=['GET', 'POST'])
def create_host():
	if request.form:
		try:
			host = Host(ip=request.form.get("ip"), memory_mb=request.form.get("memory_mb"), user_id=request.form.get("user_id"), cpu_type_id=request.form.get("cpu_type_id"), country_type_id=request.form.get("country_type_id"))
			db.session.add(host)
			db.session.commit()
		except Exception as e:
			print("Error: Failed to create Host")
			print(e)
	hosts = Host.query.all()
	return render_template("host.html", hosts=hosts)

@app.route("/admin/host/delete", methods=["POST"])
def delete_host():
	try:
		id = request.form.get("id")
		host = Host.query.filter_by(id=id).first()
		db.session.delete(host)
		db.session.commit()
	except Exception as e:
		print("Error: Failed to delete Host")
		print(e)  
	return redirect("/admin/host/")

###
### Routes for class User
###

@app.route('/admin/user/', methods=['GET', 'POST'])
def create_user():
	if request.form:
		try:
			user = User(email=request.form.get("email"))
			db.session.add(user)
			db.session.commit()
		except Exception as e:
			print("Error: Failed to create User")
			print(e)
	users = User.query.all()
	return render_template("user.html", users=users)

@app.route("/admin/user/update", methods=["POST"])
def update_user():
	try:
		newemail = request.form.get("newemail")
		oldemail = request.form.get("oldemail")
		user = User.query.filter_by(email=oldemail).first()
		user.email = newemail
		db.session.commit()
	except Exception as e:
		print("Error: Failed to update User")
		print(e)
	return redirect("/admin/user/")

@app.route("/admin/user/delete", methods=["POST"])
def delete_user():
	try:
		email = request.form.get("email")
		user = User.query.filter_by(email=email).first()
		db.session.delete(user)
		db.session.commit()
	except Exception as e:
		print("Error: Failed to delete User")
		print(e)  
	return redirect("/admin/user/")

###
### Routes for class GpuType
###

@app.route('/admin/gputype/', methods=['GET', 'POST'])
def create_gputype():
	if request.form:
		try:
			gpu_type = GpuType(name=request.form.get("name"), price_minute_eur=request.form.get("price_minute_eur"))
			db.session.add(gpu_type)
			db.session.commit()
		except Exception as e:
			print("Error: Failed to create GpuType")
			print(e)
	gpu_types = GpuType.query.all()
	return render_template("gpu_type.html", gpu_types=gpu_types)

@app.route("/admin/gputype/delete", methods=["POST"])
def delete_gputype():
	try:
		id = request.form.get("id")
		gputype = GpuType.query.filter_by(id=id).first()
		db.session.delete(gputype)
		db.session.commit()
	except Exception as e:
		print("Error: Failed to delete GpuType")
		print(e)  
	return redirect("/admin/gputype/")

###
### Routes for class ImageType
###

@app.route('/admin/imagetype/', methods=['GET', 'POST'])
def create_imagetype():
	if request.form:
		try:
			image_type = ImageType(name=request.form.get("name"))
			db.session.add(image_type)
			db.session.commit()
		except Exception as e:
			print("Error: Failed to create ImageType")
			print(e)
	image_types = ImageType.query.all()
	return render_template("image_type.html", image_types=image_types)

@app.route("/admin/imagetype/delete", methods=["POST"])
def delete_imagetype():
	try:
		id = request.form.get("id")
		imagetype = ImageType.query.filter_by(id=id).first()
		db.session.delete(imagetype)
		db.session.commit()
	except Exception as e:
		print("Error: Failed to delete ImageType")
		print(e)  
	return redirect("/admin/imagetype/")

###
### Routes for class CpuType
###

@app.route('/admin/cputype/', methods=['GET', 'POST'])
def create_cputype():
	if request.form:
		try:
			cpu_type = CpuType(name=request.form.get("name"))
			db.session.add(cpu_type)
			db.session.commit()
		except Exception as e:
			print("Error: Failed to create CpuType")
			print(e)
	cpu_types = CpuType.query.all()
	return render_template("cpu_type.html", cpu_types=cpu_types)

@app.route("/admin/cputype/delete", methods=["POST"])
def delete_cputype():
	try:
		id = request.form.get("id")
		cputype = CpuType.query.filter_by(id=id).first()
		db.session.delete(cputype)
		db.session.commit()
	except Exception as e:
		print("Error: Failed to delete CpuType")
		print(e)  
	return redirect("/admin/cputype/")

###
### Routes for class CountryType
###

@app.route('/admin/countrytype/', methods=['GET', 'POST'])
def create_countrytype():
	if request.form:
		try:
			country_type = CountryType(name=request.form.get("name"))
			db.session.add(country_type)
			db.session.commit()
		except Exception as e:
			print("Error: Failed to create CountryType")
			print(e)
	country_types = CountryType.query.all()
	return render_template("country_type.html", country_types=country_types)

@app.route("/admin/countrytype/delete", methods=["POST"])
def delete_countrytype():
	try:
		id = request.form.get("id")
		countrytype = CountryType.query.filter_by(id=id).first()
		db.session.delete(countrytype)
		db.session.commit()
	except Exception as e:
		print("Error: Failed to delete CountryType")
		print(e)  
	return redirect("/admin/countrytype/")

###
### Routes for static Admin page
###

@app.route('/admin/', methods=['GET'])
def tmp_admin():
	return render_template("admin.html")

###
### Main
###

if __name__ == "__main__":
	app.run(host="0.0.0.0", debug=True)

# end
