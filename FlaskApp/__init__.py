from flask import Flask, render_template, request, redirect
import re
import twilio.twiml
import seatguru
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
	try:
		phone_number = request.values.get('From')
		message_body = request.values.get('Body')

		response = response_for_message_body(message_body)

		resp = twilio.twiml.Response()
		resp.message(response)
		return str(resp)
	except Exception:
		resp = twilio.twiml.Response()
		resp.message("An error occured :(")
		return str(resp)


'''
Given a seat number and a flight number
return the best possible seat with an explanation as to why its good
- this is the top level function that calls everything
'''
def seat_info_string(airline, aircraft, seatnum):
	seat_info = seatguru.get_airline_info("BA", "747")
	if split_seat_num(seatnum) in seat_info.keys():
		matched_seat = seat_info[split_seat_num(seatnum)]
		return matched_seat["description"]
	else:
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
	return reversed(sorted(seat_list, key=rank_for_seat_tuple))


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

'''
Given a message, return a response. This is wrapped by the route
'''
def response_for_message_body(message_body):
	flightnum, flightmsg = get_flight_number(message_body)


	seatnum, seatmsg = get_seat_number(message_body)

	response = ""

	if flightnum and seatnum:
		# IATA says that airline codes are two letter
		# ICAO says that they are three letters, whopee
		airline = flightnum[0:1]
		depart, arrive, aircraft = flightaware.get_flight_details(flightnum)

		seatinfo = seat_info_string(airline, aircraft, seatnum)
		if seatinfo:
			response = "You're on flight " +  flightnum + ", " + seatinfo.replace("{SEAT}", seatnum).encode('utf-8')
		else:
			response = "This seat does not exist!"
	else:
		response = "Error! " + flightmsg + ", " + seatmsg

	return response

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

'''
Parse the message and get the flight number
'''
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

