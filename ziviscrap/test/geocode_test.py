import os
import urllib2
import unittest
from mock import patch
from StringIO import StringIO
import ziviscrap.testdata as testdata
import ziviscrap.geocode as geocode

datapath = os.path.dirname(testdata.__file__)

class TestNominatimGeocode(unittest.TestCase):
    def test_sample_data(self):
       with open(os.path.join(datapath, 'geocode_nominatim.json')) as f:
            jsondata = f.read()
       with patch('urllib2.urlopen') as mock:
           mock.return_value = StringIO(jsondata)
           address = geocode._nominatim_geocode('')
       assert address['canton'] == 'Fribourg'
       assert address['locality'] == 'Estavayer-le-Lac'
       assert address['latitude'] == '46.8511962'
       assert address['longitude'] == '6.8496797'
       assert address['formatted_address'] == 'Estavayer-le-Lac, District de '\
                                              'la Broye, Fribourg, Switzerland'

class TestGoogleGeocode(unittest.TestCase):
    def test_sample_data(self):
        with open(os.path.join(datapath, 'geocode_google.json')) as f:
            jsondata = f.read()
        with patch('urllib2.urlopen') as mock:
            mock.return_value = StringIO(jsondata)
            address = geocode._google_geocode('')
        assert address['canton'] == 'Canton of Fribourg'
        assert address['locality'] == 'Estavayer-le-Lac'
        assert address['latitude'] == 46.849340
        assert address['longitude'] == 6.847530000000001
        assert address['formatted_address'] == '1470 Estavayer-le-Lac, '\
                                               'Switzerland'
