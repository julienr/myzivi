"""
Adaptation of django.forms.extra.SelectDateWidget to show only month and year
"""
from __future__ import unicode_literals

import datetime
import re
import calendar

from django.forms.widgets import Widget, Select
from django.utils import datetime_safe
from django.utils.dates import MONTHS
from django.utils.encoding import force_str
from django.utils.safestring import mark_safe
from django.utils.formats import get_format
from django.utils import six
from django.conf import settings

__all__ = ('SelectDateWidget',)

class SelectMonthYearWidget(Widget):
    """
    A Widget that splits date input into two <select> boxes and allow selection
    of month/year
    """
    none_value = (0, '---')
    month_field = '%s_month'
    year_field = '%s_year'

    def __init__(self, defaultdate, day, attrs=None, years=None,
                 required=True):
        # dayval is the value that will be set for the days. Can be 'first'
        # or 'last'
        # years is an optional list/tuple of years to use in the "year" select box.
        self.attrs = attrs or {}
        self.required = required
        self.dayval = day
        self.defaultdate = defaultdate
        if years:
            self.years = years
        else:
            this_year = datetime.date.today().year
            self.years = range(this_year, this_year+10)

    def render(self, name, value, attrs=None):
        try:
            year_val, month_val = value.year, value.month
        except AttributeError:
            year_val, month_val = self.defaultdate.year, self.defaultdate.month

        choices = [(i, i) for i in self.years]
        year_html = self.create_select(name, self.year_field, value, year_val, choices)
        choices = list(six.iteritems(MONTHS))
        month_html = self.create_select(name, self.month_field, value, month_val, choices)

        output = [month_html, year_html]
        return mark_safe('\n'.join(output))

    def id_for_label(self, id_):
        return '%s_month' % id_

    def value_from_datadict(self, data, files, name):
        y = data.get(self.year_field % name)
        m = data.get(self.month_field % name)
        if y == m == "0": # No selection
            return None
        if y and m:
            y = int(y)
            m = int(m)
            if self.dayval == 'first':
                day = 1
            else:
                day = calendar.monthrange(y, m)[1]
            return datetime.date(int(y), int(m), day)
        else:
            return None

    def create_select(self, name, field, value, val, choices):
        if 'id' in self.attrs:
            id_ = self.attrs['id']
        else:
            id_ = 'id_%s' % name
        #if not (self.required and val):
            #choices.insert(0, self.none_value)
        local_attrs = self.build_attrs(id=field % id_)
        local_attrs['class'] = field % 'select'
        s = Select(choices=choices)
        select_html = s.render(field % name, val, local_attrs)
        return select_html
