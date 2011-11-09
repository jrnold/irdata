import datetime

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext import declarative

Base = declarative.declarative_base()
SESSION = orm.sessionmaker()

class Mixin(object):
    pass

class FactorMixin():
    label = sa.Column(sa.Unicode)
    
class CharFactorMixin(FactorMixin):
    value = sa.Column(sa.Unicode, primary_key=True)

class IntFactorMixin(FactorMixin):
    value = sa.Column(sa.Integer, primary_key=True)

class CowState(Base, Mixin):
    """COW state numbers, abbrevations, and names (2008.1)

    """
    __tablename__ = 'cow_statelist'
    
    ccode = sa.Column(sa.Integer,
                      primary_key=True,
                      doc="COW state number")
    state_abb = sa.Column(sa.Unicode(3),
                         doc="COW state abbrevation")
    state_nme = sa.Column(sa.Unicode(25),
                         doc="COW state name")

class CowSysMembership(Base, Mixin):
    """COW system membership (2008.1)

    Date intervals in which COW states are part of the international
    system.
    
    """

    __tablename__ = "cow_sys_membership"

    ONGOING_DATE = datetime.date(2008, 6, 30)
    """ Last date in the dataset """

    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(CowState.__table__.c.ccode,
                                    initially = "DEFERRED",
                                    deferrable=True),
                      primary_key=True,
                      doc = "COW column number")
    interval = sa.Column(sa.Integer,
                         primary_key=True,
                         doc = "State interval number")
    st_date = sa.Column(sa.Date, nullable = False,
                       doc="International system membership start date")
    end_date = sa.Column(sa.Date, nullable = False,
                        doc="International system membership end date")

class CowMajor(Base, Mixin):
    """COW major power list
    """

    __tablename__ = "cow_majors"

    ONGOING_DATE = datetime.date(2008, 6, 30)
    """ Last date in the dataset """

    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(CowState.__table__.c.ccode),
                      primary_key=True)
    interval = sa.Column(sa.Integer,
                         primary_key=True,
                         doc = "nth time that this state was a great power.")
    st_date = sa.Column(sa.Date, nullable = False,
                       doc="Major power status start date")
    end_date = sa.Column(sa.Date,
                        nullable = False,
                        doc="Major power status end date")


class CowSystem(Base, Mixin):
    """ COW System (2008.1) """
    __tablename__ = "cow_system"

    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(CowState.__table__.c.ccode),
                      primary_key=True)
    year = sa.Column(sa.Integer, primary_key=True)


class KsgState(Base, Mixin):
    """ State in K.S. Gleditsch's statelist v. 4

    States in KSG but not 

    """ 
    __tablename__ = 'ksg_statelist'

    idnum = sa.Column(sa.Integer, primary_key=True)
    idabb = sa.Column(sa.String(3), nullable=False, index=True)
    country_name = sa.Column(sa.Unicode(50), nullable=False, index=True)
    microstate = sa.Column(sa.Boolean)


class KsgSysMembership(Base, Mixin):
    """ System membership in K.S. Gleditsch's statelist v. 4
    """ 
    __tablename__ = 'ksg_sys_membership'
    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(KsgState.__table__.c.idnum,
                                    deferrable = True,
                                    initially = "DEFERRED"),
                      primary_key=True)
    interval = sa.Column(sa.Integer, primary_key=True)
    start_date = sa.Column(sa.Date)
    end_date = sa.Column(sa.Date)


class KsgSystem(Base, Mixin):
    """ State system in K.S. Gleditsch's statelist v. 4
    """
    __tablename__ = 'ksg_system'
    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(KsgState.__table__.c.idnum),
                      primary_key=True)
    year = sa.Column(sa.Integer,
                     primary_key=True)
    

class Ksg2Cow(Base, Mixin):
    """ KSG statelist to COW statelist 

    see cowfilter.pl in http://privatewww.essex.ac.uk/~ksg/data/exptradegdpv4.1.zip

    Apart from disagreements in the dates in which countries were in the system,
    which can be handled by merging, the main differences are in the following countries:
    
    - Yemen post-1991
    - Germany post-1991
    """

    __tablename__ = 'ksg_to_cow'
    year = sa.Column(sa.Integer,
                     primary_key=True)
    ksg_ccode = sa.Column(sa.ForeignKey(KsgState.__table__.c.idnum),
                          primary_key=True)
    cow_ccode = sa.Column(sa.ForeignKey(CowState.__table__.c.ccode))

class NmcPecqualitycode(Base, Mixin, CharFactorMixin):
    """ NMC Primary Energy Consumption quality codes"""
    __tablename__ = 'nmc_pecqualitycode'

class NmcPecanomalycode(Base, Mixin, CharFactorMixin):
    """ NMC Primary Energy Consumption anomaly codes"""
    __tablename__ = 'nmc_pecanomalycode'

class NmcIrstqualitycode(Base, Mixin, CharFactorMixin):
    """ NMC Iron and Steel Production quality codes"""
    __tablename__ = 'nmc_irstqualitycode'

class NmcIrstanomalycode(Base, Mixin, CharFactorMixin):
    """ NMC Iron and Steel Production anomaly codes"""
    __tablename__ = 'nmc_irstanomalycode'

class NmcTpopqualitycode(Base, Mixin, CharFactorMixin):
    """ NMC Total Population quality codes"""
    __tablename__ = 'nmc_tpopqualitycode'

class NmcTpopanomalycode(Base, Mixin, CharFactorMixin):
    """ NMC Total Population anomaly codes"""
    __tablename__ = 'nmc_tpopanomalycode'

class NmcUpopqualitycode(Base, Mixin, CharFactorMixin):
    """ NMC Total Population quality codes"""    
    __tablename__ = 'nmc_upopqualitycode'

