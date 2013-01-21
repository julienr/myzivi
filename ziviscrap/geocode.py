import urllib2
import urllib
import logging
import json
import shove

geocache = shove.Shove('sqlite:///geocache.sqlite')

class GeocodingError(Exception):
    def __init__(self, msg, url=None):
        if url is None:
            url = ""
        self.msg = msg
        self.url = url
    def __str__(self):
        return "GeocodingError : " + repr(self.msg)

def create_address(canton, locality, latitude, longitude, formatted_address):
    return {'canton':canton, 'locality':locality, 'latitude':latitude,
            'longitude':longitude, 'formatted_address':formatted_address}

## Google geocoding
GOOGLE_GEOCODING_API = "http://maps.googleapis.com/maps/api/geocode/json?"
def _google_find_locality_address(addresses):
    """
    From a JSON response of Google geocoding (potentially
    containing multiple addresses), find the most likely address.
    We basically want the address where place_of_work is a locality or
    a sublocality
    """
    for addr in addresses:
        locality = None
        canton = None
        for component in addr['address_components']:
            ctypes = component['types']
            if 'locality' in ctypes:
                locality = component['long_name']
            elif 'sublocality' in ctypes:
                locality = component['long_name']
            elif 'administrative_area_level_1' in ctypes:
                canton = component['long_name']
        if canton is not None and locality is not None:
            latlng = addr['geometry']['location']
            return create_address(canton=canton, locality=locality,
                           latitude=latlng['lat'], longitude=latlng['lng'],
                           formatted_address = addr['formatted_address'])
    return None

def _google_geocode(address):
    """Uses Google's geocoding API to geocode an address"""
    params = {'address' : address.encode('utf-8'),
              'sensor' : 'false',
              'region' : 'ch'}
    try:
        url = GOOGLE_GEOCODING_API + urllib.urlencode(params)
        res = urllib2.urlopen(url)
    except urllib2.URLError:
        raise GeocodingError("URLError", url=url)

    res = json.load(res)
    # TODO: handle OVER_QUERY_LIMIT by retrying
    if len(res['results']) == 0:
        raise GeocodingError("No results, status = %s" % res['status'], url=url)
    return _google_find_locality_address(res['results'])

## OpenStreetMap geocoding
NOMINATIM_GEOCODING_API = "http://nominatim.openstreetmap.org/search?"
def _nominatim_geocode(address):
    """
    Use OpenStreetMap nominatim geocoder :
    http://wiki.openstreetmap.org/wiki/Nominatim
    """
    params = {'q' : address.encode('utf-8'),
              'format' : 'json',
              'addressdetails': 1,
              'countrycodes': 'ch'} # comma-separated
    url = NOMINATIM_GEOCODING_API + urllib.urlencode(params)
    try:
        res = urllib2.urlopen(url)
    except urllib2.URLError:
        raise GeocodingError('URLError', url=url)

    res = json.load(res)
    if len(res) == 0:
        raise GeocodingError('No results', url=url)

    def get_locality(resaddr):
        if 'city' in resaddr:
            return resaddr['city']
        elif 'town' in resaddr :
            return resaddr['town']
        elif 'village' in resaddr:
            return resaddr['village']
        else:
            raise GeocodingError('No place found for %s' % resaddr, url=url)

    try:
        return create_address(canton=res[0]['address']['state'],
                              locality=get_locality(res[0]['address']),
                              latitude=res[0]['lat'],
                              longitude=res[0]['lon'],
                              formatted_address = res[0]['display_name'])
    except KeyError as e:
        raise GeocodingError('Keyerror : %s' %e, url=url)

def geocode_address(raw_address):
    #address = _google_geocode(raw_address)
    if raw_address in geocache:
        return geocache[raw_address]
    else:
        address = _nominatim_geocode(raw_address)
        geocache[raw_address] = address
        return address


