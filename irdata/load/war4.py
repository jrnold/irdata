""" Load data from COW Inter-, Intra-, Non-State wars into the database """
## This code is pretty ugly because the data are not very clean, and organized in
## a non-relational way
# TODO: add the links between wars
import sys
import collections
import datetime
import zipfile
import pkgutil
import re
from os import path

import sqlalchemy as sa
import yaml

from irdata import csv2
from irdata import model
from irdata.load import utils

KLS = (model.CowWarType,
        model.War4Outcome,
        model.War4,
        model.War4Side,
        model.War4Partic,
        model.War4Belligerent,
        model.War4ParticDate,
        model.War4List)

WHERE_FOUGHT = {1: {"west_hem": True,
                    "europe": False,
                    "africa": False,
                    "mid_east": False,
                    "asia": False,
                    "oceania": False},
                2: {"west_hem": False,
                    "europe": True,
                    "africa": False,
                    "mid_east": False,
                    "asia": False,
                    "oceania": False},
                4: {"west_hem": False,
                    "europe": False,
                    "africa": True,
                    "mid_east": False,
                    "asia": False,
                    "oceania": False},
                6: {"west_hem": False,
                    "europe": False,
                    "africa": False,
                    "mid_east": True,
                    "asia": False,
                    "oceania": False},
                7: {"west_hem": False,
                    "europe": False,
                    "africa": False,
                    "mid_east": False,
                    "asia": True,
                    "oceania": False},
                9: {"west_hem": False,
                    "europe": False,
                    "africa": False,
                    "mid_east": False,
                    "asia": False,
                    "oceania": True},
                11: {"west_hem": False,
                    "europe": True,
                    "africa": False,
                    "mid_east": True,
                    "asia": False,
                    "oceania": False},
                12: {"west_hem": False,
                    "europe": True,
                    "africa": False,
                    "mid_east": False,
                    "asia": True,
                    "oceania": False},
                13: {"west_hem": True,
                    "europe": False,
                    "africa": False,
                    "mid_east": False,
                    "asia": True,
                    "oceania": False},
                14: {"west_hem": False,
                    "europe": True,
                    "africa": True,
                    "mid_east": True,
                    "asia": False,
                    "oceania": False},
                15: {"west_hem": False,
                    "europe": True,
                    "africa": True,
                    "mid_east": True,
                    "asia": True,
                    "oceania": False},
                16: {"west_hem": False,
                    "europe": False,
                    "africa": True,
                    "mid_east": True,
                    "asia": True,
                    "oceania": True},
                17: {"west_hem": False,
                    "europe": False,
                    "africa": False,
                    "mid_east": False,
                    "asia": True,
                    "oceania": True},
                18: {"west_hem": False,
                    "europe": False,
                    "africa": True,
                    "mid_east": True,
                    "asia": False,
                    "oceania": False},
                19: {"west_hem": False,
                    "europe": True,
                    "africa": True,
                    "mid_east": True,
                    "asia": True,
                    "oceania": True}}
""" Dictionary mapping numbers in WhereFought to region boolean variables

See Documentation: http://www.correlatesofwar.org/COW2%20Data/WarData_NEW/InterStateWars_Codebook.pdf
"""

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

def war_side_pkey(war_num, side):
    """ Create primary key for war_side

    Create a unique key for war_num, side combinations

    :param war_num: int. war number
    :param side: int. side of war
    """
    return ("%s,%s" % (war_num, int(side)))

def war_partic_pkey(war_side, belligerent):
    """ Create primary key for war_side

    Create a unique key for war_num, side combinations

    :param war_side: str. war_side key
    :param belligerent: str. belligerent
    """
    return ("%s,%s" % (war_side, belligerent))


def load_war4_list(src):
    """ Load war4_list """
    session = model.SESSION()
    PAT = re.compile(r"\d{4} +(?P<name>.*) +(?P<type>Intra|Extra|Non|Inter)-State War +#(?P<warnum>\d+)")
    for line in src:
        m = PAT.match(line)
        if m:
            session.add(model.War4List(war_num = int(m.group('warnum')),
                                       war_name = unicode(m.group('name').strip(), 'utf-8')))
    session.commit()


