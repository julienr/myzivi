##
import re
from django.core.management import setup_environ
from django.conf import settings
#from ziviweb import settings
#setup_environ(settings)

from zivimap.models import WorkSpec, Address, DateRange
import json
import urlparse

import os
import ziviscrap.settings as scrap_settings
##
ZIVI_DOMAIN = "http://www.eis.zivi.admin.ch"
INPUT_FILE = os.path.join(scrap_settings.DATA_DIR, "final_items.json")

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
    raw_phid = item['phid']
    phid = re.sub('[\W_]', '', item['phid'])
    shortname = item['shortname']
    url = urlparse.urljoin(ZIVI_DOMAIN, item['url'])

    # Create or update into DB
    addr, created = Address.objects.get_or_create(canton=canton,
            locality=locality, defaults={'latitude':lat, 'longitude':lng})
    # Now, the address of the workspec might have changed, in which case
    # we need to delete the old workspec and create a new one
    try:
        ws = WorkSpec.objects.get(phid=phid)
        ws.address = addr
    except WorkSpec.DoesNotExist:
        ws = WorkSpec(phid=phid, address=addr)
    ws.raw_phid = raw_phid
    ws.shortname = shortname
    ws.url = url
    ws.institution_name = item['institution_name']
    ws.institution_description = item['institution_description']
    ws.job_title = item['job_title']
    ws.job_functions = item['job_functions_list']
    ws.activity_domain = item['activity_domain']
    ws.language = item['lang']
    ws.save()
    # Update available dates for this workspec. First remove all previous
    # available dates
    for dr in ws.daterange_set.all():
        dr.delete()

    for daterange in item['available_dates']:
        start, end = daterange
        dr = DateRange(workspec=ws, start=start, end=end)
        dr.save()
##
items = map(process_item, items)
##
