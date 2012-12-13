import re
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import FormRequest

from ziviscrap.items import WorkSpecItem

phid_re = re.compile(r'.*?phid=(?P<phid>COO\.\d{4}\.\d{3}\.\d\.\d+).*$')


class ZiviSpider(BaseSpider):
    name = "zivi"
    allowed_domains = ["www.eis.zivi.admin.ch"]
    start_urls = [
        "https://www.eis.zivi.admin.ch/ZiviEis/ModuleDisplayPage.aspx?functionId=123F61E5-F417-4F51-AC59-906D6F999D02"
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        workspecs_a = hxs.select('//a[contains(@id, "workSpecificationList_workSpecificationTitle")]')
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

        formdata = {'ctl00$CommonScriptManager':'tl00$cphContent$ctl04$workSpecificationList$TableUpdatePanel|ctl00$cphContent$ctl04$workSpecificationList$workSpecificationPagingBar$onePageForwardButton',
                'ctl00$cphContent$ctl04$workSpecificationList$workSpecificationPagingBar$currentPageValue':'2'} # TODO: replace 2 by +1
#        fr = FormRequest.from_response(response, dont_click=True,
#                formdata=formdata, callback=self.next_page)
        fr = FormRequest.from_response(response, dont_click=True,
                formdata=formdata)
        yield fr

    def next_page(self, response):
        print '---- Got to next page'
        hxs = HtmlXPathSelector(response)
        print 'Page number : ', hxs.select('//input[@name="ctl00$cphContent$ctl04$workSpecificationList$workSpecificationPagingBar$currentPageValue"]/@value').extract()
