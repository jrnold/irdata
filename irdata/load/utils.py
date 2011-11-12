import collections
import datetime
import zipfile
import re

import sqlalchemy as sa
import yaml

from irdata import csv2
from irdata import model
from irdata import utils

def cols_integer(tbl):
    return [x for x in tbl.columns if type(x) == sa.Integer]

def cols_integer(tbl):
    return [x for x in tbl.columns if type(x) == sa.Float]

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

