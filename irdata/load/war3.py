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

def load_war3(src):
    """ Load COW War Data v. 3 """

    session = model.SESSION()

    def _int(x):
        try:
            return int(x)
        except TypeError:
            return None

    def _dates(row, n):
        if row['yr_beg%d' % n]:
            y = model.War3Date()
            y.war_no = row['war_no']
            y.spell_no = n
            date_beg = utils.daterng(_int(row['yr_beg%d' % n]),
                                     _int(row['mon_beg%d' % n]),
                                     _int(row['day_beg%d' % n]))
            y.date_beg_min, y.date_beg_max = date_beg
            date_end = utils.daterng(_int(row['yr_end%d' % n]),
                                     _int(row['mon_end%d' % n]),
                                     _int(row['day_end%d' % n]))
            y.date_end_min, y.date_end_max = date_end
            session.add(y)

    reader = csv2.DictReader(src, encoding='latin1')
    reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]

    war_cols = [x.name for x in model.War3.__table__.c]
    war_date_cols = [x.name for x in model.War3Date.__table__.c]
    for row in reader:
        for k,v in row.iteritems():
            row[k] = utils.replmiss(v, lambda x: x in ("-999", "-888"))
        ## Inter-state war does not have a war_type
        if 'war_type' not in row.keys():
            row['war_type'] = 1
        row['oceania'] = row['oceania'] if row['oceania'] else False
        session.add(model.War3(**utils.subset(row, war_cols)))
        ## Dates
        for i in (1, 2):
            _dates(row, i)
    session.commit()

def load_war3_partic(src):
    """ Load COW War Data v. 3, Participants """
    session = model.SESSION()
    def _int(x):
        try:
            return int(x)
        except TypeError:
            return None

    def _dates(row, n):
        if row['yr_beg%d' % n]:
            y = model.War3ParticDate()
            y.war_no = row['war_no']
            y.state_num = row['state_num']
            y.partic_no = row['partic_no']
            y.spell_no = n
            date_beg = utils.daterng(_int(row['yr_beg%d' % n]),
                                     _int(row['mon_beg%d' % n]),
                                     _int(row['day_beg%d' % n]))
            y.date_beg_min, y.date_beg_max = date_beg
            date_end = utils.daterng(_int(row['yr_end%d' % n]),
                                     _int(row['mon_end%d' % n]),
                                     _int(row['day_end%d' % n]))
            y.date_end_min, y.date_end_max = date_end
            session.add(y)

    reader = csv2.DictReader(src, encoding='latin1')
    reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]
    war_cols = [x.name for x in model.War3Partic.__table__.c]
    war_date_cols = [x.name for x in model.War3ParticDate.__table__.c]
    cnt = collections.Counter()
    for row in reader:
        ## Account for multiple country-war participations
        key = (row['war_no'], row['state_num'])
        cnt[key] += 1
        row['partic_no'] = cnt[key]
        ## replace missing values
        for k,v in row.iteritems():
            row[k] = utils.replmiss(v, lambda x: x in ("-999", "-888"))
        session.add(model.War3Partic(**utils.subset(row, war_cols)))
        ## Dates
        for i in (1, 2):
             _dates(row, i)
    session.commit()

def load_all(data, external):
    """ Load all COW War Data v. 3 (Inter-, Intra-, and Extra-State)"""
    utils.load_enum_from_yaml(open(path.join(data, "war3_enum.yaml"), 'r'))
    load_war3(open(path.join(external, "www.correlatesofwar.org/cow2 data/WarData/InterState/Inter-State Wars (V 3-0).csv"), 'r'))
    load_war3_partic(open(path.join(external, "www.correlatesofwar.org/cow2 data/WarData/InterState/Inter-State War Participants (V 3-0).csv"), 'r'))
    load_war3(open(path.join(external, "www.correlatesofwar.org/cow2 data/WarData/IntraState/Intra-State Wars (V 3-0).csv"), 'r'))
    load_war3_partic(open(path.join(external, "www.correlatesofwar.org/cow2 data/WarData/IntraState/Intra-State War Participants (V 3-0).csv"), 'r'))
    load_war3(open(path.join(external, "www.correlatesofwar.org/cow2 data/WarData/ExtraState/Extra-State Wars (V 3-0).csv"), 'r'))
    load_war3_partic(open(path.join(external, "www.correlatesofwar.org/cow2 data/WarData/ExtraState/Extra-State War Participants (V 3-0).csv"), 'r'))

    
