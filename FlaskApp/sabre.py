from urllib2 import urlopen, URLError
import json
import logging
import logging.config
import base64
import requests
import sys

# enables debugging the calls made with requests
import httplib
httplib.HTTPConnection.debuglevel = 1

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('sabre')

CLIENT_ID = 'V1:wlhqw2b8zyy36xy0:DEVCENTER:EXT'
CLIENT_SECRET = 'i0Cw4GcF'
SABRE_API_BASE = 'https://api.test.sabre.com'
AUTH_TOKEN_ENDPOINT = '/v1/auth/token'
SEATMAP_ENDPOINT = '/v3.0.0/book/flights/seatmaps?mode=seatmaps'

def get_access_token():
  def build_credentials():
    client_id     = base64.b64encode(CLIENT_ID)
    client_secret = base64.b64encode(CLIENT_SECRET)
    return base64.b64encode("{}:{}".format(client_id, client_secret))

  def build_auth_endpoint():
    return "{}{}".format(SABRE_API_BASE, AUTH_TOKEN_ENDPOINT)

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

def get_seat_map():
  sample_request  = open('sample_data/sabre_seatmap_rest.json', 'r').read()
  print "\n\n"
  print sample_request
  print "\n\n"
  headers = {
    'Authorization': 'Bearer {}'.format(get_access_token()),
    'Accept': 'application/json',
    'Content-Type': 'application/json'
  }
  # return None
  response = requests.post("{}{}".format(SABRE_API_BASE, SEATMAP_ENDPOINT),
    headers=headers,
    data=sample_request)
  return response

# https://api.test.sabre.com/v1/lists/utilities/airlines?airlinecode=BA
# https://api.test.sabre.com/v1/lists/utilities/aircraft/equipment?aircraftcode=747
# https://api.test.sabre.com/v1/lists/supported/cities/NYC/airports
# https://api.test.sabre.com/v1/lists/supported/cities?country=US
