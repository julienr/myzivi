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
def process_item(item):
    # Extract infos
    addr = item['address']
    canton = addr['canton']
    locality = addr['locality']
    lat = addr['latitude']
    lng = addr['longitude']
    address = addr['formatted_address']
    # Remove dots from phid. This cause some bugs with django/tastypie urls
    phid = re.sub('[\W_]', '', item['phid'])
    shortname = item['shortname']
    url = urlparse.urljoin(ZIVI_DOMAIN, item['url'])

    # Create or update into DB
    addr, created = Address.objects.get_or_create(canton=canton,
            locality=locality, defaults={'latitude':lat, 'longitude':lng})
    ws, created = WorkSpec.objects.get_or_create(phid=phid, address=addr)
    ws.shortname = shortname
    ws.url = url
    ws.save()
##
items = map(process_item, items)
##
