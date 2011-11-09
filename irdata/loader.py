import collections
import datetime
import zipfile

import sqlalchemy as sa
import yaml

import csv2
from . import model
from . import utils


COW_MAX_YEAR = 2008
""" Correlates of War maximum year in the data"""

def row_ymd(row, y, m, d):
    return datetime.date(*(int(row[x]) for x in (y, m, d)))

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

def load_nmc_codes(src):
    session = model.SESSION()
    for tbl, v in yaml.load(src).iteritems():
        data = []
        for value, label in v.iteritems():
            data.append({'value': unicode(value),
                        'label': unicode(label)})
        model.Base.metadata.tables[tbl].insert().execute(data)
    session.commit()


def load_nmc(src):
    def missing(x):
        return x if x != '-9' else None
    def _int(x):
        try:
            return int(x)
        except TypeError:
            return None
    def _float(x):
        try:
            return float(x)
        except TypeError:
            return None
    session = model.SESSION()
    # session = model.SESSION()
    reader = csv2.DictReader(src, encoding='latin-1')
    for i, row in enumerate(reader):
        del row['stateabb']
        del row['statenme']
        del row['upopanomalycode']
        del row['version']
        for k in ['ccode', 'irst', 'milex', 'milper', 'tpop', 'upop']:
                row[k] = _int(row[k])
        for k in ["pec", 'upopgrowth']:
            v = _float(row[k])
            if v < 0:
                v = None
            row[k]  = v
        session.add(model.Nmc(**row))
    session.commit()


def load_polity_states(src):
    POLITY_MAX_YEAR = model.PolitySysMembership.ONGOING
    session = model.SESSION()
    data = yaml.load(src)
    cnt = collections.Counter()
    for x in data:
        ccode = x['ccode']
        cnt[ccode] += 1
        if cnt[ccode] == 1:
            session.add(model.PolityState(**utils.subset(x, ('ccode', 'scode', 'country'))))
        x['end_year'] = x['end_year'] if x['end_year'] else POLITY_MAX_YEAR
        session.add(model.PolitySysMembership(interval = cnt[ccode],
                                        **utils.subset(x, ('ccode', ''))))
    session.commit()

def load_polity(src):
    session = model.SESSION()
    reader = csv2.DictReader(src)
    for row in reader:
        for k in ('scode', 'country'):
            del row[k]
        session.add(model.PolityStateYear(**row))
    session.commit()

def main():
    model.Base.metadata.bind = sa.create_engine("sqlite:///irdata.db")
    model.Base.metadata.drop_all(checkfirst=True)
    model.Base.metadata.create_all(checkfirst=True)
    ## Load data from cow system
    load_cow_states(open("external/www.correlatesofwar.org/COW2 Data/SystemMembership/2008/states2008.1.csv", 'rb'))
    load_cow_majors(open("external/www.correlatesofwar.org/COW2 Data/SystemMembership/2008/majors2008.1.csv", 'rb'))
    load_cow_system()
    load_ksg_states(open("external/privatewww.essex.ac.uk/~ksg/data/iisystem.dat", 'rb'),
                    open("external/privatewww.essex.ac.uk/~ksg/data/microstatessystem.dat", 'rb'))
    load_ksg_system()
    load_ksg2cow()
    load_nmc_codes(open("data/nmc_codes.yaml", 'r'))
    ## If not opened with rU then throws 
    load_nmc(zipfile.ZipFile('external/www.correlatesofwar.org/COW2 Data/Capabilities/NMC_Supplement_v4_0_csv.zip').open('NMC_Supplement_v4_0.csv', 'rU'))
    load_polity_states(open('data/polity4_states.yaml', 'r'))
    load_polity(open('data/p4v2010.csv', 'r'))
    
    
if __name__ == '__main__':
    main()
