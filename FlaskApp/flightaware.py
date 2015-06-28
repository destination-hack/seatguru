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
def get_flight_details(flight_code):

  def extract_iata_airport_code(html_soup):
    link_text = html_soup.find(class_='track-panel-airport').a.contents[0]
    iata_search = re.search('.*?([A-Za-z]{3})$', link_text)
    if (iata_search):
      return iata_search.group(1)

  def extract_aircraft_code(html_soup):
    aircraft_code = html_soup.parent.find_next_sibling('td').find('a')
    if (aircraft_code):
      aircraft_code = aircraft_code['href'].split('/')[-1]
    # we only need the numeric part of the model
    # i.e. for H/B744/L we get 744
    # CRJ 700 borks - http://flightaware.com/live/flight/BAW4449
    numeric_code = re.search('.*?(\d+).*?$', aircraft_code)
    if (numeric_code):
      return numeric_code.group(1)

  resp = urlopen(FLIGHTAWARE_URL.format(flight_code)).read()
  soup = BeautifulSoup(resp)

  depart    = extract_iata_airport_code(soup.find(class_='track-panel-departure'))
  arrive    = extract_iata_airport_code(soup.find(class_='track-panel-arrival'))
  aircraft  = extract_aircraft_code(soup.find(text='Aircraft'))
  return (depart, arrive, aircraft)

