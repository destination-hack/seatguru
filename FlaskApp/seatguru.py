from urllib2 import urlopen, URLError
import json
import logging
import logging.config

API_KEY = "sabrehack"
API_CALL_TEMPLATE = "http://www.seatguru.com/api/aircraftconfigurations/1?airline={}&aircraft={}&key={}"

"""
This method calls the SeatGuru API and retrieves information about seats on a certain airplane type.

It can optionally receive a list of seat identifiers, so the unavailable seats can be excluded from the response.

The response should contain a map from seat identifier to seat information.

A seat identifier is a (row, column) tuple. The row is a numeric index, the column is a letter.

The seat information is a map that should contain:
* seat quality (green, green-yellow, yellow, white)
* seat class

TODO: multiple aircraft returned, select the one that matches the flight (ask for more info for the flight)
TOOD: render only available seats
TODO: handle bundled seats in the response
"""

rating_metrics = {"white":1, "yellow":2, "green":4, "red":0, "green_yellow":3}

def get_airline_info(airline, aircraft, available_seats=None):
  url = API_CALL_TEMPLATE.format(airline, aircraft, API_KEY)
  response = json.loads(urlopen(url).read())
  return structure_response(response)
  #logger.info("Received response {}".format(json.dumps(response, indent=2)))

def structure_response(response):
  result = {}
  seats = response['aircraft'][0]['seats']
  classes = get_seat_classes(response['aircraft'][0])

  for i in xrange(len(seats)):
    seat = seats[i]
    seat_identifier = extract_seat_identifier(seat)

    details = extract_details(response, seat)
    details['class'] = get_seat_class(classes, int(seat_identifier[0]))
    result[seat_identifier] = details
  return result

def extract_seat_identifier(seat):
  row, column = seat["seats"].split(" ")
  return (int(row), column.strip())

def get_seat_class(classes, index):
  # print "Seat class for ", index,
  for class_name in classes.keys():
    start, end = classes[class_name]
    if index >= start and index <= end:
      # print "is ", class_name
      return class_name
  # print "is unknown"
  return 'unknown'

def get_seat_classes(aircraft):
  seat_classes = {}
  classes = aircraft["seat_classes"]
  for seat_class in classes:
    category = seat_class["category"]
    start = seat_class["start"]
    end = seat_class["end"]
    seat_classes[category] = (start,end)
  return seat_classes

def extract_details(response, seat):
  rating = seat["rating"]
  score = rating_metrics[rating]

  descriptions = response["seat_descriptions"]
  desc = descriptions[seat["desc_id"]]

  return {"rating":rating, "score":score, "description":desc}
