import urllib2
import urllib
import bs4
import re
import collections

baseurl = "https://www.eis.zivi.admin.ch/"
url = "https://www.eis.zivi.admin.ch/ZiviEis/ModuleDisplayPage.aspx?functionId=123F61E5-F417-4F51-AC59-906D6F999D02"
html = urllib2.urlopen(url).read()

soup = bs4.BeautifulSoup(html)

workspec_a = soup.find_all("a", id=re.compile(r".*workSpecificationList_workSpecificationTitle\d+$"))

WorkSpec = collections.namedtuple('WorkSpec', ['shortname', 'phid'])
phid_re = re.compile(r'.*?phid=(?P<phid>COO\.\d{4}\.\d{3}\.\d\.\d+).*$')

workspecs = []
for a in workspec_a:
    # Extract phid from href
    m = phid_re.match(a['href'])
    if 'phid' not in m.groupdict():
        raise "Error : couldn't extract phid from %s" % a['href']
    phid = m.group('phid')
    shortname = a.string

    workspecs.append(WorkSpec(shortname=shortname, phid=phid))

# Pagination tests
url = "https://www.eis.zivi.admin.ch/ZiviEis/ModuleDisplayPage.aspx?functionId=123F61E5-F417-4F51-AC59-906D6F999D02"
html = urllib2.urlopen(url).read()
with open('out.html', 'w') as f:
    f.write(html)

data = {
    'ctl00$cphContent$ctl04$workSpecificationList$workSpecificationPagingBar$pageSizeValue':100,
    'ctl00$cphContent$ctl04$workSpecificationList$workSpecificationPagingBar$currentPageValue':5
}
html = urllib2.urlopen(url, data=urllib.urlencode(data)).read()
with open('outdata.html', 'w') as f:
    f.write(html)

#
form = soup('form')[0]
inputs = form.find_all('input')
## Only keep key-value inputs
kvinputs = filter(lambda ipt: 'value' in ipt.attrs, inputs)
data = {ipt['name']:ipt['value'].encode('utf-8') for ipt in kvinputs}
data['ctl00$cphContent$ctl04$workSpecificationList$workSpecificationPagingBar$pageSizeValue'] = 100
data['ctl00$cphContent$ctl04$workSpecificationList$workSpecificationPagingBar$currentPageValue'] = 1
html = urllib2.urlopen(url, data=urllib.urlencode(data)).read()
with open('outinput.html', 'w') as f:
    f.write(html)
##

def data_from_soup(soup):
    form = soup('form')[0]
    inputs = form.find_all('input')
    ## Only keep key-value inputs
    kvinputs = filter(lambda ipt: 'value' in ipt.attrs, inputs)
    data = {ipt['name']:ipt['value'].encode('utf-8') for ipt in kvinputs}

##
