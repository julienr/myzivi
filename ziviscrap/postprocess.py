##
import ziviscrap.settings as settings
import json
import os, urlparse
from scrapy.selector import HtmlXPathSelector
import common.model
import urllib2
import urllib
##
GOOGLE_GEOCODING_API = "http://maps.googleapis.com/maps/api/geocode/json?"
def geocode_address(address):
    """Uses Google's geocoding API to geocode an address"""
    params = {'address' : address.encode('utf-8'),
              'sensor' : 'false',
              'region' : 'ch'}
    try:
        res = urllib2.urlopen(GOOGLE_GEOCODING_API + urllib.urlencode(params))
        return json.load(res)
    except urllib2.URLError:
        return None
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
    for place_of_work, item in pow_items:
        address = geocode_address(place_of_work)
        if address is not None:
            newitem = item.copy()
            newitem['address'] = address
            outlist.append(newitem)
        else:
            print 'No geocoded address for phid=%s, place_of_work=%s' % (
                    item['phid'], place_of_work)
    return outlist
outitems = geocode_pow_items(pow_items)

## Save items completed with address
outfile = os.path.join(os.path.dirname(jsonfile), 'final_items.json')
with open(outfile, 'w') as f:
    json.dump(outitems, f, indent=2, sort_keys=True)

##