def load_war4_inter(src):
    """ Add Inter-state war data to war4_* tables
    
    updates tables cow_war4, cow_belligerents, cow_war4_participation, cow_war4_partic_dates
    """
    session = model.SESSION()

    def _int(x):
        y = int(x)
        return y if y >= 0 else None

    def partic(row):
        y = model.War4Partic()
        belligerent = belligerent_key(row['ccode'], row['state_name'])
        war_side = war_side_pkey(int(row['war_num']),
                                 int(row['side']))
        y.war_partic = war_partic_pkey(war_side, belligerent)
        y.war_side = war_side
        y.belligerent = belligerent
        for k, v in WHERE_FOUGHT[_int(row['where_fought'])].iteritems():
            setattr(y, k, v)
        y.outcome = row['outcome']
        y.bat_death = _int(row['bat_death'])
        y.initiator = (int(row['initiator']) == 1)
        return y

    def add_partic_dates(row, n):
        if row['start_year%d' % n] != '-8':
            y = model.War4ParticDate()
            war_side = war_side_pkey(int(row['war_num']),
                                     int(row['side']))
            belligerent = belligerent_key(row['ccode'], row['state_name'])
            y.war_partic = war_partic_pkey(war_side, belligerent)
            y.partic_num = n
            start_date = utils.daterng(_int(row['start_year%d' % n]),
                                       _int(row['start_month%d' % n]),
                                       _int(row['start_day%d' % n]))
            y.start_date_min, y.start_date_max = start_date
            if row['end_year%d' % n] == "-7":
                y.end_date_min = y.end_date_max = model.War4.ONGOING_DATE
                y.ongoing = True
            else:
                end_date = utils.daterng(_int(row['end_year%d' % n]),
                                         _int(row['end_month%d' % n]),
                                         _int(row['end_day%d' % n]))
                y.end_date_min, y.end_date_max = end_date
                y.ongoing = False
            session.add(y)
        
    cols = ("war_num", "war_name", "war_type")
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
            for side in (1, 2):
                session.add(model.War4Side(war_side = war_side_pkey(side=side, war_num=war_num),
                                           side=side, war_num=war_num))
            session.flush()
        if cnt_bellig[belligerent] == 1:
            session.add(model.War4Belligerent(belligerent = belligerent,
                                              belligerent_name = row['state_name'],
                                              ccode = row['ccode']))
            session.flush()
        session.add(partic(row))
        for i in (1, 2):
            add_partic_dates(row, i)
    session.commit()

