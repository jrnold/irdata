""" Load KSG state system data """
import collections
import datetime
import zipfile
import re
from os import path

import sqlalchemy as sa
import yaml

from irdata import csv2
from irdata import model
from irdata import utils

def _iisystem_dates(x):
    """ Parse iisystem dates

    >>> _iisystem_dates("18:11:2008")
    datetime.date(2008, 11, 18)
    """
    d, m, y = [int(y) for y in x.split(':')]
    return datetime.date(y, m, d)


def _load_ksg_states(src, microstate):
    """ Create ksg_states """
    session = model.SESSION()
    HEADER = ['idnum', 'idabb', 'country_name', 'start_date', 'end_date']
    rowgen = csv2.DictReader(src, delimiter='\t',
                             fieldnames = HEADER, encoding='latin-1')
    cnt = collections.Counter()
    for row in rowgen:
        idnum = row["idnum"]
        cnt[idnum] += 1
        if cnt[idnum] == 1:
            session.add(model.KsgState(idnum = idnum,
                                       idabb = row["idabb"],
                                       country_name = row["country_name"],
                                       microstate = microstate))
        interval = cnt[idnum]
        start_date = _iisystem_dates(row['start_date'])
        end_date = _iisystem_dates(row['end_date'])
        session.add(model.KsgSysMembership(ccode = idnum,
                                           start_date = start_date,
                                           end_date = end_date,
                                           interval = interval))
    session.commit()

def load_ksg_states(src1, src2):
    for x in ((src1, False), (src2, True)):
        _load_ksg_states(*x)

def load_ksg_system():
    """ Create cow_system table """ 
    session = model.SESSION()
    for st in session.query(model.KsgSysMembership):
        for yr in range(st.start_date.year, st.end_date.year + 1):
            session.add(model.KsgSystem(ccode = st.ccode,
                                        year = yr))
        session.flush()
    session.commit()

def load_ksg2cow():
    """ Load data into ksg_to_cow
    
    see cowfilter.pl in http://privatewww.essex.ac.uk/~ksg/data/exptradegdpv4.1.zip

    Apart from disagreements in the dates in which countries were in the system,
    which can be handled by merging, the main differences are in the following countries:
    
    - Yemen post-1990

      - KSG considers Yemen a continuation of North Yemen
      - COW replaces both 678, and 680 with ccode 679 on 1990-5-22
    
    - Germany post-1991

      - COW switches from ccode 260 to 255 on 1990-10-30
      - KSG considers modern Germany a continuation of the German Federal Republic.
      
    
    """
    session = model.SESSION()
    q = session.query(model.CowSysMembership, model.KsgSysMembership).\
        filter(model.CowSysMembership.ccode == model.KsgSysMembership.ccode).\
        filter(model.CowSysMembership.st_date <= model.KsgSysMembership.end_date).\
        filter(model.CowSysMembership.end_date >= model.KsgSysMembership.st_date)
    for cow, ksg in q:
        start_date = max(cow.st_date, ksg.start_date)
        end_date = min(cow.end_date, ksg.end_date)
        session.add(KsgToCow(cow_ccode = cow.ccode,
                             ksg_ccode = ksg.ccode,
                             start_date = start_date,
                             end_date = end_date))
        ## Get parts not in the data
        if cow.st_date < ksg.start_date:
            session.add(KsgToCow(cow_ccode = cow.ccode,
                                 ksg_ccode = None,
                                 start_date = cow.st_date,
                                 end_date = ksg.st_date - datetime.timedelta(days=1)))
        elif cow.st_date > ksg.start_date:
            session.add(KsgToCow(cow_ccode = None,
                                 ksg_ccode = ksg.ccode,
                                 start_date = ksg.st_date,
                                 end_date = cow.st_date - datetime.timedelta(days=1)))
        if cow.end_date < ksg.end_date:
            session.add(KsgToCow(cow_ccode = None,
                                 ksg_ccode = ksg.ccode,
                                 start_date = cow.end_date + datetime.timedelta(days=1)
                                 end_date = ksg.end_date))
        elif cow.end_date > ksg.end_date:
            session.add(KsgToCow(cow_ccode = cow.ccode
                                 ksg_ccode = None,
                                 start_date = ksg.end_date + datetime.timedelta(days=1)
                                 end_date = cow.end_date))
        session.flush()

    new_data = [{start_date : datetime.Date(1990, 5, 21),
                end_date : datetime.Date(model.CowSysMembership.ONGOING_DATE),
                cow_ccode : 679,
                ksg_ccode : 678}, 
                {start_date : datetime.Date(1990, 5, 21),
                end_date : datetime.Date(model.CowSysMembership.ONGOING_DATE),
                cow_ccode : 255,
                ksg_ccode : 260}]
    for row in new_data:
                
    ## KSG start date
    ## 678	YEM	Yemen (Arab Republic of Yemen)	30:10:1918	01:11:2008
    ## COW
    ## YAR,678,Yemen Arab Republic,1926,9,2,1990,5,21,2008.1
    ## YEM,679,Yemen,1990,5,22,2008,6,30,2008.1
    # COW_MAX_YEAR = model.CowSysMembership.ONGOING_DATE.year
    # for y in range(1991,COW_MAX_YEAR + 1):
    #     session.add(model.Ksg2Cow(year = y,
    #                         ksg_ccode = 678,
    #                         cow_ccode = 679))
    ## KSG treats Germany post-1991 as a continuation of West Germany
    ## COW treats it as a continuation of pre-WWII Germany
    # for y in range(1991, COW_MAX_YEAR + 1):
    #     session.add(model.Ksg2Cow(year = y,
    #                         ksg_ccode = 260,
    #                         cow_ccode = 255))
    session.commit()

def load_all(external):
    """ Load all KSG data """
    load_ksg_states(open(path.join(external, "privatewww.essex.ac.uk/~ksg/data/iisystem.dat"),
                         'rb'),
                    open(path.join(external, "privatewww.essex.ac.uk/~ksg/data/microstatessystem.dat"),
                         'rb'))
    load_ksg_system()
    load_ksg2cow()
