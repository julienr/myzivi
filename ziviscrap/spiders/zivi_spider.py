import re
import os.path
import os, errno
from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import Request, FormRequest
from scrapy import log
from scrapy.utils.url import urljoin_rfc
from ziviscrap.items import WorkSpecItem
import ziviscrap.settings as settings

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

phid_re = r'.*?phid=(COO\.\d{4}\.\d{3}\.\d\.\d+).*$'

ZIVI_DOMAIN = "www.eis.zivi.admin.ch"
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
    """
    Parse ZIVI SIA (job search page).

    'parse' is called first. It will simply simulate a form request to change
        the number of items per page from 10 to 100.
    'parse_workspecs_list' is then called to actually parse the workspecs. It
        will parse pages one by one
    'parse_workspec_page' is called to parse the detailed information of a
        workspec. Instead of parsing these informations here, we simply save
        a dump of the page, and do the processing offline

    A few remarks regarding zivi's website :
        - It uses ASP.NET and therefore has a lot of hidden forms with
          _VIEWSTATE and other variables. Googling for "scrapy VIEWSTATE" or
          similar gives good informations regarding those types of pages
        - The first time we get on the workspec list page, the workspecs shown
          are in somewhat random order (if they are equal wrt the ordering
          criteria, they are random). It seems like a session is used for each
          visitor to avoid serving him the same list twice. Scrapy seems to
          handle that nicely
    """
    name = "zivi"
    allowed_domains = [ZIVI_DOMAIN]
    start_urls = [WORKSPEC_LIST_URL]

    def parse(self, response):
        log.msg('parse : [%s]' % response.url)
        formdata = {POST_PAGE_SIZE: '100'}
        return FormRequest.from_response(response, dont_click=True,
                formdata=formdata, callback=self.parse_workspecs_list)

    def parse_workspecs_list(self, response):
        log.msg('parse_workspecs_list : [%s]' % response.url)
        hxs = HtmlXPathSelector(response)
        current_page = extract_current_page(hxs)
        total_pages = extract_total_pages(hxs)
        log.msg('Current page : %d / %d' % (current_page, total_pages))
        workspecs_a = hxs.select('//a[contains(@id, "%s")]' % WORKSPEC_A_ID)
        log.msg('Number of workspecs : %d' % len(workspecs_a))
        for a in workspecs_a:
            item = WorkSpecItem()
            item['shortname'] = a.select('text()').extract()[0]
            url = a.select('@href').extract()[0]
            item['url'] = url
            item['phid'] = a.select('@href').re(phid_re)[0]
            yield item
            full_url = urljoin_rfc(response.url, url)
            self.crawler.stats.inc_value('workspec_pages_queued')
            yield Request(full_url, callback=self.parse_workspec_page,
                          dont_filter=True,
                          meta={'phid':item['phid']})

        if current_page < total_pages:
        # TODO: Remove this, debug only
        #if current_page < 3:
            formdata = {CURRENT_PAGE_INPUT :str(current_page + 1)}
            yield FormRequest.from_response(response, dont_click=True,
                    formdata=formdata, callback=self.parse_workspecs_list)

    def parse_workspec_page(self, response):
        log.msg('parse_workspec_page : [%s]' % response.url)
        phid = response.meta['phid']
        mkdir_p(settings.DETAIL_HTML_DIR)
        path = os.path.join(settings.DETAIL_HTML_DIR, 'detail_%s.html' % phid)
        with open(path, 'w') as f:
            f.write(response.body)
        self.crawler.stats.inc_value('workspec_pages_written')
        log.msg('Detail page saved to %s' % path)

