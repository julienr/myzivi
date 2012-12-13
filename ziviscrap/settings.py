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

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'ziviscrap (+http://www.yourdomain.com)'
