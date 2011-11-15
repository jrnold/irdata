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
        for k in ["pec", 'upopgrowth', 'cinc']:
            v = _float(row[k])
            if v < 0:
                v = None
            row[k]  = v
        session.add(model.Nmc(**row))
    session.commit()

def load_all(data, external):
    """ Load all COW National Military Capabilities data """
    load_nmc_codes(open(path.join(data, "nmc_codes.yaml"), 'r'))
    ## If not opened with rU then throws
    nmc_zip = zipfile.ZipFile(path.join(external,
                                        "www.correlatesofwar.org/COW2 Data/Capabilities/NMC_Supplement_v4_0_csv.zip"))
    load_nmc(nmc_zip.open('NMC_Supplement_v4_0.csv', 'rU'))
