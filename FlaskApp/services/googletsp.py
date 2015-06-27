# get places from input as english text
# run via google api

# input: loc1, loc2
# output: distance

import requests, json, pprint
from itertools import permutations

# Get input from the user, example "Barbican Station, Tower Hill, Buckingham
# Palace"
my_input = raw_input()

# Split into components, remove extra spaced on either side
components = map(lambda x: x.strip(), my_input.split(','))

callString = "https://maps.googleapis.com/maps/api/directions/json?origin="

# Gets the google query url for any two given points
def get_d_url(origin, dest):
    return callString + origin.replace(" ","%20") + "&destination=" +\
    dest.replace(" ", "%20") + "&mode=transit"

# Make a call to the service given the src and dest
def make_call(origin, destination):
    url = get_d_url(origin, destination)
    r = requests.get(url)
    return r.json()

# Given src, dest, get the time it takes to travel between the two in sec
def get_distance(start,end):
    result = make_call(start, end)
    if 'routes' in result:
        first = result['routes'][0]
        legs = first['legs']
        total = 0
        for leg in legs:
            total += int(leg['duration']['value'])
        return total
    else:
        return 0

allitems = []
for perm in permutations(components):
    total = 0
    prev = None
    for item in perm:
        if not prev:
            prev = item
        else:
            total += get_distance(item,prev)
    print "Found distance following route:", perm, ": ", total
    allitems.append(total)

print "Shortest path:", min(allitems)
