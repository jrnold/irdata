import collections
import datetime
import zipfile
import re

import sqlalchemy as sa
import yaml

from irdata import csv2
from irdata import model
from irdata import utils

def load_cow_states(src):
    """ Loads states2008.1.csv into cow_statelist and cow_system_membership tables """
    session = model.SESSION()
    reader = csv2.DictReader(src)
    reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]
    cnt = collections.Counter()
    for row in reader:
        ccode = row['ccode']
        cnt[row['ccode']] +=1
        if cnt[ccode] == 1:
            session.add(model.CowState(ccode = ccode,
                                       state_abb = row['state_abb'],
                                       state_nme = row['state_nme']))
        st_date = row_ymd(row, 'st_year', 'st_month', 'st_day')
        end_date = row_ymd(row, 'end_year', 'end_month', 'end_day')
        session.add(model.CowSysMembership(ccode = ccode,
                                           interval = cnt[ccode],
                                           st_date = st_date,
                                           end_date = end_date))
    session.commit()

def load_cow_majors(src):
    """ Loads majors2008.1.csv into cow_majors """
    session = model.SESSION()
    reader = csv2.DictReader(src)
    reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]
    cnt = collections.Counter()
    for row in reader:
        ccode = row['ccode']
        cnt[row['ccode']] +=1
        st_date = row_ymd(row, 'st_year', 'st_month', 'st_day')
        end_date = row_ymd(row, 'end_year', 'end_month', 'end_day')
        session.add(model.CowMajor(ccode = ccode,
                                    interval = cnt[ccode],
                                    st_date = st_date,
                                    end_date = end_date))
    session.commit()

def load_cow_system():
    """ Create cow_system table """ 
    session = model.SESSION()
    for st in session.query(model.CowSysMembership):
        for yr in range(st.st_date.year, st.end_date.year + 1):
            session.add(model.CowSystem(ccode = st.ccode,
                                        year = yr))
        session.flush()
    session.commit()
