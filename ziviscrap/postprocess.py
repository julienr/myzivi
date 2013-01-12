##
import ziviscrap.settings as settings
import json
import os, urlparse
from scrapy.selector import HtmlXPathSelector
import urllib2
import urllib
import time
import collections
##

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
    try:
        url = NOMINATIM_GEOCODING_API + urllib.urlencode(params)
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

def geocode_address(address):
    #return _google_geocode(address)
    return _nominatim_geocode(address)


## Load Items from the scraper
jsonfile = urlparse.urlparse(settings.FEED_URI).path
with open(jsonfile) as f:
    items = json.load(f)
## Find duplicates
nduplicates = 0
itemdict = {}
for i in items:
    if i['phid'] in itemdict:
        #print 'Item ', i, ' duplicate of :', itemdict[i['phid']]
        nduplicates += 1
    itemdict[i['phid']] = i
print 'Number of duplicates : ', nduplicates
## For each item, extract address from detail page
def extract_place_of_work(items):
    """Return a list of (place_of_work, item) tuples"""
    outlist = []
    for item in items:
        phid = item['phid']
        detailfile = os.path.join(settings.DETAIL_HTML_DIR,
                                  'detail_%s.html'%phid)
        with open(detailfile) as f:
            detail = f.read()
        hxs = HtmlXPathSelector(text=detail)
        place_of_work = hxs.select(
            '//span[contains(@id, "placeOfWorkValue")]/text()').extract()
        if len(place_of_work) == 1:
            outlist.append((place_of_work[0], item))
        else:
            print 'No place of work for phid : ', phid
    return outlist
pow_items = extract_place_of_work(itemdict.values())
##
def geocode_pow_items(pow_items):
    """
    Given a list of (place_of_work, item) tuples, return a list of items
    with an added 'address' entry containing the geocoded address
    """
    outlist = []
    errlist = []
    for i, (place_of_work, item) in enumerate(pow_items):
        print i, ' / ', len(pow_items)
        try:
            address = geocode_address(place_of_work)
            newitem = item.copy()
            newitem['address'] = address
            newitem['place_of_work'] = place_of_work
            outlist.append(newitem)
        except GeocodingError as e:
            err = 'Error geocoding phid=%s, place_of_work=%s : %s' % (item['phid'],
                    place_of_work, e)
            print err
            errlist.append({'item':item.copy(), 'error': err, 'geourl':e.url})
        time.sleep(0.5)
    return outlist, errlist

# TODO: DEBUG ONLY REMOVE !
#pow_items = pow_items[:100]
outitems, erritems = geocode_pow_items(pow_items)
print 'pow_items : ', len(pow_items)
print 'outitems : ', len(outitems)
print 'erritems : ', len(erritems)

## Save items completed with address
outfile = os.path.join(os.path.dirname(jsonfile), 'final_items.json')
with open(outfile, 'w') as f:
    json.dump(outitems, f, indent=2, sort_keys=True)

outfile = os.path.join(os.path.dirname(jsonfile), 'err_items.json')
with open(outfile, 'w') as f:
    json.dump(erritems, f, indent=2, sort_keys=True)

##
