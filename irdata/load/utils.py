import collections
import datetime
import zipfile
import re
import calendar

import sqlalchemy as sa
from sqlalchemy import types
import yaml

from irdata import csv2
from irdata import model


def camel2under(x):
    """Convert Camelcase words to underscore separated words

    >>> camel2under("HelloWorld")
    hello_world

    """
    return re.sub(r"(?<=[a-z])([A-Z])", r"_\1", x).lower()

def subset(d, keys):
    """ Subset a dictionary """
    return dict((k, v) for k, v in d.iteritems() if k in keys)

def cols_by_type(tbl, _type):
    """ Names of columns in a Table of a certain type"""
    return [x for x in tbl.columns if type(x) == _type]

def row_ymd(row, y, m, d):
    return datetime.date(*(int(row[x]) for x in (y, m, d)))

def replmiss(x, f):
    return x if not f(x) else None

def load_from_yaml(src, tbl):
    """ Load from yaml file

    Data must be a list of dicts, with each element in the list
    being a row, and each key in the dict being a column.
    """
    data = yaml.load(src)
    tbl.insert().execute(data)

def load_enum_from_yaml(src):
    """ Load dict of dicts into tables with key/value combinations """ 
    session = model.SESSION()
    for tbl, v in yaml.load(src).iteritems():
        data = []
        for value, label in v.iteritems():
            data.append({'value': unicode(value),
                        'label': unicode(label)})
        model.Base.metadata.tables[tbl].insert().execute(data)
    session.commit()

def last_day_of_month(year, month):
    return calendar.monthrange(year, month)[1]

def daterng(y, m, d):
    if y:
        if m:
            if d:
                dt_min = datetime.date(y, m, d)
                dt_max = dt_min
            else:
                dt_min = datetime.date(y, m, 1)
                dt_max = datetime.date(y, m, last_day_of_month(y, m))
        else:
            dt_min = datetime.date(y, 1, 1)
            dt_max = datetime.date(y, 12, 31)
    else:
        dt_min = dt_max = None
    return (dt_min, dt_max)
                
