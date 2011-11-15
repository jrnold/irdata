import collections
import datetime
import zipfile
import re
from os import path

import sqlalchemy as sa
import yaml

from irdata import xls
from irdata import model
from irdata.load import utils

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
    reader = xls.DictReader(src)
    for row in reader:
        for k in ('scode', 'country'):
            del row[k]
        session.add(model.PolityStateYear(**row))
    session.commit()

def load_polityd(src):
    session = model.SESSION()
    reader = xls.DictReader(src)
    columns = [x.name for x in model.PolityCase.__table__.c]
    cnt = collections.Counter()
    for row in reader:
        ccode = row['ccode']
        cnt[ccode] += 1
        row['pcase'] = cnt[ccode]
        row['present'] = row['present'] == '1'
        for i in ('e', 'b'):
            row['%sday' % i] = utils.replmiss(row['%sday' % i], lambda x: int(x) == 99)
            row['%smonth' % i] = utils.replmiss(row['%smonth' % i], lambda x: int(x) == 99)
            row['%syear' % i] = utils.replmiss(row['%syear' % i], lambda x: int(x) == 9999)
        if row['byear']:
            row['bdate'] = utils.row_ymd(row, 'byear', 'bmonth', 'bday')
        if row['eyear']:
            row['edate'] = utils.row_ymd(row, 'eyear', 'emonth', 'eday')
        session.add(model.PolityCase(**utils.subset(row, columns)))
    session.commit()

def load_all(data, external):
    """ Load all Polity 4 data """
    load_polity_states(open(path.join(data, 'polity4_states.yaml'), 'r'))
    load_polity(path.join(external, 'www.systemicpeace.org/inscr/p4v2010.xls'))
    load_polityd(path.join(external, 'www.systemicpeace.org/inscr/p4v2010d.xls'))

