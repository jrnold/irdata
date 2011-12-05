""" Load all data into the irdata database  """
from os import path
import argparse
import tempfile
import shutil
import sys

import sqlalchemy as sa

from irdata import model
from irdata import download
from irdata.load import (version, cow_states, ksg_states,
                         nmc, polity, war4, war3,
                         contdir, ksg_polity, ksg_to_cow,
                         mid)

def load_all(EXTERNAL):
    """ Load data into the database """
    ## Load data from cow system
    model.Base.metadata.drop_all(checkfirst=True)
    model.Base.metadata.create_all(checkfirst=True)
    version.load_all(EXTERNAL)
    cow_states.load_all(EXTERNAL)
    ksg_states.load_all(EXTERNAL)
    ksg_to_cow.load_all(EXTERNAL)
    nmc.load_all(EXTERNAL)
    polity.load_all(EXTERNAL)
    war4.load_all(EXTERNAL)
    war3.load_all(EXTERNAL)
    contdir.load_all(EXTERNAL)
    ksg_polity.load_all(EXTERNAL)

def load_one(loader, EXTERNAL):
    foo = sys.modules['irdata.load.%s' % loader]
    ## make sure everything exists
    model.Base.metadata.create_all(checkfirst=True)
    ## Unload observations
    for kls in reversed(foo.KLS):
        kls.__table__.delete().execute()
    ## Load data
    foo.load_all(EXTERNAL)

def main():
    """ Load ALL data into the database

    :param config: yaml configuration file. See the self-documented
    example included with the distribution.
    
    """
    parser = argparse.ArgumentParser(description='Create the irdata database .')
    parser.add_argument('-D', '--dst', metavar='dest', dest="dest",
                        default=None, required=False,
                        type=str, help='directory in which to download data sources.')
    parser.add_argument('-L', '--loader', metavar="LOADER", default=None,
                        dest='loader',
                        type=str, help='load')
    parser.add_argument('engine', metavar="ENGINE", default=None, 
                        type=str, help='database engine')

    opts = parser.parse_args()
    if opts.dest:
        EXTERNAL = opts.dest
        tempdir = False
    else:
        EXTERNAL = tempfile.mkdtemp()
        tempdir = True
    kwargs = {}

    try:
        #download.download_all(EXTERNAL)
        # reload database
        model.Base.metadata.bind = sa.create_engine(opts.engine, **kwargs)
        print("Loading data into %s" % opts.engine)
        if opts.loader:
            load_one(opts.loader, EXTERNAL)
        else:
            load_all(EXTERNAL)
    except Exception:
        raise
    finally:
        # cleanup temporary directory-+
        if tempdir:
            shutil.rmtree(EXTERNAL)

if __name__ == '__main__':
    main()
