""" Load all data into the irdata database  """
from os import path

import sqlalchemy as sa

from irdata import model
from irdata.load import ksg_states
from irdata.load import (version, cow_states, ksg_states, nmc, polity, war4, war3, contdir, ksg_polity, ksg_to_cow)

def download_files():
    # TODO: remove wget dependency
    pass

def main(config):
    """ Load ALL data into the database

    :param config: yaml configuration file. See the self-documented
    example included with the distribution.
    
    """
    DATA = path.join(path.dirname(__file__), '..', 'data')
    EXTERNAL = path.join(config['dir'], 'external')
    ENGINE = config['engine']
    kwargs = config['engine_kwargs']
    # reload database
    model.Base.metadata.bind = sa.create_engine(ENGINE, **kwargs)
    model.Base.metadata.drop_all(checkfirst=True)
    model.Base.metadata.create_all(checkfirst=True)
    ## Load data from cow system
    version.load_all()
    cow_states.load_all(EXTERNAL)
    ksg_states.load_all(EXTERNAL)
    ksg_to_cow.load_all()
    nmc.load_all(DATA, EXTERNAL)
    polity.load_all(DATA, EXTERNAL)
    war4.load_all(DATA, EXTERNAL)
    war3.load_all(DATA, EXTERNAL)
    contdir.load_all(DATA, EXTERNAL)
    ksg_polity.load_all(DATA, EXTERNAL)

if __name__ == '__main__':
    main()
