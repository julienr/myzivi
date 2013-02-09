#!/bin/bash
DDIR=$PWD/_data/scraped_`date +%F-%T`
mkdir -p $DDIR
export SCRAPY_DATA_DIR=$DDIR
export PYTHONPATH=.:$PYTHONPATH
# Crawler
scrapy crawl zivi
# Postprocess (geotagging, translation, ...)
python ziviscrap/postprocess.py
# Insert into DB
python zivimap/import_items.py
