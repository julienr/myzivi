##
import ziviscrap.settings as settings
import json
import logging
import multiprocessing
from datetime import datetime
import os, urlparse
from scrapy.selector import HtmlXPathSelector
import time
import collections
import ziviscrap.geocode as geocode
import ziviscrap.translations as translations
import guess_language

## Find duplicates
def filter_duplicates(items):
    nduplicates = 0
    itemdict = {}
    for i in items:
        if i['phid'] in itemdict:
            nduplicates += 1
        itemdict[i['phid']] = i
    logging.info('Number of duplicates : %d', nduplicates)
    return itemdict.values()

##
def parse_date_range(txt):
    start, end = txt.strip().split('-')
    start = datetime.strptime(start, '%d.%m.%Y').isoformat()
    end = datetime.strptime(end, '%d.%m.%Y').isoformat()
    return (start, end)

def parse_item(item):
    phid = item['phid']
    detailfile = os.path.join(settings.DETAIL_HTML_DIR, 'detail_%s.html'%phid)
    if not os.path.exists(detailfile):
        logging.info('File not found %s' % detailfile)
        return {}

    with open(detailfile) as f:
        detail = f.read()
    hxs = HtmlXPathSelector(text=detail)
    def span_text(id):
        r = hxs.select('//span[contains(@id, "%s")]/text()' % id).extract()
        if len(r) == 1:
            return r[0]
        else:
            logging.info('No "%s" found for phid : %s' % (id, phid))
            return ""

    data = item.copy()
    data['institution_name'] = span_text("EIBName")
    data['institution_description'] = span_text("EIBDescription")
    data['job_title'] = span_text("workSpecificationTitle")
    data['job_functions_list'] = '\n'.join(hxs.select(
        '//ul[contains(@class, "workSpecification-List")]/li/text()').
        extract())
    data['minimum_duration'] = span_text("minimumDurationValue")
    data['timemodel'] = span_text("workTimeModelValue")
    data['weekly_working_time'] = span_text("weeklyWorkingTimeValue")
    data['weekend_work'] = span_text("weekendWorkValue")
    data['night_work'] = span_text("nightlyWorkValue")
    data['lodging'] = span_text("lodgingValue")
    data['food'] = span_text("foodValue")

    data['ws_number'] = span_text("workSpecificationNumberValue")
    data['institution_number'] = span_text("EIBNumberValue")
    data['activity_domain'] = translations.to_activity_domain(
            span_text("fieldOfActivityValue"))
    data['priority_program'] = span_text("schwerpunktProgramValue")
    data['job_function_category'] = span_text("functionsValue")
    data['place_of_work'] = span_text("placeOfWorkValue")
    data['work_abroad'] = span_text("workAbroadValue")
    data['available_dates'] = hxs.select('//span[contains(@id, ' +
        '"freePeriodsLabel")]/following::table[1]//span/text()').extract()
    data['available_dates'] = [parse_date_range(d)
                               for d in data['available_dates']]
    return data

def geocode_item(item):
    newitem = item.copy()
    try:
        phid, place_of_work = item['phid'], item['place_of_work']
        address = geocode.geocode_address(place_of_work)
        newitem['address'] = address
    except geocode.GeocodingError as e:
        logging.exception('Error geocoding phid=%s, place_of_work=%s : %s ' + \
                          '(geourl:[%s])', phid, place_of_work, e, e.url)
        newitem['address'] = None
    return newitem

def translate_item(item):
    """Translate various item entries"""
    data = item.copy()
#    data['activity_field']

def add_lang(item):
    """Guess language for item"""
    lang = guess_language.guessLanguage(item['institution_description'])
    if lang == 'UNKNOWN':
        lang = guess_language.guessLanguage(item['job_functions_list'])

    if lang == 'UNKNOWN':
        logging.info('No language found for item %s' % item['phid'])
        return {}
    item['lang'] = lang
    return item


## Load Items from the scraper
jsonfile = urlparse.urlparse(settings.FEED_URI).path
with open(jsonfile) as f:
    items = json.load(f)

items = filter_duplicates(items)

## items transformations
def remove_empty(items):
    return filter(lambda d: len(d) > 0, items)

#pool = multiprocessing.Pool(5)
#items = pool.map(parse_item, items)
items = map(parse_item, items)
items = remove_empty(items)
#items = pool.map(geocode_item, items)
items = map(geocode_item, items)
items = remove_empty(items)
items = map(add_lang, items)
items = remove_empty(items)

## Remove items with empty addresses
items = filter(lambda i: i['address'] is not None, items)

## Save items completed with address
outfile = os.path.join(os.path.dirname(jsonfile), 'final_items.json')
with open(outfile, 'w') as f:
    json.dump(items, f, indent=2, sort_keys=True)

##
