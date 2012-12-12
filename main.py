import urllib2
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

