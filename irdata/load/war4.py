import collections
import datetime
import zipfile
import re

import sqlalchemy as sa
import yaml

from irdata import csv2
from irdata import model
from irdata import utils
from .utils import replmiss

def load_war4(src):
    """ COW Inter-State War v 4.0

    updates tables cow_war4, cow_belligerents, cow_war4_participation, cow_war4_partic_dates
    """

    def partic(row):
        y = model.War4Partic()
        y.war_num = int(row['war_num'])
        y.belligerent = unicode(row['state_name'])
        y.side = int(row['side']) == 2
        y.where_fought = row['where_fought']
        y.outcome = row['outcome']
        y.bat_death = row['bat_death']
        y.initiator = (int(row['initiator']) == 1)
        return y

    def partic_dates(row, n):
        y = model.War4ParticDate()
        y.war_num = row['war_num']
        y.belligerent = row['state_name']
        y.side = int(row['side']) == 2
        y.partic_num = n
        y.start_year = row['start_year%d' % n]
        y.start_month = row['start_month%d' % n]
        y.start_day = row['start_day%d' % n]
        if row['start_day%d' % n] == "-7":
            y.end_year = model.War4.ONGOING_DATE.year
        else:
            y.end_year = row['end_year%d' % n]
        if row['end_month%d' % n] == "-7":
            y.end_month = model.War4.ONGOING_DATE.month
        else:
            y.end_month = row['end_month%d' % n]
        if row['end_month%d' % n] == "-7":        
            y.end_day = model.War4.ONGOING_DATE.day
        else:
            y.end_day = row['end_day%d' % n]

        return y
        
    cols = ("war_num", "war_name", "war_type")
    session = model.SESSION()
    cnt = collections.Counter()
    cnt_bellig = collections.Counter()
    reader = csv2.DictReader(src)
    reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]
    for row in reader:
        war_num = row['war_num']
        state_name = row['state_name']
        cnt[war_num] += 1
        cnt_bellig[state_name] +=1 
        if cnt[war_num] == 1:
            session.add(model.War4(intnl=True, **utils.subset(row, cols)))
            for side in (False, True):
                session.add(model.War4Side(side=side, war_num=row['war_num']))
        if cnt_bellig[row['state_name']] == 1:
            session.add(model.War4Belligerent(belligerent = row['state_name'],
                                                  ccode = row['ccode']))
        session.add(partic(row))
        session.add(partic_dates(row, 1))
        if row['end_year2'] != '-8':
            session.add(partic_dates(row, 2))
    session.commit()

def load_war4_intra(src):
    def _int(x):
        try:
            y = int(re.sub(',', '', x))
            return y if y > 0 else None
        except TypeError:
            return None

    def _side(x):
        return x if x != "-8" else  None

    def add_belligerent(session, belligerent, ccode):
        if belligerent != "-8":
            q = session.query(model.War4Belligerent).\
                filter(model.War4Belligerent.belligerent == belligerent)
            if q.count() == 0:
                obj = model.War4Belligerent(ccode = ccode,
                                                belligerent = belligerent)
                session.add(obj)

    def partic(row, side):
        y = model.War4Partic()
        y.war_num = _int(row['war_num'])
        y.belligerent = unicode(row['side_%s' % side])
        y.side = side == "b"
        y.where_fought = row['where_fought']
        y.outcome = row['outcome']
        y.bat_death = _int(row['side_%sdeaths' % side])
        y.initiator = (row['initiator'] == y.belligerent)
        return y
    
    session = model.SESSION()
    session = model.SESSION()
    cnt = collections.Counter()
    reader = csv2.DictReader(src, encoding='latin1')
    reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]
    for row in reader:
        war_num = row['war_num']
        cnt[war_num] += 1
        ## Add war
        if cnt[war_num] == 1:
            session.add(model.War4(war_num = war_num,
                                      war_name = row['war_name'],
                                      war_type = int(row['war_type']),
                                      intnl = bool(row['intnl'])))
            for side in (False, True):
                session.add(model.War4Side(side=side, war_num=row['war_num']))
        add_belligerent(session, row['side_a'], _int(row['ccode_a']))
        add_belligerent(session, row['side_b'], _int(row['ccode_b']))
        if _side(row['side_a']):
            session.add(partic(row, 'a'))
        if _side(row['side_b']):
            session.add(partic(row, 'b'))
        session.flush()
        
    session.commit()
