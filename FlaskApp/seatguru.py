from urllib2 import urlopen, URLError
from retrying import retry
import json
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('seatguru')

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

@retry(stop_max_attempt_number=5)
def get_airline_info(airline, aircraft, available_seats=None):
  url = API_CALL_TEMPLATE.format(airline, aircraft, API_KEY)
  logger.info("Calling the SeatGuru API - {}".format(url))
  response = json.loads(urlopen(url).read())
  return response
  #logger.info("Received response {}".format(json.dumps(response, indent=2)))

def structure_response(response):
  result = {}
  seats = response['aircraft'][0]['seats']
  for seat in seats:
    result[extract_seat_identifier(seat)] = {}
  return result

def extract_seat_identifier(seat):
  row, column = seat["seats"].split(" ")
  return (row, column)

# get_airline_info("BA", "747")
