# -*- encoding: utf-8 -*- 
""" irdata Database model """ 
import datetime

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy import types
from sqlalchemy.ext import declarative

Base = declarative.declarative_base()
SESSION = orm.sessionmaker()

COW_ONGOING_DATE = datetime.date(2008, 6, 30)
""" COW maximal date """

class IntegerConstrained(sa.Integer, types.SchemaType):
    """Integer that can only take on constrained values

    An integer column with a check constraint on valid values.
    It is like an integer version of the Enum type.
    
    """
    def __init__(self, name=None, *values):
        """Construct a day

        :param name: if a CHECK constraint is generated, specify
          the name of the constraint.

        """
        self.values = values
        self.name = name

    def _set_table(self, column, table):
        e = sa.schema.CheckConstraint(
                        column.in_(self.values),
                        name=self.name)
        table.append_constraint(e)

        
class Day(IntegerConstrained, types.SchemaType):
    """Day of the month column type

    An integer column with a check constraint that the
    values are in 1-31.
    
    """
    values = range(1, 32)
    
    def __init__(self, name=None):
        self.name = name


class Month(IntegerConstrained, types.SchemaType):
    """ Month column type

    An integer column with a check constraint that the
    values are in 1-12.
    """
    values = range(1, 13)
    
    def __init__(self, name=None):
        self.name = name


class Mixin(object):
    """ Project mixin class

    All objects mapping to tables in this database inherit
    from this class. 

    """
    @classmethod
    def columns(kls):
        """ names of columns in the table mapped to the class """ 
        return [x.name for x in kls.__table__.c]


class FactorMixin(object):
    """ Factor (Categorical) data table
    """
    label = sa.Column(sa.Unicode)
    
class CharFactorMixin(FactorMixin):
    """ Factor (Categorical) data table with character values """
    value = sa.Column(sa.Unicode, primary_key=True)


class IntFactorMixin(FactorMixin):
    """ Factor (Categorical) data table with integer values """
    value = sa.Column(sa.Integer, primary_key=True)


class Version(Base, Mixin):
    """ Version number """
    __tablename__ = 'version'
    version = sa.Column(sa.Unicode, primary_key=True)


class CowState(Base, Mixin):
    """COW state numbers, abbrevations, and names
    """ 

    __tablename__ = 'cow_statelist'
    
    ccode = sa.Column(sa.Integer,
                      primary_key=True)
    state_abb = sa.Column(sa.Unicode(3))
    state_nme = sa.Column(sa.Unicode)

class CowWarType(Base, Mixin):
    """ COW War Typology
    """
    __tablename__ = "cow_war_types"
    value = sa.Column(sa.Integer, primary_key=True)
    label = sa.Column(sa.Unicode)
    category = sa.Column(sa.Enum("Inter-State War", "Extra-State War",
                                 "Intra-State War", "Non-State War",
                                 name = "cow_war_categories"))
    

class CowSysMembership(Base, Mixin):
    """COW system membership

    Entry and exit dates of states into and out of the international system.

    From 

      Correlates of War Project. 2008. “State System Membership List, v2008.1.” Online, http://correlatesofwar.org.
    
    """
    __tablename__ = "cow_sys_membership"

    ONGOING_DATE = COW_ONGOING_DATE
    """ Last day in this dataset """

    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(CowState.__table__.c.ccode,
                                    initially = "DEFERRED",
                                    deferrable=True),
                      primary_key=True)
    interval = sa.Column(sa.Integer,
                         primary_key=True)
    st_date = sa.Column(sa.Date, nullable = False)
    end_date = sa.Column(sa.Date, nullable = False)


class CowMajor(Base, Mixin):
    """COW Major Power list

    Entry and exit dates for states to be designated major powers.

    From
    
          Correlates of War Project. 2008. “State System Membership List, v2008.1.” Online, http://correlatesofwar.org.
    
    """

    __tablename__ = "cow_majors"

    ONGOING_DATE = COW_ONGOING_DATE
    """ Last date in the dataset """

    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(CowState.__table__.c.ccode),
                      primary_key=True)
    interval = sa.Column(sa.Integer,
                         primary_key=True)
    st_date = sa.Column(sa.Date, nullable = False)
    end_date = sa.Column(sa.Date,
                        nullable = False)


