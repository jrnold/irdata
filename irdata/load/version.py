from irdata import model

KLS = model.Version

VERSION = "6.0.0"

def unload():
    model.Version.__table__.delete().execute()

def load_all(external):
    model.Version.__table__.insert().execute(version = VERSION)