class Nmc(Base, Mixin):
    """ National Military Capabilities

    See

    """
    __tablename__ = 'nmc'
    VERSION = "4.0"
    ccode = sa.Column(sa.ForeignKey(CowState.__table__.c.ccode), primary_key=True)
    year = sa.Column(sa.Integer,
                     primary_key=True)
    ## IRST
    irst = sa.Column(sa.Float)
    irstsource = sa.Column(sa.Unicode)
    irstnote = sa.Column(sa.Unicode)
    irstqualitycode = sa.Column(sa.ForeignKey(NmcIrstqualitycode.__table__.c.value,
                                              deferrable=True))
    irstanomalycode = sa.Column(sa.ForeignKey(NmcIrstanomalycode.__table__.c.value,
                                              deferrable=True))
    ## Energy consumption
    pec = sa.Column(sa.Float)
    pecsource = sa.Column(sa.Unicode)
    pecnote = sa.Column(sa.Unicode)
    pecqualitycode = sa.Column(sa.ForeignKey(NmcPecqualitycode.__table__.c.value,
                                             deferrable=True))
    pecanomalycode = sa.Column(sa.ForeignKey(NmcPecanomalycode.__table__.c.value,
                                             deferrable=True))
    ## Military expenditure
    milex = sa.Column(sa.Float)
    milexsource = sa.Column(sa.Unicode)
    milexnote = sa.Column(sa.Unicode)
    ## Military personnel
    milper = sa.Column(sa.Float)
    milpersource = sa.Column(sa.Unicode)
    milpernote = sa.Column(sa.Unicode)
    ## urban population
    upop = sa.Column(sa.Float)
    upopsource = sa.Column(sa.Unicode)
    upopnote = sa.Column(sa.Unicode)
    upopqualitycode = sa.Column(sa.ForeignKey(NmcUpopqualitycode.__table__.c.value,
                                             deferrable=True))
    # upopanomalycode = sa.Column(sa.ForeignKey(NmcUpopqualitycode.__table__.c.value,
    #                                          deferrable=True))
    upopgrowth = sa.Column(sa.Float)
    upopgrowthsource = sa.Column(sa.Unicode)
    ## Total population
    tpop = sa.Column(sa.Float)
    tpopsource = sa.Column(sa.Unicode)
    tpopnote = sa.Column(sa.Unicode)
    tpopqualitycode = sa.Column(sa.ForeignKey(NmcTpopqualitycode.__table__.c.value,
                                              deferrable=True))
    tpopanomalycode = sa.Column(sa.ForeignKey(NmcTpopanomalycode.__table__.c.value,
                                              deferrable=True))
    cinc = sa.Column(sa.Float)


class PolityState(Base, Mixin):
    """ List of Poilty States

    Notes
    ------------
    
    The list of Polity states appears in 
    http://www.systemicpeace.org/inscr/p4manualv2009.pdf
    
    """
    __tablename__ = 'polity4_states'
    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(CowState.__table__.c.ccode),
                      primary_key=True)
    scode = sa.Column(sa.Unicode(3))
    country = sa.Column(sa.Unicode)


class PolitySysMembership(Base, Mixin):
    """ List of Poilty States and Spells of Independence

    Notes
    ------------

    Since states can have multiple spells of independence,
    e.g. Estonia, Latvia, Serbia, these data are in a separate
    table.
    
    """
    __tablename__ = 'polity4_sys_membership'

    ONGOING = 2010
    
    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(PolityState.__table__.c.ccode),
                      primary_key=True)
    interval = sa.Column(sa.Integer, primary_key=True)
    start_year = sa.Column(sa.Integer)
    end_year = sa.Column(sa.Integer)


class PolityStateYear(Base, Mixin):
    """ Polity state-years

    Source: http://www.systemicpeace.org/inscr/p4v2010.xls

    Documentation: http://www.systemicpeace.org/inscr/p4manualv2009.pdf

    """ 
    __tablename__ = 'polity_state_year'

    cyear = sa.Column(sa.Integer, primary_key=True)
    ccode = sa.Column(sa.Integer, 
                      sa.ForeignKey(PolityState.__table__.c.ccode),
                      nullable=False)
    year = sa.Column(sa.Integer)
    flag = sa.Column(sa.Integer, nullable=False)
    fragment = sa.Column(sa.Integer)
    democ = sa.Column(sa.Integer)
    autoc = sa.Column(sa.Integer)
    polity = sa.Column(sa.Integer)
    polity2 = sa.Column(sa.Integer)
    durable = sa.Column(sa.Integer)
    xrreg = sa.Column(sa.Integer)
    xrcomp = sa.Column(sa.Integer)
    xropen = sa.Column(sa.Integer)
    xconst = sa.Column(sa.Integer)
    parreg = sa.Column(sa.Integer)
    parcomp = sa.Column(sa.Integer)
    exrec = sa.Column(sa.Integer)
    exconst = sa.Column(sa.Integer)
    polcomp = sa.Column(sa.Integer)
    prior = sa.Column(sa.Integer)
    emonth = sa.Column(sa.Integer)
    eday = sa.Column(sa.Integer)
    eyear = sa.Column(sa.Integer)
    eprec = sa.Column(sa.Integer)
    interim = sa.Column(sa.Integer)
    bmonth = sa.Column(sa.Integer)
    bday = sa.Column(sa.Integer)
    byear = sa.Column(sa.Integer)
    bprec = sa.Column(sa.Integer)
    post = sa.Column(sa.Integer)
    change = sa.Column(sa.Integer)
    d4 = sa.Column(sa.Integer)
    sf = sa.Column(sa.Integer)
    regtrans = sa.Column(sa.Integer)