class CowSystem(Base, Mixin):
    """ COW System (2008.1) """
    __tablename__ = "cow_system"

    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(CowState.__table__.c.ccode),
                      primary_key=True)
    year = sa.Column(sa.Integer, primary_key=True)
    start_year = sa.Column(sa.Boolean)
    end_year = sa.Column(sa.Boolean)
    mid_year = sa.Column(sa.Boolean)
    frac_year = sa.Column(sa.Float)


class KsgState(Base, Mixin):
    __tablename__ = 'ksg_statelist'

    idnum = sa.Column(sa.Integer, primary_key=True)
    idabb = sa.Column(sa.String(3), nullable=False, index=True)
    country_name = sa.Column(sa.Unicode(50), nullable=False, index=True)
    microstate = sa.Column(sa.Boolean)


class KsgSysMembership(Base, Mixin):
    __tablename__ = 'ksg_sys_membership'
    ONGOING_DATE = datetime.date(2008, 11, 1)
    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(KsgState.__table__.c.idnum,
                                    deferrable = True,
                                    initially = "DEFERRED"),
                      primary_key=True)
    interval = sa.Column(sa.Integer, primary_key=True)
    start_date = sa.Column(sa.Date)
    end_date = sa.Column(sa.Date)


class KsgSystem(Base, Mixin):
    __tablename__ = 'ksg_system'
    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(KsgState.__table__.c.idnum),
                      primary_key=True)
    year = sa.Column(sa.Integer,
                     primary_key=True)
    

class KsgToCow(Base, Mixin):
    """ KSG-COW date interval links

    see cowfilter.pl in http://privatewww.essex.ac.uk/~ksg/data/exptradegdpv4.1.zip

    Apart from disagreements in the dates at which countries were in the system,
    which can be handled by merging, the main differences are in the following countries:
    
    - Yemen post-1991
    - Germany post-1991
    
    """

    __tablename__ = 'ksg_to_cow'

    rowid = sa.Column(sa.Integer, primary_key=True)
    ksg_ccode = sa.Column(sa.Integer,
                          sa.ForeignKey(KsgState.__table__.c.idnum))
    cow_ccode = sa.Column(sa.Integer,
                          sa.ForeignKey(CowState.__table__.c.ccode))
    start_date  = sa.Column(sa.Date)
    end_date  = sa.Column(sa.Date)

