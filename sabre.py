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

  credentials   = build_credentials()
  headers       = {
    'Authorization': "Basic {}".format(credentials),
    'Content-Type': 'application/x-www-form-urlencoded'
  }
  body          = 'grant_type=client_credentials'
  r = requests.post(build_auth_endpoint(),
    data=body,
    headers=headers)
  return r

get_access_token()