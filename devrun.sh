#!/bin/bash
export DJANGO_SETTINGS_MODULE=ziviweb.settings
export SENTRY_DSN=""
PYTHONPATH=.:$PYTHONPATH python $@
