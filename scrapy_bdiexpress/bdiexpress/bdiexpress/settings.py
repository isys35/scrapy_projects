

BOT_NAME = 'bdiexpress'

SPIDER_MODULES = ['bdiexpress.spiders']
NEWSPIDER_MODULE = 'bdiexpress.spiders'


FEED_FORMAT = "csv"
FEED_URI = "data.csv"
DOWNLOAD_DELAY = 0.15


ROBOTSTXT_OBEY = False


