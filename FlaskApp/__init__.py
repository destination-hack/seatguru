from flask import Flask, render_template, request, redirect
import re
from flask.ext.sqlalchemy import SQLAlchemy
import flask.ext.restless
import twilio.twiml

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:desthack101xyz@localhost/FlaskApp'
db = SQLAlchemy(app)

# ------------------------------------------
# Database ORM Section - with Flask SQLAlchemy
# ------------------------------------------

# Example ORM model - please modify to your requirements
# SQL Alchemy quick reference: pythonhosted.org/Flask-SQLAlchemy/quickstart.html
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True)
    email = db.Column(db.String(120), unique=True)

    def __init__(self, username, email):
        self.username = username
        self.email = email

    def __repr__(self):
        return '<User %r>' % self.username

# ------------------------------------------
# Database API Section - with Flask Restless
# ------------------------------------------

manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)
manager.create_api(User, methods=['GET', 'POST', 'DELETE'])


# ------------------------------------------
# Routing Section
# ------------------------------------------

# Sets up the database - visit this page after configuring 
# SQLAlchemy models above 
@app.route("/mysql_db_setup")
def db_setup():
	try:
		# Database setup logic
		db.create_all()
		return "Database setup was successfull, please disable db_setup() in your application"
	except Exception, e:
		return str(e)

# Root page - please change as required
@app.route("/")
def index():
	try:
		# Index logic goes here 
		return render_template("index.html")
	except Exception, e:
		return str(e)

@app.route("/twilio", methods=['GET','POST'])
def twilio_response():
	phone_number = request.values.get('From')
	message_body = request.values.get('Body')

	flightnum, flightmsg = get_flight_number(message_body)
	seatnum, seatmsg = get_seat_number(message_body)

	response = ""

	if flightnum and seatnum:
		response = "Flight number: " + flightnum + ", Seat num: " + seatnum	
	else:
		response = "Error! " + flightmsg + ", " + seatmsg 

	resp = twilio.twiml.Response()
	resp.message(response)
	return str(resp)

def get_seat_number(message):
	seat_numbers = re.findall("[0-9]{1,2}[a-zA-Z]{1}", message)
	response = ""
	number = ""

	if len(seat_numbers) == 1:
		# Success!
		number = seat_numbers[0]
		response = "Seat number found!"
	elif len(seat_numbers) == 0:
		# Could not find a number
		response = "Invalid seat number provided"
		number = None
	else:
		# Too many numbers!	
		response = "You provided more than 1 seat number"
		number = None

	return (number, response)

def get_flight_number(message):
	flight_numbers = re.findall("[a-zA-Z0-9]{2}[a-zA-Z]?[0-9]{1,4}[a-zA-Z]?", message)
	response = ""
	number = ""

	if len(flight_numbers) == 1:
		# Success!
		number = flight_numbers[0]
		response = "Flight number found!"
	elif len(flight_numbers) == 0:
		# Could not find a number
		response = "Flight not found"
		number = None
	else:
		# Too many numbers!	
		response = "You provided more than 1 flight number"
		number = None

	return (number, response)

if __name__ == "__main__":
	app.run(debug=True)

