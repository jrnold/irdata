from irdata import model

VERSION = "6.0.0"

def load_all():
    model.Version.__table__.insert().execute(version = VERSION)
