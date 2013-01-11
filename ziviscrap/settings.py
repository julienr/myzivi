# Scrapy settings for ziviscrap project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/topics/settings.html
#

BOT_NAME = 'ziviscrap'

SPIDER_MODULES = ['ziviscrap.spiders']
NEWSPIDER_MODULE = 'ziviscrap.spiders'

LOG_LEVEL = 'INFO'
DATA_DIR = '/home/julien/dev/zivi/_data/scraped/'
DETAIL_HTML_DIR = DATA_DIR + 'detail_html/'

FEED_FORMAT = 'json'
FEED_URI = 'file://' + DATA_DIR + 'items.json'

LOG_FILE = DATA_DIR + 'log.txt'
LOG_LEVEL = 'DEBUG'

DOWNLOAD_DELAY = 0.1

RETRY_ENABLED = True
RETRY_TIMES = 5

# Disable redirect because the website redirects us on 500 error
REDIRECT_ENABLED = False
# Retry 500 and 404 because sometimes, temporary errors seem to cause the
# server to return 404, but the page exists on next try
RETRY_HTTP_CODES = [500, 503, 504, 400, 404, 408, 300, 307]

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ziviscrap (+http://www.yourdomain.com)'
USER_AGENT = "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.1.16) Gecko/20120421 Firefox/11.0"
