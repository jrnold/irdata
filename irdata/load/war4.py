""" Load data from COW Inter-, Intra-, Non-State wars into the database """
## This code is pretty ugly because the data are not very clean, and organized in
## a non-relational way
# TODO: add the links between wars
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
    try:
        ccode = int(ccode) if int(ccode) > 0 else None
    except TypeError:
        ccode = None
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
        y.belligerent = belligerent_key(row['ccode'], row['state_name'])
        y.side = int(row['side']) == 2
        y.partic_num = n
        y.start_year = row['start_year%d' % n]
        y.start_month = row['start_month%d' % n]
        y.start_day = row['start_day%d' % n]
        if row['end_day%d' % n] == "-7":
            y.end_year = model.War4.ONGOING_DATE.year
            y.ongoing = True
        else:
            y.end_year = row['end_year%d' % n]
            y.ongoing = False
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
                    ccode = _int(ccode))
                session.add(obj)
            session.flush()
            
    def partic(row, belligerent, side):
        y = model.War4Partic()
        y.war_num = _int(row['war_num'])
        y.belligerent = belligerent
        y.side = (side == 'b')
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

    def partic_dates(row, belligerent, side, n):
        y = model.War4ParticDate()
        y.war_num = row['war_num']
        y.belligerent = belligerent
        y.side = (side == 'b')
        y.partic_num = n
        y.start_year = _int(row['start_year%d' % n])
        y.start_month = _int(row['start_month%d' % n])
        y.start_day = _int(row['start_day%d' % n])
        if row['end_day%d' % n] == "-7":
            y.end_year = model.War4.ONGOING_DATE.year
            y.ongoing = True
        else:
            y.end_year = _int(row['end_year%d' % n])
            y.ongoing = False
        if row['end_month%d' % n] == "-7":
            y.end_month = model.War4.ONGOING_DATE.month
        else:
            y.end_month = _int(row['end_month%d' % n])
        if row['end_month%d' % n] == "-7":        
            y.end_day = model.War4.ONGOING_DATE.day
        else:
            y.end_day = _int(row['end_day%d' % n])
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
        if _side(row['side_a']):
            add_belligerent(session, row['side_a'], row['ccode_a'])
            belligerent = belligerent_key(row['ccode_a'], row['side_a'])
            session.add(partic(row, belligerent, 'a'))
            session.add(partic_dates(row, belligerent, 'a', 1))
            if row['start_year2'] != '-8':
                session.add(partic_dates(row, belligerent, 'a', 2))
        if _side(row['side_b']):
            add_belligerent(session, row['side_b'], row['ccode_b'])
            belligerent = belligerent_key(row['ccode_b'], row['side_b'])
            session.add(partic(row, belligerent, 'b'))
            session.add(partic_dates(row, belligerent, 'b', 1))
            if row['start_year2'] != '-8':
                session.add(partic_dates(row, belligerent, 'b', 2))
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
                    belligerent_name = name,
                    ccode = ccode)
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

    def partic_dates(row, name, side):
        y = model.War4ParticDate()
        y.war_num = row['war_num']
        y.belligerent = belligerent_key(None, name)
        y.side = side
        y.partic_num = 1
        y.start_year = _int(row['start_year'])
        y.start_month = _int(row['start_month'])
        y.start_day = _int(row['start_day'])
        if row['end_year'] == "-7":
            y.end_year = model.War4.ONGOING_DATE.year
            y.ongoing = True
        else:
            y.end_year = _int(row['end_year'])
            y.ongoing = False
        if row['end_month'] == "-7":
            y.end_month = model.War4.ONGOING_DATE.month
        else:
            y.end_month = _int(row['end_month'])
        if row['end_month'] == "-7":        
            y.end_day = model.War4.ONGOING_DATE.day
        else:
            y.end_day = _int(row['end_day'])
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
                                       bat_death = _int(row['side_%sdeaths' % side])))
        session.flush()
        for i in (1, 2):
            name = row['side_a%d' % i]
            if name != '-8':
                add_belligerent(session, name)
                session.add(partic(row, 'a', name))
                session.add(partic_dates(row, name, False))
        for i in range(1, 6):
            name = row['side_b%d' % i]
            if name != '-8':
                add_belligerent(session, name)
                session.add(partic(row, 'b', name))
                session.add(partic_dates(row, name, True))
        session.flush()
    session.commit()

def load_war4_links(inter, intra, nonstate):
    session = model.SESSION()
    
    def _int(x):
        y = int(x)
        return y if y > 0 else None

    def clean(x):
        return [_int(y.strip()) for y in x.split(',')]

    def load_link(war_from, war_to):
        if war_from and war_to:
            q = session.query(model.War4Link).\
                filter(model.War4Link.war_from == war_from).\
                filter(model.War4Link.war_to == war_to)
            if q.count() == 0:
                session.add(model.War4Link(war_from=war_from,
                                           war_to=war_to))
    
    def load_file(src):
        reader = csv2.DictReader(src, encoding='latin-1')
        reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]
        for row in reader:
            print row
            war_num = int(row['war_num'])
            for x in clean(row['trans_from']):
                load_link(x, war_num)
            for x in clean(row['trans_to']):
                load_link(war_num, x)

    load_file(inter)
    load_file(intra)
    load_file(nonstate)
    session.commit()

def load_all(data, external):
    """ Load all COW War v. 4 data """
    inter = path.join(data, "InterStateWarData_v4.0.csv")
    intra = path.join(data, "IntraStateWarData_v4.1.csv")
    nonstate = path.join(data, "NonStateWarData_v4.0.csv")
    load_cow_war_types(open(path.join(data, "cow_war_types.yaml"), "r"))
    utils.load_enum_from_yaml(open(path.join(data, "war4_enum.yaml"), "r"))
    load_war4(open(inter, 'rU'))
    load_war4_intra(open(intra, 'rU'))
    load_war4_nonstate(open(nonstate, 'rU'))
    load_war4_links(open(inter, 'rU'), open(intra, 'rU'), open(nonstate, 'rU'))
            
                    
