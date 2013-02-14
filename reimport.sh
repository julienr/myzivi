#!/bin/bash
# execute postprocess and import_items using given _data directory
DDIR=$PWD/$1
if [ ! -d "$DDIR" ]; then
	echo "Directory doesn't exist : $DDIR"
	exit 1
fi
export SCRAPY_DATA_DIR=$DDIR
export PYTHONPATH=.:/home/myzivi/django-myzivi:$PYTHONPATH
export DJANGO_SETTINGS_MODULE=ziviweb.settings_deployment
# Postprocess (geotagging, translation, ...)
python ziviscrap/postprocess.py
# Insert into DB
python zivimap/import_items.py
