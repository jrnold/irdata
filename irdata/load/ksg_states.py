import collections
import datetime
import zipfile
import re

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
    """
    see cowfilter.pl in http://privatewww.essex.ac.uk/~ksg/data/exptradegdpv4.1.zip

    Apart from disagreements in the dates in which countries were in the system,
    which can be handled by merging, the main differences are in the following countries:
    
    - Yemen post-1991
    - Germany post-1991
    
    """
    session = model.SESSION()
    ## KSG start date
    ## 678	YEM	Yemen (Arab Republic of Yemen)	30:10:1918	01:11:2008
    ## COW
    ## YAR,678,Yemen Arab Republic,1926,9,2,1990,5,21,2008.1
    ## YEM,679,Yemen,1990,5,22,2008,6,30,2008.1
    for y in range(1991,COW_MAX_YEAR + 1):
        session.add(model.Ksg2Cow(year = y,
                            ksg_ccode = 678,
                            cow_ccode = 679))
    ## KSG treats Germany post-1991 as a continuation of West Germany
    ## COW treats it as a continuation of pre-WWII Germany
    for y in range(1991, COW_MAX_YEAR + 1):
        session.add(model.Ksg2Cow(year = y,
                            ksg_ccode = 260,
                            cow_ccode = 255))
    session.commit()
