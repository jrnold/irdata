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
from irdata.load import utils

KLS = [model.KsgState, model.KsgSysMembership]

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

def unload():
    for x in reversed(KLS):
        x.__table__.delete().execute()

def load_all(external):
    """ Load all KSG data """
    load_ksg_states(open(path.join(external, "privatewww.essex.ac.uk/~ksg/data/iisystem.dat"),
                         'rb'),
                    open(path.join(external, "privatewww.essex.ac.uk/~ksg/data/microstatessystem.dat"),
                         'rb'))
    load_ksg_system()
