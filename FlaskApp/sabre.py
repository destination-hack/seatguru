from urllib2 import urlopen, URLError
from retrying import retry
import json
import logging
import logging.config
import base64
import requests
import sys

# enables debugging the calls made with requests
# import httplib
# httplib.HTTPConnection.debuglevel = 1

# logging.config.fileConfig('logging.conf')
logger = logging.getLogger('sabre')

CLIENT_ID = 'V1:wlhqw2b8zyy36xy0:DEVCENTER:EXT'
CLIENT_SECRET = 'i0Cw4GcF'
SABRE_API_BASE = 'https://api.test.sabre.com'
AUTH_TOKEN_ENDPOINT = '/v1/auth/token'
SEATMAP_ENDPOINT = '/v3.0.0/book/flights/seatmaps?mode=seatmaps'

# obtains an access token to talk to SABRE APIs
@retry(stop_max_attempt_number=5)
def get_access_token():
  def build_credentials():
    client_id     = base64.b64encode(CLIENT_ID)
    client_secret = base64.b64encode(CLIENT_SECRET)
    return base64.b64encode("{}:{}".format(client_id, client_secret))

  def build_auth_endpoint():
    return SABRE_API_BASE + AUTH_TOKEN_ENDPOINT

  def extract_token(response):
    if response.status_code == 200:
      return json.loads(response.text)['access_token']
    else:
      raise "Could not authenticate against Sabre!"

  credentials   = build_credentials()
  headers       = {
    'Authorization': "Basic {}".format(credentials),
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  body          = 'grant_type=client_credentials'
  response = requests.post(build_auth_endpoint(),
    data=body,
    headers=headers)
  return extract_token(response)

# returns a map of all seats in format [(row, seat_number) : { 'available': True, 'price': '100 USD' }] for a given flight
# e.g.: get_seat_map('LHR', 'OTP', '2015-07-16', 'BA', '0886')
def get_seat_map(origin, destination, departure_date, carrier, flight_number):

  def build_request():
    # TODO: figure out why building this as an object instead of string breaks the Sabre API
    return  '{ "EnhancedSeatMapRQ": {\
      "SeatMapQueryEnhanced": {\
        "RequestType": "Payload",\
        "Flight": {\
          "destination": "' + destination +'",\
          "origin": "' + origin + '",\
          "DepartureDate": {\
            "content": "' + departure_date + '"\
          },\
          "Operating": {\
            "carrier": "' + carrier + '",\
            "content": "' + flight_number + '"\
          },\
          "Marketing": [\
            {\
              "carrier": "' + carrier + '",\
              "content": "' + flight_number + '"\
            }\
          ]\
        },\
        "CabinDefinition": {\
          "RBD": "Y"\
        }\
      }\
    }\
  }'

  # returns a map of all seats in format [(row, seat_number) : { 'available': True, 'price': '100 USD' }]
  def parse_response(response):
    data = json.loads(response.text)
    seats = {}
    for row_data in data["EnhancedSeatMapRS"]["SeatMap"][0]["Cabin"][0]["Row"]:
      for seat in parse_row(row_data):
          seat_key = (seat["row"], seat["number"])
          seat_details = { "available": seat["available"] }
          if "price" in seat:
            seat_details["price"] = seat["price"]
          # store seat
          seats[seat_key] = seat_details
    return seats

  # extracts seat details from Sabre response
  def parse_seat(seat_data, row_number):
    seat = {}
    seat["row"] = row_number
    seat["number"] = seat_data["Number"]
    seat["available"] = not seat_data["occupiedInd"]
    if "Price" in seat_data:
      price = seat_data["Price"][0]["TotalAmount"]
      seat["price"] = price["content"] + ' ' + price["currencyCode"]

    return seat

  # returns a list of seat details from a given row data
  def parse_row(row_data):
    seats = []
    row_number = row_data["RowNumber"]
    for seat_data in row_data["Seat"]:
      seats.append(parse_seat(seat_data, row_number))

    return seats

  @retry(stop_max_attempt_number=5)
  def perform_call():
    headers = {
      'Authorization': 'Bearer {}'.format(get_access_token()),
      'Accept': 'application/json',
      'Content-Type': 'application/json'
    }

    request = build_request()

    return requests.post("{}{}".format(SABRE_API_BASE, SEATMAP_ENDPOINT),
      headers=headers,
      data=request)

  response = perform_call()

  if response.status_code != 200:
    logger.warn("Error occurred while calling SeatMap: {}", response.text)
    return {}

  seats = parse_response(response)
  return seats

# https://api.test.sabre.com/v1/lists/utilities/airlines?airlinecode=BA
# https://api.test.sabre.com/v1/lists/utilities/aircraft/equipment?aircraftcode=747
# https://api.test.sabre.com/v1/lists/supported/cities/NYC/airports
# https://api.test.sabre.com/v1/lists/supported/cities?country=US
