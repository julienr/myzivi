##
import re
from django.core.management import setup_environ
from ziviweb import settings
setup_environ(settings)

from zivimap.models import WorkSpec, Address
import json
import urlparse
##
ZIVI_DOMAIN = "http://www.eis.zivi.admin.ch"
INPUT_FILE = "/home/julien/dev/zivi/_data/scraped/final_items.json"

with open(INPUT_FILE) as f:
    items = json.load(f)

##
def find_locality_address(addresses):
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
            return {'canton': canton,
                    'locality': locality,
                    'latlng' : addr['geometry']['location'],
                    'address' : addr['formatted_address']}
    return None

def process_item(item):
    # Extract infos
    addr = find_locality_address(item['addresses'])
    if addr is None:
        print 'Skipping item with empty canton/locality : ', item
        return
    canton = addr['canton']
    locality = addr['locality']
    latlng = addr['latlng']
    address = addr['address']
    # Remove dots from phid. This cause some bugs with django/tastypie urls
    phid = re.sub('[\W_]', '', item['phid'])
    shortname = item['shortname']
    url = urlparse.urljoin(ZIVI_DOMAIN, item['url'])

    # Create or update into DB
    addr, created = Address.objects.get_or_create(canton=canton,
            locality=locality, defaults={'latitude':latlng['lat'],
                'longitude':latlng['lng']})
    ws, created = WorkSpec.objects.get_or_create(phid=phid, address=addr)
    ws.shortname = shortname
    ws.url = url
    ws.save()
##
items = map(process_item, items)
##
