#!/bin/bash
DDIR=$PWD/_data/scraped_`date +%F-%T`
mkdir -p $DDIR
SCRAPY_DATA_DIR=$DDIR scrapy crawl zivi