class KsgToCowYear(Base, Mixin):
    """ KSG-COW state-year links

    Derived from the ksg_to_cow table
    
    """

    __tablename__ = 'ksg_to_cow_year'

    rowid = sa.Column(sa.Integer, primary_key=True)
    ksg_ccode = sa.Column(sa.Integer,
                          sa.ForeignKey(KsgState.__table__.c.idnum))
    cow_ccode = sa.Column(sa.Integer,
                          sa.ForeignKey(CowState.__table__.c.ccode))
    year = sa.Column(sa.Integer)
    start_year = sa.Column(sa.Boolean)
    end_year = sa.Column(sa.Boolean)
    mid_year = sa.Column(sa.Boolean)
    frac_year = sa.Column(sa.Float)


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
    irstqualitycode = sa.Column(sa.Unicode(1),
                                sa.ForeignKey(NmcIrstqualitycode.__table__.c.value,
                                              deferrable=True))
    irstanomalycode = sa.Column(sa.Unicode(1),
                                sa.ForeignKey(NmcIrstanomalycode.__table__.c.value,
                                              deferrable=True))
    ## Energy consumption
    pec = sa.Column(sa.Float)
    pecsource = sa.Column(sa.Unicode)
    pecnote = sa.Column(sa.Unicode)
    pecqualitycode = sa.Column(sa.Unicode(1),
                               sa.ForeignKey(NmcPecqualitycode.__table__.c.value,
                                             deferrable=True))
    pecanomalycode = sa.Column(sa.Unicode(1),
                               sa.ForeignKey(NmcPecanomalycode.__table__.c.value,
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
    upopqualitycode = sa.Column(sa.Unicode(1),
                                sa.ForeignKey(NmcUpopqualitycode.__table__.c.value,
                                              deferrable=True))
    # upopanomalycode = sa.Column(sa.ForeignKey(NmcUpopqualitycode.__table__.c.value,
    #                                          deferrable=True))
    upopgrowth = sa.Column(sa.Float)
    upopgrowthsource = sa.Column(sa.Unicode)
    ## Total population
    tpop = sa.Column(sa.Float)
    tpopsource = sa.Column(sa.Unicode)
    tpopnote = sa.Column(sa.Unicode)
    tpopqualitycode = sa.Column(sa.Unicode(1),
                                sa.ForeignKey(NmcTpopqualitycode.__table__.c.value,
                                              deferrable=True))
    tpopanomalycode = sa.Column(sa.Unicode(1),
                                sa.ForeignKey(NmcTpopanomalycode.__table__.c.value,
                                              deferrable=True))
    cinc = sa.Column(sa.Float)


class PolityState(Base, Mixin):
    """ List of Poilty States

    The list of Polity states appears in 
    http://www.systemicpeace.org/inscr/p4manualv2009.pdf

    It mostly uses the same set of numerical identifiers as COW,
    there are a few differences between scode and the COW abbreviation,
    and some differences in start and stop dates of countries. 

    - After 1993 Ethiopia has a different identifier (529, ETI).
    
    
    """
    __tablename__ = 'polity4_states'
    ccode = sa.Column(sa.Integer,
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
                      sa.ForeignKey(PolityState.__table__.c.ccode, deferrable = True, initially = "DEFERRED"),
                      primary_key=True)
    interval = sa.Column(sa.Integer, primary_key=True)
    start_year = sa.Column(sa.Integer)
    end_year = sa.Column(sa.Integer)


class PolityStateYear(Base, Mixin):
    """ Polity state-years
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
    emonth = sa.Column(Month)
    eday = sa.Column(Day)
    eyear = sa.Column(sa.Integer)
    eprec = sa.Column(sa.Integer)
    interim = sa.Column(sa.Integer)
    bmonth = sa.Column(Month)
    bday = sa.Column(Day)
    byear = sa.Column(sa.Integer)
    bprec = sa.Column(sa.Integer)
    post = sa.Column(sa.Integer)
    change = sa.Column(sa.Integer)
    d4 = sa.Column(sa.Integer)
    sf = sa.Column(sa.Integer)
    regtrans = sa.Column(sa.Integer)

    @property
    def edate(self):
        if self.eyear and self.emonth and self.eday:
            return datetime.date(self.eyear, self.emonth, self.eday)

    @property
    def edate(self):
        if self.byear and self.bmonth and self.bday:
            return datetime.date(self.byear, self.bmonth, self.bday)


class PolityCase(Base, Mixin):
    """ Polity IV Polity-Case Format
    """ 
    __tablename__ = 'polity_case'

    ccode = sa.Column(sa.Integer, 
                      sa.ForeignKey(PolityState.__table__.c.ccode),
                      primary_key=True)
    bdate = sa.Column(sa.Date, primary_key=True)
    edate = sa.Column(sa.Date, nullable = True)
    present = sa.Column(sa.Boolean, nullable = False)
    persist = sa.Column(sa.Integer)
    democ = sa.Column(sa.Integer)
    autoc = sa.Column(sa.Integer)
    polity = sa.Column(sa.Integer)
    xrreg = sa.Column(sa.Integer)
    xrcomp = sa.Column(sa.Integer)
    xropen = sa.Column(sa.Integer)
    xconst = sa.Column(sa.Integer)
    parreg = sa.Column(sa.Integer)
    parcomp = sa.Column(sa.Integer)
    exrec = sa.Column(sa.Integer)
    exconst = sa.Column(sa.Integer)
    polcomp = sa.Column(sa.Integer)


class War4Outcome(Base, IntFactorMixin, Mixin):
    """ COW War Data v. 4 outcome values """
    __tablename__ = 'war4_outcomes'

class War4List(Base, Mixin):
    __tablename__ = 'war4_list'
    war_num = sa.Column(sa.Integer, primary_key=True)
    war_name = sa.Column(sa.Unicode, nullable = False)

class War4(Base, Mixin):
    ONGOING_DATE = datetime.date(2007, 12, 31)
    
    __tablename__ = 'war4'
    war_num = sa.Column(sa.Integer, primary_key=True)
    war_name = sa.Column(sa.Unicode,
                         nullable = False)
    war_type = sa.Column(sa.Integer,
                         sa.ForeignKey(CowWarType.__table__.c.value),
                         nullable = False)
    intnl = sa.Column(sa.Boolean, nullable=True)
    bat_deaths = sa.Column(sa.Integer, nullable=True)


class War4Link(Base, Mixin):
    """ Links between COW War v. 4 wars """
    __tablename__ = 'war4_links'
    war_from = sa.Column(sa.Integer, primary_key=True)
    war_to = sa.Column(sa.Integer, primary_key=True)


class War4Belligerent(Base, Mixin):
    """ COW War Data v. 4 Belligerents 
    """
    __tablename__ = 'war4_belligerents'
    belligerent = sa.Column(sa.Unicode, primary_key=True)
    belligerent_name = sa.Column(sa.Unicode)
    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(CowState.__table__.c.ccode))

class War4Side(Base, Mixin):
    """ Cow War v. 4 Sides
    """ 
    __tablename__ = 'war4_sides'
    war_num = sa.Column(sa.ForeignKey(War4.__table__.c.war_num,
                                      deferrable=True,
                                      initially="DEFERRED"),
                       primary_key=True)
    side = sa.Column(sa.Boolean, primary_key=True)
    bat_death = sa.Column(sa.Integer)
    

class War4Partic(Base, Mixin):
    """ Cow War v.4 Participation
    """
    __tablename__ = 'war4_partic'
    war_num = sa.Column(sa.Integer, primary_key=True)
    belligerent = sa.Column(sa.Unicode,
                            sa.ForeignKey(War4Belligerent.__table__.c.belligerent),
                            primary_key=True)
    side = sa.Column(sa.Boolean, primary_key=True)
    west_hem = sa.Column(sa.Boolean)
    europe = sa.Column(sa.Boolean,
                       nullable = False)
    africa = sa.Column(sa.Boolean)
    mid_east = sa.Column(sa.Boolean)
    asia = sa.Column(sa.Boolean)
    oceania = sa.Column(sa.Boolean)
    ## Countries on the same side can have different outcomes
    ## see Germany in war 108.
    outcome = sa.Column(sa.Integer,
                        sa.ForeignKey(War4Outcome.__table__.c.value),
                        nullable = False)
    bat_death = sa.Column(sa.Integer)
    ## Initiation is by participant not side
    initiator = sa.Column(sa.Boolean, nullable = False)
    sa.ForeignKey(['war_num', 'side'],
                  [War4Side.__table__.c.war_num,
                   War4Side.__table__.c.side],
                  initially="DEFERRED", deferrable=True)


class War4ParticDate(Base, Mixin):
    """ Date interval in which a belligerent participated in a war """
    __tablename__ = 'war4_partic_dates'
    
    war_num = sa.Column(sa.Integer,
                        primary_key=True)
    belligerent = sa.Column(sa.Unicode, primary_key=True)
    side = sa.Column(sa.Boolean, primary_key=True)
    partic_num = sa.Column(sa.Integer, primary_key=True)
    start_date_min = sa.Column(sa.Date)
    start_date_max = sa.Column(sa.Date)
    end_date_min = sa.Column(sa.Date)
    end_date_max = sa.Column(sa.Date)
    ongoing = sa.Column(sa.Boolean, nullable = False)
    sa.ForeignKeyConstraint(['war_num', 'ccode', 'side'],
                            [War4Partic.__table__.c.war_num,
                             War4Partic.__table__.c.belligerent,
                             War4Partic.__table__.c.side],
                            initially="DEFERRED", deferrable=True)

    @property
    def start_date(self):
        return (self.start_date_min + self.start_date_max) / 2

    @property
    def end_date(self):
        return (self.end_date_min + self.end_date_max) / 2


class War3Outcome(Base, IntFactorMixin, Mixin):
    """ War Outcomes for Participants in Inter-State Wars

    See http://www.correlatesofwar.org/cow2%20data/WarData/InterState/Inter-State%20War%20Format%20(V%203-0).htm
    
    """
    __tablename__ = 'war3_outcomes'


class War3SysStat(Base, IntFactorMixin, Mixin):
    """ COW War Data v. 3 SysStat codes

    System membership status of state

    See http://www.correlatesofwar.org/cow2%20data/WarData/InterState/Inter-State%20War%20Format%20(V%203-0).htm
    """
    __tablename__ = 'war3_sys_stat'


class War3Winner(Base, IntFactorMixin, Mixin):
    """ COW War Data v. 3 Intra- and Extra-State war winner values
    """
    __tablename__ = "war3_winner"


class War3IntSide(Base, IntFactorMixin, Mixin):
    """ Correlates of War Data v. 3 intside values
    """
    __tablename__ = 'war3_int_side'

    
class War3Edition(Base, IntFactorMixin, Mixin):
    """ Correlates of War Data v. 3 edition values
    """
    __tablename__ = 'war3_edition'


class War3(Base, Mixin):
    """ COW Inter-State Wars v 3.0 (Wars)
    """
    __tablename__ = 'war3'
    
    war_no = sa.Column(sa.Integer, primary_key=True)
    war_type = sa.Column(sa.Integer,
                         sa.ForeignKey(CowWarType.__table__.c.value),
                         nullable = False)
    war_name = sa.Column(sa.Unicode(50),
                         nullable = False)
    #duration = sa.Column(sa.Integer)
    deaths = sa.Column(sa.Integer)
    cen_sub_sy = sa.Column(sa.Boolean)
    sub_sys_ea = sa.Column(sa.Boolean)
    maj_pow_in = sa.Column(sa.Boolean)
    maj_pow_ea = sa.Column(sa.Boolean)
    west_hem = sa.Column(sa.Boolean)
    europe = sa.Column(sa.Boolean, nullable = False)
    africa = sa.Column(sa.Boolean)
    mid_east = sa.Column(sa.Boolean)
    asia = sa.Column(sa.Boolean)
    oceania = sa.Column(sa.Boolean)
    edition = sa.Column(sa.Integer,
                        sa.ForeignKey(War3Edition.__table__.c.value))
    winner = sa.Column(sa.Integer,
                       sa.ForeignKey(War3Winner.__table__.c.value))
    interven = sa.Column(sa.Boolean)
    st_deaths = sa.Column(sa.Integer)
    to_deaths = sa.Column(sa.Integer)
    non_state = sa.Column(sa.Unicode(100))
    # intra
    # majorin -> majpowin
    # censubin -> censubsy
    # insurgnt -> nonstate
    state_num = sa.Column(sa.Integer,
                         sa.ForeignKey(CowState.__table__.c.ccode))


class War3Date(Base, Mixin):
    """ COW Inter-State Wars v 3.0 (War dates)
    """
    __tablename__ = 'war3_dates'
    
    war_no = sa.Column(sa.Integer, 
                      sa.ForeignKey(War3.__table__.c.war_no,
                                    deferrable = True,
                                    initially = "DEFERRED"),
                      primary_key=True)
    spell_no = sa.Column(sa.Integer, primary_key=True)
    date_beg_min = sa.Column(sa.Date)
    date_beg_max = sa.Column(sa.Date)
    sa.CheckConstraint('date_end_max >= date_end_min')
    date_end_min = sa.Column(sa.Date)
    date_end_max = sa.Column(sa.Date)
    sa.CheckConstraint('date_end_max >= date_end_min')

    @property
    def date_beg(self):
        if self.yr_beg and self.mon_beg and self.day_beg:
            return datetime.date(self.yr_beg, self.mon_beg, self.day_beg)

    @property
    def date_end(self):
        if self.yr_end and self.mon_end and self.day_end:
            return datetime.date(self.yr_end, self.mon_end, self.day_end)


class War3Partic(Base, Mixin):
    """ COW Inter-State Wars v 3.0 (Participants)
    """
    __tablename__ = 'war3_partic'
    
    war_no = sa.Column(sa.Integer, sa.ForeignKey(War3.__table__.c.war_no),
                      primary_key=True)
    state_num = sa.Column(sa.Integer, sa.ForeignKey(CowState.__table__.c.ccode),
                      primary_key=True)
    partic_no = sa.Column(sa.Integer, primary_key=True)
    #duration = sa.Column(sa.Integer)
    deaths = sa.Column(sa.Integer)
    outcome = sa.Column(sa.Integer,
                        sa.ForeignKey(War3Outcome.__table__.c.value))
    initiate = sa.Column(sa.Boolean)
    sys_stat = sa.Column(sa.Integer,
                         sa.ForeignKey(War3SysStat.__table__.c.value))
    pr_war_pop = sa.Column(sa.Integer)
    pr_war_arm = sa.Column(sa.Integer)
    west_hem = sa.Column(sa.Boolean)
    europe = sa.Column(sa.Boolean)
    africa = sa.Column(sa.Boolean)
    mid_east = sa.Column(sa.Boolean)
    asia = sa.Column(sa.Boolean)
    oceania = sa.Column(sa.Boolean)
    int_side = sa.Column(sa.Integer,
                         sa.ForeignKey(War3IntSide.__table__.c.value))


class War3ParticDate(Base, Mixin):
    """ COW Wars v 3.0 (Participants dates of war involvement)
    """

    __tablename__ = 'war3_partic_dates'
    
    war_no = sa.Column(sa.Integer, primary_key=True)
    state_num = sa.Column(sa.Integer, primary_key=True)
    partic_no = sa.Column(sa.Integer,primary_key=True)
    spell_no = sa.Column(sa.Integer, primary_key=True)
    date_beg_min = sa.Column(sa.Date)
    date_beg_max = sa.Column(sa.Date)
    sa.CheckConstraint('date_end_max >= date_end_min')
    date_end_min = sa.Column(sa.Date)
    date_end_max = sa.Column(sa.Date)
    sa.CheckConstraint('date_end_max >= date_end_min')
    sa.ForeignKey(['war_no', 'state_num'],
                  [War3Partic.__table__.c.war_no,
                   War3Partic.__table__.c.state_num,
                   War3Partic.__table__.c.partic_no])



class ContType(Base, IntFactorMixin, Mixin):
    """COW contiguity categories"""
    __tablename__ = 'cont_type'
    

class ContDir(Base, Mixin):
    """ COW Direct Contiguity v. 3. 1
    """
    __tablename__ = 'contdir'
    VERSION = '3.1'
    ONGOING = datetime.date(2006, 12, 31)
    
    statelno = sa.Column(sa.Integer,
                         sa.ForeignKey(CowState.__table__.c.ccode),
                         primary_key=True)
    statehno = sa.Column(sa.Integer, 
                         sa.ForeignKey(CowState.__table__.c.ccode),
                         primary_key=True)
    start_date = sa.Column(sa.Date, primary_key=True)
    end_date = sa.Column(sa.Date)
    conttype = sa.Column(sa.Integer,
                         sa.ForeignKey(ContType.__table__.c.value))
    notes = sa.Column(sa.Unicode)
    #version = sa.Column(sa.Unicode)


class KsgP4dOrigin(Base, Mixin, IntFactorMixin):
    """ Observation Origin codes for table ksgp4duse """
    __tablename__ = 'ksgp4duse_origin'


class KsgP4Origin(Base, Mixin, IntFactorMixin):
    """ Observation Origin codes for table ksgp4use """
    __tablename__ = 'ksgp4use_origin'


class KsgP4duse(Base, Mixin):
    """ Polity 4 (2008) data modified for KSG statelist

    See http://privatewww.essex.ac.uk/~ksg/polity.html
    """ 
    __tablename__ = 'ksgp4duse'

    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(KsgState.__table__.c.idnum),
                      primary_key=True)
    startdate = sa.Column(sa.Date, primary_key=True)
    enddate = sa.Column(sa.Date, primary_key=True)
    xrreg = sa.Column(sa.Integer)
    xrcomp = sa.Column(sa.Integer)
    xropen = sa.Column(sa.Integer) 
    xconst = sa.Column(sa.Integer)
    parreg = sa.Column(sa.Integer)
    parcomp = sa.Column(sa.Integer)
    democracy = sa.Column(sa.Integer)
    autocracy = sa.Column(sa.Integer)
    polity = sa.Column(sa.Integer)
    origin = sa.Column(sa.Integer,
                       sa.ForeignKey(KsgP4dOrigin.__table__.c.value))


class KsgP4use(Base, Mixin):
    """ Polity 4 (2008) data modified for KSG statelist

    See http://privatewww.essex.ac.uk/~ksg/polity.html
    """ 
    __tablename__ = 'ksgp4use'

    ccode = sa.Column(sa.Integer,
                      sa.ForeignKey(KsgState.__table__.c.idnum),
                      primary_key=True)
    year = sa.Column(sa.Integer, primary_key=True)
    xrreg = sa.Column(sa.Integer)
    xrcomp = sa.Column(sa.Integer)
    xropen = sa.Column(sa.Integer) 
    xconst = sa.Column(sa.Integer)
    parreg = sa.Column(sa.Integer)
    parcomp = sa.Column(sa.Integer)
    democracy = sa.Column(sa.Integer)
    autocracy = sa.Column(sa.Integer)
    polity = sa.Column(sa.Integer)
    origin = sa.Column(sa.Integer,
                       sa.ForeignKey(KsgP4dOrigin.__table__.c.value))

