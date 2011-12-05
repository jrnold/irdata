""" Load Militarized Interstate dispute data """ 
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

KLS = [model.MidA, model.MidB, model.MidLinkMid, model.MidLinkWar,
       model.MidOutcome, model.MidSettle, model.MidFatality, model.MidHiAct,
       model.MidHostLev, model.MidRevType, model.MidI]

def _int(x):
    try:
        y = int(re.sub(',', '', x))
        return y if y > 0 else None
    except TypeError:
        return None


def load_mida(src):
    session = model.SESSION()
    reader = csv2.DictReader(src, encoding='latin1')
    reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]

    cols = [c.name for c in model.MidA.__table__.columns]
    int_cols = [c.name for c in model.MidA.__table__.columns
                if isinstance(c.type, sa.types.Integer)]
    for row in reader:
        start_date = utils.daterng(*(_int(row[k]) for k in
                                     ('st_year', 'st_mon', 'st_day')))
        row['st_date_min'], row['st_date_min'] = start_date
        end_date = utils.daterng(*(_int(row[k]) for k in
                                   ('end_year', 'end_mon', 'end_day')))
        row['end_date_min'], row['end_date_min'] = end_date
        ## set -9 to NULL
        for k in int_cols:
            row[k] = _int(row[k])
        session.add(model.MidA(**utils.subset(row, cols)))
    session.commit()

def load_mid_links(src):
    """ Load tables mid_link_mid and link_mid_war """
    session = model.SESSION()
    reader = csv2.DictReader(src, encoding='latin1')
    reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]
    for row in reader:
        disp_num = row['disp_num']
        for k in ('link%d' % i for i in range(1, 4)):
            link = row[k]
            if link == '0' or link is None:
                continue
            elif link[-1] == 'W':
                session.add(model.MidLinkWar(disp_num = disp_num,
                                             war_num = link[:-1]))
            else:
                session.add(model.MidLinkMid(disp_num_1 = disp_num,
                                             disp_num_2 = link))
    session.commit()

def load_midb(src):
    session = model.SESSION()
    reader = csv2.DictReader(src, encoding='latin1')
    reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]
    cols = [c.name for c in model.MidB.__table__.columns]
    int_cols = [c.name for c in model.MidB.__table__.columns
                if isinstance(c.type, sa.types.Integer)]
    cnt = collections.Counter()
    for row in reader:
        cnt[(row['disp_num'], row['ccode'])] += 1
        row['spell_num'] = cnt[(row['disp_num'], row['ccode'])]
        start_date = utils.daterng(*(_int(row[k]) for k in
                                     ('st_year', 'st_mon', 'st_day')))
        row['st_date_min'], row['st_date_min'] = start_date
        end_date = utils.daterng(*(_int(row[k]) for k in
                                   ('end_year', 'end_mon', 'end_day')))
        row['end_date_min'], row['end_date_min'] = end_date
        ## set -9 to NULL
        for k in int_cols:
            row[k] = _int(row[k])
        session.add(model.MidB(**utils.subset(row, cols)))
    session.commit()

def load_midi(src):
    session = model.SESSION()
    reader = csv2.DictReader(src, encoding='latin1')
    reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]
    cols = [c.name for c in model.MidI.__table__.columns]
    int_cols = [c.name for c in model.MidI.__table__.columns
                if isinstance(c.type, sa.types.Integer)]
    for row in reader:
        start_date = utils.daterng(*(_int(row[k]) for k in
                                     ('st_year', 'st_mon', 'st_day')))
        row['st_date_min'], row['st_date_min'] = start_date
        end_date = utils.daterng(*(_int(row[k]) for k in
                                   ('end_year', 'end_mon', 'end_day')))
        row['end_date_min'], row['end_date_min'] = end_date
        ## set -9 to NULL
        for k in int_cols:
            row[k] = _int(row[k])
        session.add(model.MidI(**utils.subset(row, cols)))
    session.commit()

def load_midip(src):
    session = model.SESSION()
    reader = csv2.DictReader(src, encoding='latin1')
    reader.fieldnames = [utils.camel2under(x) for x in reader.fieldnames]
    cols = [c.name for c in model.MidIP.__table__.columns]
    int_cols = [c.name for c in model.MidIP.__table__.columns
                if isinstance(c.type, sa.types.Integer)]
    for row in reader:
        start_date = utils.daterng(*(_int(row[k]) for k in
                                     ('st_year', 'st_mon', 'st_day')))
        row['st_date_min'], row['st_date_min'] = start_date
        end_date = utils.daterng(*(_int(row[k]) for k in
                                   ('end_year', 'end_mon', 'end_day')))
        row['end_date_min'], row['end_date_min'] = end_date
        ## set -9 to NULL
        for k in int_cols:
            row[k] = _int(row[k])
        session.add(model.MidIP(**utils.subset(row, cols)))
    session.commit()



def load_all(EXTERNAL):
    cow_path = "www.correlatesofwar.org/COW2 Data/MIDs"
    utils.load_enum_from_yaml(utils.get_data("mid.yaml"))
    load_mida(utils.get_data("MIDA_3.10.csv"))
    load_mid_links(utils.get_data("MIDA_3.10.csv"))                             
    load_midb(utils.get_data("MIDB_3.10.csv"))
    load_midi(open(path.join(EXTERNAL, cow_path, "MIDI_3.10.csv"), 'rU'))
    load_midip(open(path.join(EXTERNAL, cow_path, "MIDIP_3.10.csv"), 'rU'))                             
