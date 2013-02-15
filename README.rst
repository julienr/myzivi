myzivi.ch
=========
This is the source code for the http://myzivi.ch website.

myzivi.ch allows user to search for swiss civilian service assignments using
an interactive Google Map with assignments locations shown.

technologies
============
This site uses Django_ for the server-side web framework.
Scrapy_ is used to scrape the official_ database.
Bootstrap_ is used for CSS, while the Javascript frontend uses backbone.js_,
django-tastypie and MarkerClustererPlus.
Sentry_ is used on the production server to monitor crawling errors.

.. _Django: http://www.djangoproject.com/
.. _Scrapy: http://scrapy.org/
.. _official: https://www.eis.zivi.admin.ch/ZiviEis/default.aspx?lang=fr
.. _Bootstrap: http://twitter.github.com/bootstrap/
.. _backbone.js: http://backbonejs.org/
.. _Sentry: https://getsentry.com/welcome/


license
=======
myzivi.ch is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

myzivi.ch is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with myzivi.ch.  If not, see <http://www.gnu.org/licenses/>
