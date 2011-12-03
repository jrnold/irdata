""" Load modified Polity data of KSG """
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

def _strpftime(x):
    """ Strpftime that works before 1900"""
    d, m, y = x.split('/')
    return datetime.date(*([int(x) for x in (y, m, d)]))

def load_ksgp4duse(src):
    """ Load data for table ksgp4duse """
    session = model.SESSION()
    reader = csv2.DictReader(src, delimiter = ' ')
    reader.fieldnames = [x.lower() for x in reader.fieldnames]
    cols = [x.name for x in model.KsgP4duse.__table__.c]
    for row in reader:
        row['startdate'] = _strpftime(row['startdate'])
        row['enddate'] = _strpftime(row['enddate'])
        for k, v in row.iteritems():
            if v == '.':
                row[k] = None
        session.add(model.KsgP4duse(**utils.subset(row, cols)))
    session.commit()    

def load_ksgp4use(src):
    """ Load data for table ksgp4use """ 
    session = model.SESSION()
    reader = csv2.DictReader(src, delimiter = ' ')
    reader.fieldnames = [x.lower() for x in reader.fieldnames]
    cols = [x.name for x in model.KsgP4use.__table__.c]
    for row in reader:
        for k, v in row.iteritems():
            if v == '.':
                row[k] = None
        session.add(model.KsgP4use(**utils.subset(row, cols)))
    session.commit()


def load_all(external):
    utils.load_enum_from_yaml(utils.get_data("ksgp4_enum.yaml"))
    load_ksgp4duse(utils.get_data("ksgp4duse.asc"))
    load_ksgp4use(utils.get_data("ksgp4use.asc"))    
    
