""" irdata load """
import sqlalchemy as sa

from irdata import model
from irdata.load import ksg_states
from irdata.load import (version, cow_states, ksg_states, nmc, polity, war4, war3, contdir)

def download_files():
    # TODO: remove wget dependency
    pass

def main():
    DATA = "./data"
    EXTERNAL = "./external"
    ENGINE = "postgresql://jeff@localhost/irdata"
    kwargs = {}
    # reload database
    model.Base.metadata.bind = sa.create_engine(ENGINE, **kwargs)
    model.Base.metadata.drop_all(checkfirst=True)
    model.Base.metadata.create_all(checkfirst=True)
    ## Load data from cow system
    version.load_all()
    cow_states.load_all(EXTERNAL)
    ksg_states.load_all(EXTERNAL)
    nmc.load_all(DATA, EXTERNAL)
    polity.load_all(DATA, EXTERNAL)
    war4.load_all(DATA, EXTERNAL)
    war3.load_all(DATA, EXTERNAL)
    contdir.load_all(DATA, EXTERNAL)

if __name__ == '__main__':
    main()
