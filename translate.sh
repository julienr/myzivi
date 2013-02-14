#!/bin/sh
cd zivimap
django-admin.py makemessages -a
django-admin.py compilemessages
cd ..