def load_war4_intra(src):
    """ Add Intra-state war data to war4_* tables

    updates tables cow_war4, cow_belligerents, cow_war4_participation, cow_war4_partic_dates
    """
    session = model.SESSION()

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
        war_side = war_side_pkey(_int(row['war_num']),
                                 (side == 'b') + 1)
        y.war_partic = war_partic_pkey(war_side, belligerent)
        y.belligerent = belligerent
        y.war_side = war_side
        for k, v in WHERE_FOUGHT[_int(row['where_fought'])].iteritems():
            setattr(y, k, v)
        ## outcomes given in Side A / Side B rather than winner/loser
        ## per participant
        outcome = _int(row['outcome'])
        if side == 2:
            if outcome == 2: outcome = 1
            elif outcome == 1: outcome = 2
        y.outcome = outcome
        y.bat_death = _int(row['side_%sdeaths' % side])
        y.initiator = (row['initiator'] == y.belligerent)
        return y

    def add_partic_dates(row, belligerent, side, n):
        if row['start_year%d' % n] != '-8':
            y = model.War4ParticDate()
            war_side = war_side_pkey(_int(row['war_num']),
                                     (side == 'b') + 1)
            y.war_partic = war_partic_pkey(war_side,
                                           belligerent)
            y.belligerent = belligerent
            y.war_side = war_side
            y.partic_num = n
            start_date = utils.daterng(_int(row['start_year%d' % n]),
                                       _int(row['start_month%d' % n]),
                                       _int(row['start_day%d' % n]))
            y.start_date_min, y.start_date_max = start_date
            if row['end_year%d' % n] == "-7":
                y.end_date_min = y.end_date_max = model.War4.ONGOING_DATE
                y.ongoing = True
            else:
                end_date = utils.daterng(_int(row['end_year%d' % n]),
                                         _int(row['end_month%d' % n]),
                                         _int(row['end_day%d' % n]))
                y.end_date_min, y.end_date_max = end_date
                y.ongoing = False
            session.add(y)
    
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
            for side in (1, 2):
                session.add(model.War4Side(war_side = war_side_pkey(war_num, side),
                                           side=side, war_num=row['war_num']))
            session.flush()
        if _side(row['side_a']):
            add_belligerent(session, row['side_a'], row['ccode_a'])
            belligerent = belligerent_key(row['ccode_a'], row['side_a'])
            session.add(partic(row, belligerent, 'a'))
            for i in (1, 2):
                add_partic_dates(row, belligerent, 'a', i)
        if _side(row['side_b']):
            add_belligerent(session, row['side_b'], row['ccode_b'])
            belligerent = belligerent_key(row['ccode_b'], row['side_b'])
            session.add(partic(row, belligerent, 'b'))
            for i in (1, 2):
                add_partic_dates(row, belligerent, 'b', i)
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
        war_side = war_side_pkey(_int(row['war_num']), (side == "b") + 1)
        belligerent = belligerent_key(None, name)
        y.war_partic = war_partic_pkey(war_side, belligerent)
        y.war_side = war_side
        y.belligerent = belligerent
        for k, v in WHERE_FOUGHT[_int(row['where_fought'])].iteritems():
            setattr(y, k, v)
        outcome = _int(row['outcome'])
        if side:
            if outcome == 2: outcome = 1
            elif outcome == 1: outcome = 2
        y.outcome = outcome
        y.initiator = (row['initiator'] == side.upper())
        return y

    def add_partic_dates(row, name, side):
        y = model.War4ParticDate()
        war_side = war_side_pkey(_int(row['war_num']),
                                 (side == "b") + 1)
        belligerent = belligerent_key(None, name)
        y.war_partic = war_partic_pkey(war_side, belligerent)
        y.partic_num = 1
        start_date = utils.daterng(_int(row['start_year']),
                                   _int(row['start_month']),
                                   _int(row['start_day']))
        y.start_date_min, y.start_date_max = start_date
        if row['end_year'] == "-7":
            y.end_date_min = y.end_date_max = model.War4.ONGOING_DATE
            y.ongoing = True
        else:
            end_date = utils.daterng(_int(row['end_year']),
                                     _int(row['end_month']),
                                     _int(row['end_day']))
            y.end_date_min, y.end_date_max = end_date
            y.ongoing = False
        session.add(y)

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
            side_bool = (side == 'b') + 1
            session.add(model.War4Side(war_side = war_side_pkey(war_num, side_bool),
                                       side = side_bool,
                                       war_num = war_num,
                                       bat_death = _int(row['side_%sdeaths' % side])))
        session.flush()
        for i in (1, 2):
            name = row['side_a%d' % i]
            if name != '-8':
                add_belligerent(session, name)
                session.add(partic(row, 'a', name))
                add_partic_dates(row, name, 'a')
        for i in range(1, 6):
            name = row['side_b%d' % i]
            if name != '-8':
                add_belligerent(session, name)
                session.add(partic(row, 'b', name))
                add_partic_dates(row, name, 'b')
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
            war_num = int(row['war_num'])
            for x in clean(row['trans_from']):
                load_link(x, war_num)
            for x in clean(row['trans_to']):
                load_link(war_num, x)

    load_file(inter)
    load_file(intra)
    load_file(nonstate)
    session.commit()

def drop_all():
    for x in reversed(KLS):
        KLS.__table__.delete().execute()

def load_all(external):
    """ Load all COW War v. 4 data """
    model.Base.metadata.create_all(checkfirst=True)
    load_cow_war_types(utils.get_data("cow_war_types.yaml"))
    utils.load_enum_from_yaml(utils.get_data("war4_enum.yaml"))
    load_war4_list(utils.get_data("WarList_NEW.txt"))
    load_war4_inter(utils.get_data("InterStateWarData_v4.0.csv"))
    load_war4_intra(utils.get_data("IntraStateWarData_v4.1.csv"))
    load_war4_nonstate(utils.get_data("NonStateWarData_v4.0.csv"))
    load_war4_links(utils.get_data("InterStateWarData_v4.0.csv"),
                    utils.get_data("IntraStateWarData_v4.1.csv"),
                    utils.get_data("NonStateWarData_v4.0.csv"))
def main():
    drop_all()
    load_all()

if __name__ == '__main__':
    engine = sys.argv[1]
    model.Base.metadata.bind = sa.create_engine(engine)
    main()
    
