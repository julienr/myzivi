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

DOWNLOAD_DELAY = 0.25

RETRY_ENABLED = True
RETRY_TIMES = 5

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ziviscrap (+http://www.yourdomain.com)'
