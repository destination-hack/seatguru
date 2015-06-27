import json
import re
import random
from urllib import urlretrieve
from urllib2 import urlopen, URLError
from pprint import pprint
from bs4 import BeautifulSoup
from retrying import retry

# https://flightaware.com/live/flight/{flightcode}
FLIGHTAWARE_URL = "https://flightaware.com/live/flight/{}"

""" gets origin and destination airport code for a given flight """
@retry(stop_max_attempt_number=5)
def get_airport_code(flight_code):
  def extract_iata_airport_code(html_soup):
    link_text = html_soup.find(class_='track-panel-airport').a.contents[0]
    iata_search = re.search('.*?[^A-Za-z]([A-Za-z]{3})$', link_text)
    if (iata_search):
      return iata_search.group(1)

  resp = urlopen(FLIGHTAWARE_URL.format(flight_code)).read()
  soup = BeautifulSoup(resp)

  depart = extract_iata_airport_code(soup.find(class_='track-panel-departure'))
  arrive = extract_iata_airport_code(soup.find(class_='track-panel-arrival'))
  return (depart, arrive)
