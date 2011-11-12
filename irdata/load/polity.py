import collections
import datetime
import zipfile
import re

import sqlalchemy as sa
import yaml

from irdata import csv2
from irdata import model
from irdata import utils

def load_polity_states(src):
    POLITY_MAX_YEAR = model.PolitySysMembership.ONGOING
    session = model.SESSION()
    data = yaml.load(src)
    cnt = collections.Counter()
    for x in data:
        ccode = x['ccode']
        cnt[ccode] += 1
        x['end_year'] = x['end_year'] if x['end_year'] else POLITY_MAX_YEAR
        session.add(model.PolitySysMembership(interval = cnt[ccode],
                                        **utils.subset(x, ('ccode', ''))))
    session.commit()

def load_polity_states(src):
    session = model.SESSION()
    data = yaml.load(src)
    cnt = collections.Counter()
    cols1 = ('ccode', 'scode', 'country')
    cols2 = ('ccode', 'start_year', 'end_year')
    for row in data:
        cnt[row['ccode']] += 1
        if cnt[row['ccode']] == 1:
            data1 = utils.subset(row, cols1)
            session.add(model.PolityState(**data1))
        if not row['end_year']:
            row['end_year'] = model.PolitySysMembership.ONGOING
        data2 = utils.subset(row, cols2)
        data2['interval'] =  cnt[row['ccode']]
        session.add(model.PolitySysMembership(**data2))
    session.commit()

def load_polity(src):
    session = model.SESSION()
    reader = csv2.DictReader(src)
    for row in reader:
        for k in ('scode', 'country'):
            del row[k]
        session.add(model.PolityStateYear(**row))
    session.commit()
