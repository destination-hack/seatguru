from flask import Flask, render_template, request, redirect
from datetime import datetime
import re
import twilio.twiml
import seatguru
import sabre
import flightaware

app = Flask(__name__)

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
	# try:
	phone_number = request.values.get('From')
	message_body = request.values.get('Body')

	response = response_for_message_body(message_body)

	resp = twilio.twiml.Response()
	resp.message(response)
	return str(resp)
	# except Exception as e:
		# resp = twilio.twiml.Response()
		# resp.message("An error occured :(")
		# return resp

'''
Given a seat number and a flight number
return the best possible seat with an explanation as to why its good
- this is the top level function that calls everything
'''
def get_seat_info(seat_list, seat_code):
	for seat in seat_list:
		if split_seat_num(seat_code) == seat[0]:
			return seat[1]
	return None

'''
output: list of ((Row, "A-F"),{data})
data keys: class, score, description
'''
def get_seat_list_in_order(airline, plane, seatnum=None):
	seat_info = seatguru.get_airline_info(airline, plane)
	if seatnum:
		seatkey = split_seat_num(seatnum)
		if seatkey in seat_info.keys():
			current_seat = seat_info[seatkey]
			seat_type = current_seat['class']
			seat_info = dict((k,v) for (k,v) in seat_info.items() if v["class"] == seat_type)

	seat_list = [(k,v) for (k,v) in seat_info.items()]
	return list(reversed(sorted(seat_list, key=rank_for_seat_tuple)))


def rank_for_seat_tuple(seat_tuple):
	return seat_tuple[1]["score"]

'''
input: "6A"
output: (6,"A")
'''
def split_seat_num(seatnum):
	num = re.findall("[0-9]+", seatnum)[0]
	row = re.findall("[A-Za-z]", seatnum)[0]
	return (int(num), row)

def parse_text_message(message_body):
	flightnum, flightmsg = get_flight_number(message_body)
	seatnum, seatmsg = get_seat_number(message_body)

	if not flightnum or not seatnum:
		raise ValueError("Error! {}, {}".format(flightmsg, seatmsg))

	return (flightnum, seatnum)

'''
Given a message, return a response. This is wrapped by the route
'''
def response_for_message_body(message_body):
	try:
		flight_code, seat_code = parse_text_message(message_body)
	except ValueError as e:
		return e

	# IATA says that airline codes are two letter
	# ICAO says that they are three letters, whopee
	airline, flight_number = flight_code[0:2], flight_code[2:]
	depart, arrive, aircraft = flightaware.get_flight_details(flight_code)

	# throws error if the flight is not found in Sabre (that's what their API does)
	current_date = datetime.now().strftime("%Y-%m-%d")
	try:
		sabre.get_seat_map(depart, arrive, current_date, airline, flight_number)
	except:
		return "There is no flight {} today! Please text us on the day of your flight.".format(flight_code)

	all_seats = get_seat_list_in_order(airline, aircraft)
	my_seat  	= get_seat_info(all_seats, seat_code)
	if not my_seat:
		return "This seat does not exist!"

	best_seat = all_seats[0]
	if compare_seat(my_seat, best_seat[1]) >= 0:
		seat_description = interpolate_description(my_seat, seat_code)
		return "Your seat is pretty good for flight {}! {}".format(flight_code, seat_description)
	else:
		# (21, u'D') -> "21D"
		top_seat_codes = map(lambda top_seat: create_seat_code(top_seat[0]), all_seats[0:4])
		best_seat_code = create_seat_code(best_seat[0])
		seat_description = interpolate_description(best_seat[1], best_seat_code)
		return "For a nicer flight, try a better seat! How about {}? {}".format(
			", ".join(top_seat_codes), seat_description)

def create_seat_code(seat_code_tuple):
	return str(seat_code_tuple[0]) + seat_code_tuple[1]

def interpolate_description(seat_info, seat_code):
	return seat_info['description'].replace("{SEAT}", seat_code).encode('utf-8')

'''
Parse the message and get the seat number
'''
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

def compare_seat(first, second):
	return first['score'] - second['score']

'''
Parse the message and get the flight number
'''
def get_flight_number(message):
	flight_numbers = re.findall("[a-zA-Z0-9]{2}[a-zA-Z]?[0-9]{1,4}[a-zA-Z]?", message)

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
	app.debug = True
	app.run()
	# app.run(debug=True)

