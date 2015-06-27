from urllib2 import urlopen, URLError
import json
import logging
import logging.config

logging.config.fileConfig('logging.conf')
logger = logging.getLogger('seatguru')

API_KEY = "sabrehack"
API_CALL_TEMPLATE = "http://www.seatguru.com/api/aircraftconfigurations/1?airline={}&aircraft={}&key={}"

def get_airline_info(airline, aircraft):
  url = API_CALL_TEMPLATE.format(airline, aircraft, API_KEY)
  logger.info("Calling {}".format(url))
  response = json.loads(urlopen(url).read())
  logger.info("Received response {}".format(json.dumps(response, indent=2)))

get_airline_info("BA", "747")