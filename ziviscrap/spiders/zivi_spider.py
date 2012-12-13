import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest
from scrapy import log

from ziviscrap.items import WorkSpecItem

phid_re = re.compile(r'.*?phid=(?P<phid>COO\.\d{4}\.\d{3}\.\d\.\d+).*$')

# Scraping constants
WORKSPEC_LIST_URL = "https://www.eis.zivi.admin.ch/ZiviEis/ModuleDisplayPage."\
                    + "aspx?functionId=123F61E5-F417-4F51-AC59-906D6F999D02"

# POST request entries
POST_USED_BUTTON = 'ctl00$CommonScriptManager'
BUTTON_FORWARD = 'tl00$cphContent$ctl04$workSpecificationList$TableUpdate'\
               + 'Panel|ctl00$cphContent$ctl04$workSpecificationList$' \
               + 'workSpecificationPagingBar$onePageForwardButton'

POST_PAGE_SIZE = 'ctl00$cphContent$ctl04$workSpecificationList$'\
               + 'workSpecificationPagingBar$pageSizeValue'
# Html IDs
WORKSPEC_A_ID = "workSpecificationList_workSpecificationTitle"
CURRENT_PAGE_INPUT = 'ctl00$cphContent$ctl04$workSpecificationList$'\
                   + 'workSpecificationPagingBar$currentPageValue'

PAGE_TOTAL_LABEL = 'cphContent_ctl04_workSpecificationList_'\
                 + 'workSpecificationPagingBar_currentPageSum'

def extract_current_page(hxs):
    return int(hxs.select(
                '//input[@name="%s"]/@value'%CURRENT_PAGE_INPUT).extract()[0])

def extract_total_pages(hxs):
    pages = hxs.select('//span[@id="%s"]/text()'%PAGE_TOTAL_LABEL)[0]
    return int(pages.re('\w+\s(\d+)')[0])

class ZiviSpider(BaseSpider):
    name = "zivi"
    allowed_domains = ["www.eis.zivi.admin.ch"]
    start_urls = [WORKSPEC_LIST_URL]

    def parse(self, response):
        formdata = {POST_PAGE_SIZE: '100'}
        return FormRequest.from_response(response, dont_click=True,
                formdata=formdata, callback=self.parse_workspecs_100)

    def parse_workspecs_100(self, response):
        hxs = HtmlXPathSelector(response)
        current_page = extract_current_page(hxs)
        total_pages = extract_total_pages(hxs)
        log.msg('Current page : %d / %d' % (current_page, total_pages))
        workspecs_a = hxs.select('//a[contains(@id, "%s")]' % WORKSPEC_A_ID)
        for a in workspecs_a:
            shortname = a.select('text()').extract()
            url = a.select('@href').extract()
            m = phid_re.match(str(url))
            assert 'phid' in m.groupdict()
            phid = m.group('phid')

            item = WorkSpecItem()
            item['shortname'] = shortname
            item['url'] = url
            item['phid'] = phid
            yield item

        formdata = {CURRENT_PAGE_INPUT :str(current_page + 1)} # TODO: replace 2 by +1
#        fr = FormRequest.from_response(response, dont_click=True,
#                formdata=formdata, callback=self.next_page)
        fr = FormRequest.from_response(response, dont_click=True,
                formdata=formdata, callback=self.parse100)
        yield fr

    def next_page(self, response):
        print '---- Got to next page'
        hxs = HtmlXPathSelector(response)
        print 'Page number : ', hxs.select(
                '//input[@name="%s"]/@value'%CURRENT_PAGE_INPUT).extract()
