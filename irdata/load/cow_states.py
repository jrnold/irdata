""" Loading COW Interstate System Data """
from os import path
import collections
import datetime
import zipfile
import re
import calendar

import sqlalchemy as sa
import yaml

from irdata import csv2
from irdata import model
from irdata.load import utils

def load_cow_states(src):
    """ Load data into cow_statelist and cow_system_membership """
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
        st_date = utils.row_ymd(row, 'st_year', 'st_month', 'st_day')
        end_date = utils.row_ymd(row, 'end_year', 'end_month', 'end_day')
        session.add(model.CowSysMembership(ccode = ccode,
                                           interval = cnt[ccode],
                                           st_date = st_date,
                                           end_date = end_date))
    session.commit()

def load_cow_majors(src):
    """ Load data into cow_majors """
    session = model.SESSION()
    reader = csv2.DictReader(src)
    reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]
    cnt = collections.Counter()
    for row in reader:
        ccode = row['ccode']
        cnt[row['ccode']] +=1
        st_date = utils.row_ymd(row, 'st_year', 'st_month', 'st_day')
        end_date = utils.row_ymd(row, 'end_year', 'end_month', 'end_day')
        session.add(model.CowMajor(ccode = ccode,
                                    interval = cnt[ccode],
                                    st_date = st_date,
                                    end_date = end_date))
    session.commit()

def load_cow_system():
    """ load data into cow_system """ 
    session = model.SESSION()
    for st in session.query(model.CowSysMembership):
        for yr in range(st.st_date.year, st.end_date.year + 1):
            eoy = datetime.date(yr, 12, 31)
            boy = datetime.date(yr, 1, 1)
            moy = datetime.date(yr, 7, 2)
            start_year = (st.st_date <= boy and st.end_date >= boy)
            mid_year = (st.st_date <= moy and st.end_date >= moy)
            end_year = (st.st_date <= eoy and st.end_date >= eoy)
            ndays = 366 if calendar.isleap(yr) else 365
            frac_year = (max(boy, st.start_date) -
                         min(eoy, st.end_date)).days / ndays
            session.add(model.CowSystem(ccode = st.ccode,
                                        year = yr))
        session.flush()
    session.commit()
    

def load_all(external):
    """ Load all COW System data """
    load_cow_states(open(path.join(external, "www.correlatesofwar.org/COW2 Data/SystemMembership/2008/states2008.1.csv"), 'rb'))
    load_cow_majors(open(path.join(external, "www.correlatesofwar.org/COW2 Data/SystemMembership/2008/majors2008.1.csv"), 'rb'))
    load_cow_system()
    

