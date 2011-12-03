""" Create tables linking COW to KSG """ 
import datetime
import calendar

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy import types
from sqlalchemy.ext import declarative

from irdata import model

ONGOING = model.CowSysMembership.ONGOING_DATE

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

    Differing COW and KSG codes (COW, KSG)

    - Nauru : 970, 971
    - Tonga : 955, 972
    - Tuvalu : 947, 973
    - Kiribati : 946, 970
    
    """
    session = model.SESSION()
    q = session.query(model.CowSysMembership, model.KsgSysMembership).\
        filter(model.CowSysMembership.ccode == model.KsgSysMembership.ccode).\
        filter(model.CowSysMembership.st_date <= model.KsgSysMembership.end_date).\
        filter(model.CowSysMembership.end_date >= model.KsgSysMembership.start_date)
    for cow, ksg in q:
        start_date = max(cow.st_date, ksg.start_date)
        end_date = min(cow.end_date, ksg.end_date)
        session.add(model.KsgToCow(cow_ccode = cow.ccode,
                             ksg_ccode = ksg.ccode,
                             start_date = start_date,
                             end_date = end_date))
        ## Get parts not in the data
        # if cow.st_date < ksg.start_date:
        #     session.add(model.KsgToCow(cow_ccode = cow.ccode,
        #                          ksg_ccode = None,
        #                          start_date = cow.st_date,
        #                          end_date = ksg.start_date - datetime.timedelta(days=1)))
        # elif cow.st_date > ksg.start_date:
        #     session.add(model.KsgToCow(cow_ccode = None,
        #                          ksg_ccode = ksg.ccode,
        #                          start_date = ksg.start_date,
        #                          end_date = cow.st_date - datetime.timedelta(days=1)))
        # if cow.end_date < ksg.end_date and cow.end_date != model.CowSysMembership.ONGOING_DATE:
        #     session.add(model.KsgToCow(cow_ccode = None,
        #                          ksg_ccode = ksg.ccode,
        #                          start_date = cow.end_date + datetime.timedelta(days=1),
        #                          end_date = min(ksg.end_date,
        #                                         model.CowSysMembership.ONGOING_DATE)))
        # elif cow.end_date > ksg.end_date:
        #     session.add(model.KsgToCow(cow_ccode = cow.ccode,
        #                          ksg_ccode = None,
        #                          start_date = ksg.end_date + datetime.timedelta(days=1),
        #                          end_date = cow.end_date))
    session.flush()

    ## Update Germany Post 1990
    # ger = session.query(model.KsgToCow).\
    #        filter(model.KsgToCow.ksg_ccode == 260).\
    #        filter(model.KsgToCow.start_date == 
    # ger.cow_ccode = 255
    #session.add(ger)
    session.add(model.KsgToCow(ksg_ccode = 260, cow_ccode = 255,
                               start_date = datetime.date(1990, 10, 3),
                               end_date = ONGOING))

    # Update Yemen Post-1990
    # yemen = session.query(model.KsgToCow).\
    #        filter(model.KsgToCow.ksg_ccode == 678).\
    #        filter(model.KsgToCow.start_date == datetime.date(1990, 5, 22)).one()
    # yemen.cow_ccode = 679
    # session.add(yemen)
    session.add(model.KsgToCow(ksg_ccode = 678, cow_ccode = 679,
                               start_date = datetime.date(1990, 5, 22),
                               end_date = ONGOING))
    session.flush()

    # Resolve Nauru, Tonga, Tuvalu, Kiribati
    for x in session.query(model.KsgToCow).\
            filter(model.KsgToCow.ksg_ccode.in_([970, 971, 972, 973])).all():
        session.delete(x)
    for x in session.query(model.KsgToCow).\
            filter(model.KsgToCow.cow_ccode.in_([970, 955, 947, 946])).all():
        session.delete(x)

    NEWDATA = [ # Newdata
        # Nauru 970, 971
        # {'cow_ccode': None,
        #  'ksg_ccode': 971,
        #  'start_date' : datetime.date(1968, 12, 31),
        #  'end_date' : datetime.date(1999, 9, 13)},
        {'cow_ccode': 970,
         'ksg_ccode': 971,
         'start_date' : datetime.date(1999, 9, 14),
         'end_date' : ONGOING},
        # Tonga : 955, 972
        # {'cow_ccode': None,
        #  'ksg_ccode': 972,
        #  'start_date' : datetime.date(1970, 6, 4),
        #  'end_date' : datetime.date(1999, 9, 13)},
        {'cow_ccode': 955,
         'ksg_ccode': 972,
         'start_date' : datetime.date(1999, 9, 14),
         'end_date' : ONGOING},
        # Tuvalu : 947, 973        
        # {'cow_ccode': None,
        #  'ksg_ccode': 973,
        #  'start_date' : datetime.date(1978, 10, 1),
        #  'end_date' : datetime.date(2000, 9, 4)},
        {'cow_ccode': 947,
         'ksg_ccode': 973,
         'start_date' : datetime.date(2000, 9, 5),
         'end_date' : ONGOING},
        # Kiribati : 946, 970
        # {'cow_ccode': None,
        #  'ksg_ccode': 970,
        #  'start_date' : datetime.date(1979, 7, 12),
        #  'end_date' : datetime.date(1999, 9, 13)},
        {'cow_ccode': 946,
         'ksg_ccode': 970,
         'start_date' : datetime.date(1999, 9, 14),
         'end_date' : ONGOING}]
    for x in NEWDATA:
        session.add(model.KsgToCow(**x))

    ## Any KSG without any matches
    # for ksg in session.query(model.KsgSysMembership):
    #     if ksg.start_date < ONGOING:
    #         q = session.query(model.KsgToCow).\
    #             filter(ksg.ccode == model.KsgToCow.ksg_ccode).\
    #             filter(sa.or_(ksg.end_date < model.KsgToCow.start_date,
    #                           ksg.start_date > model.KsgToCow.end_date))
    #         if q.count() == 0:
    #             session.add(model.KsgToCow(ksg_ccode = ksg.ccode,
    #                                        start_date = ksg.start_date,
    #                                        end_date = min(ksg.end_date, ONGOING)))
    # for cow in session.query(model.CowSysMembership):
    #     if cow.st_date < ONGOING:
    #         q = session.query(model.KsgToCow).\
    #             filter(cow.ccode == model.KsgToCow.cow_ccode).\
    #             filter(sa.or_(cow.end_date < model.KsgToCow.start_date,
    #                           cow.st_date > model.KsgToCow.end_date))
    #         if q.count() == 0:
    #             session.add(model.KsgToCow(cow_ccode = cow.ccode,
    #                                        start_date = cow.st_date,
    #                                        end_date = cow.end_date))
    session.commit()

def load_ksg2cowyear():
    """ Load data into ksg_to_cow_year

    all data derived from ksg_to_cow table
    """
    session = model.SESSION()
    for x in session.query(model.KsgToCow):
        start_date = x.start_date
        end_date = x.end_date
        yr = start_date.year
        while yr <= end_date.year:
            yrdays = 366 if calendar.isleap(yr) else 365
            start_year = start_date <= datetime.date(yr, 1, 1)
            end_year = end_date >= datetime.date(yr, 12, 31)
            mid_year = (end_date >= datetime.date(yr, 6, 30)
                        and start_date <= datetime.date(yr, 6, 30))
            frac_year = ((min(datetime.date(yr, 12, 31), end_date) - 
                          max(datetime.date(yr, 1, 1), start_date)).days + 1.0) / yrdays
            session.add(model.KsgToCowYear(cow_ccode = x.cow_ccode,
                                           ksg_ccode = x.ksg_ccode,
                                           year = yr,
                                           start_year = start_year,
                                           end_year = end_year,
                                           mid_year = mid_year,
                                           frac_year = frac_year))
            yr += 1
        session.flush()
    session.commit()

def load_all(external):
    print("loading ksg_to_cow")
    load_ksg2cow()
    print("loading ksg_to_cow_year")
    load_ksg2cowyear()

if __name__ == '__main__':
    model.SESSION.close_all()
    model.KsgToCow.__table__.drop(checkfirst=True)
    model.KsgToCow.__table__.create()
    model.KsgToCowYear.__table__.drop(checkfirst=True)
    model.KsgToCowYear.__table__.create()
    load_ksg2cow()
    load_ksg2cowyear()


