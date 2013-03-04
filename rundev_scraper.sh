#!/bin/bash
DDIR=$PWD/_data/scraped_`date +%F-%T`
mkdir -p $DDIR
export SENTRY_DSN=""
export SCRAPY_DATA_DIR=$DDIR
export PYTHONPATH=.:/home/myzivi/django-myzivi:$PYTHONPATH
export DJANGO_SETTINGS_MODULE=ziviweb.settings
# Crawler
scrapy crawl zivi
# Postprocess (geotagging, translation, ...)
python ziviscrap/postprocess.py
# Insert into DB
python zivimap/import_items.py
# Delete old scraped directory
python rotate_data.py
