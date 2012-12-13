##
import ziviscrap.settings as settings
import json
import os, urlparse
from scrapy.selector import HtmlXPathSelector
##
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
for phid, item in itemdict.items():
    detailfile = os.path.join(settings.DETAIL_HTML_DIR, 'detail_%s.html'%phid)
    with open(detailfile) as f:
        detail = f.read()
    hxs = HtmlXPathSelector(text=detail)
    import ipdb; ipdb.set_trace()

##
