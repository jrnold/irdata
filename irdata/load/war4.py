""" Load data from COW Inter-, Intra-, Non-State wars into the database """
## This code is pretty ugly because the data are not very clean, and organized in
## a non-relational way
# TODO: add participant dates for Intra-, and Non-State wars
# TODO: add the relationships between wars
import collections
import datetime
import zipfile
import re
from os import path

import sqlalchemy as sa
import yaml

from irdata import csv2
from irdata import model
from irdata.load import utils

def load_cow_war_types(src):
    """ Load data into cow_war_types table """
    utils.load_from_yaml(src, model.CowWarType.__table__)


def belligerent_key(ccode, name):
    """ Create primary key for belligerents

    Create a unique key for ccode, name combinations

    :param ccode: int. country code
    :param name: str. belligerent name
    :rtype: str. belligerent key
    """
    return u"%s %s" % (ccode, name)

def load_war4(src):
    """ Add Inter-state war data to war4_* tables
    
    updates tables cow_war4, cow_belligerents, cow_war4_participation, cow_war4_partic_dates
    """

    def partic(row):
        y = model.War4Partic()
        y.war_num = int(row['war_num'])
        y.belligerent = belligerent_key(row['ccode'], row['state_name'])
        y.side = int(row['side']) == 2
        y.where_fought = row['where_fought']
        y.outcome = row['outcome']
        y.bat_death = row['bat_death']
        y.initiator = (int(row['initiator']) == 1)
        return y

    def partic_dates(row, n):
        y = model.War4ParticDate()
        y.war_num = row['war_num']
        ccode = int(row['ccode'])
        row['ccode'] = ccode if ccode > 0 else None
        y.belligerent = belligerent_key(row['ccode'], row['state_name'])
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
        belligerent = belligerent_key(row['ccode'], row['state_name'])
        cnt[war_num] += 1
        cnt_bellig[belligerent] +=1 
        if cnt[war_num] == 1:
            session.add(model.War4(intnl=True, **utils.subset(row, cols)))
            for side in (False, True):
                session.add(model.War4Side(side=side, war_num=row['war_num']))
            session.flush()
        if cnt_bellig[belligerent] == 1:
            session.add(model.War4Belligerent(belligerent = belligerent,
                                              belligerent_name = row['state_name'],
                                              ccode = row['ccode']))
            session.flush()
        session.add(partic(row))
        session.add(partic_dates(row, 1))
        if row['end_year2'] != '-8':
            session.add(partic_dates(row, 2))
    session.commit()

def load_war4_intra(src):
    """ Add Intra-state war data to war4_* tables

    updates tables cow_war4, cow_belligerents, cow_war4_participation, cow_war4_partic_dates
    """
    def _int(x):
        try:
            y = int(re.sub(',', '', x))
            return y if y > 0 else None
        except TypeError:
            return None

    def _side(x):
        return x if x != "-8" else  None

    def add_belligerent(session, name, ccode):
        if name != "-8":
            belligerent = belligerent_key(ccode, name)
            q = session.query(model.War4Belligerent).\
                filter(model.War4Belligerent.belligerent == belligerent)
            if q.count() == 0:
                obj = model.War4Belligerent(
                    belligerent = belligerent,
                    belligerent_name = name,
                    ccode = ccode)
                session.add(obj)
            session.flush()
            
    def partic(row, side):
        y = model.War4Partic()
        y.war_num = _int(row['war_num'])
        y.belligerent = belligerent_key(_int(row['ccode_%s' % side]),
                                        unicode(row['side_%s' % side]))
        y.side = side == "b"
        y.where_fought = row['where_fought']
        ## outcomes given in Side A / Side B rather than winner/loser
        ## per participant
        outcome = _int(row['outcome'])
        if side:
            if outcome == 2: outcome = 1
            elif outcome == 1: outcome = 2
        y.outcome = outcome
        y.bat_death = _int(row['side_%sdeaths' % side])
        y.initiator = (row['initiator'] == y.belligerent)
        return y
    
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
                                      intnl = row['intnl'] == '1'))
            for side in (False, True):
                session.add(model.War4Side(side=side, war_num=row['war_num']))
            session.flush()
        add_belligerent(session, row['side_a'], _int(row['ccode_a']))
        add_belligerent(session, row['side_b'], _int(row['ccode_b']))
        if _side(row['side_a']):
            session.add(partic(row, 'a'))
        if _side(row['side_b']):
            session.add(partic(row, 'b'))
        session.flush()
        
    session.commit()

def load_war4_nonstate(src):
    def _int(x):
        try:
            y = int(re.sub(',', '', x))
            return y if y > 0 else None
        except TypeError:
            return None

    def _side(x):
        return x if x != "-8" else  None

    def add_belligerent(session, name):
        ccode = None
        if name != "-8":
            belligerent = belligerent_key(ccode, name)
            q = session.query(model.War4Belligerent).\
                filter(model.War4Belligerent.belligerent == belligerent)
            if q.count() == 0:
                obj = model.War4Belligerent(
                    belligerent = belligerent,
                    belligerent_name = name)
                session.add(obj)
            session.flush()
            
    def partic(row, side, name):
        y = model.War4Partic()
        y.war_num = _int(row['war_num'])
        y.belligerent = belligerent_key(None, name)
        y.side = side == "b"
        y.where_fought = row['where_fought']
        outcome = _int(row['outcome'])
        if side:
            if outcome == 2: outcome = 1
            elif outcome == 1: outcome = 2
        y.outcome = outcome
        y.initiator = (row['initiator'] == side.upper())
        return y

    session = model.SESSION()
    reader = csv2.DictReader(src, encoding='latin1')
    reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]
    for row in reader:
        war_num = row['war_num']
        ## Add war
        session.add(model.War4(war_num = war_num,
                               war_name = row['war_name'],
                               war_type = int(row['war_type']),
                               bat_deaths = _int(row['total_combat_deaths'])))
        for side in ('a', 'b'):
            session.add(model.War4Side(side=(side == 'b'),
                                       war_num=row['war_num'],
                                       bat_death = row['side_%sdeaths' % side]))
        session.flush()
        for i in (1, 2):
            name = row['side_a%d' % i]
            if name != '-8':
                add_belligerent(session, name)
                session.add(partic(row, 'a', name))
        for i in range(1, 6):
            name = row['side_b%d' % i]
            if name != '-8':
                add_belligerent(session, name)
                session.add(partic(row, 'b', name))
        session.flush()
    session.commit()


def load_all(data, external):
    """ Load all COW War v. 4 data """
    load_cow_war_types(open(path.join(data, "cow_war_types.yaml"), "r"))
    utils.load_enum_from_yaml(open(path.join(data, "war4_enum.yaml"), "r"))
    load_war4(open(path.join(data, "InterStateWarData_v4.0.csv"), 'rU'))
    load_war4_intra(open(path.join(data, "IntraStateWarData_v4.1.csv"), 'rU'))
    load_war4_nonstate(open(path.join(data, "NonStateWarData_v4.0.csv"), 'rU'))    
