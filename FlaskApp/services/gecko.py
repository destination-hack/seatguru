import requests, json, pprint
from itertools import permutations

callString = "http://api.geckolandmarks.com/json?lat={0}&lon={1}&api_key=Zzr91jhGfXUMNu3_B63RjjkQkRSaJaeosnBePizPUtU"

# Gets the google query url for any two given points
def get_d_url(lat, lng):
    return callString.format(lat, lng)

# Make a call to the service given the src and dest
def make_call(lat, lng):
    url = get_d_url(lat, lng)
    r = requests.get(url)
    return r.json()

def get_destinations(js_in):
    return js_in["landmarks"]

def call_service(lat, lng):
    js_in = make_call(lat, lng)
    return get_destinations(js_in)
