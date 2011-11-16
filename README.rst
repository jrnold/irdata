=================================
International Relations Data
=================================

I got tired of the merging and cleaning of international relations data, so
put it all together in a relational database.

It is similar to `EUGene <http://eugenesoftware.org/>`, but uses an
relational database backend, and is much less complete.

The database currency 

- COW State System Membership 2008.1 http://www.correlatesofwar.org/
- COW Wars v 4.0 http://www.correlatesofwar.org/ (Inter-, and Intra-)
- COW Wars v 3.0 http://www.correlatesofwar.org/
- COW National Material Capabilities v 4.0 http://www.correlatesofwar.org/
- COW Direct Contiguity v 3.1 http://www.correlatesofwar.org/
- Polity IV Annual Time-Series http://www.systemicpeace.org/inscr/inscr.htm
- Kristian Skrede Gleditsh (KSG) `List of independent states <http://privatewww.essex.ac.uk/~ksg/statelist.html>`
- Kristian Skrede Gleditsh (KSG) `Modified Polity data <http://privatewww.essex.ac.uk/~ksg/polity.html>`

Install
===============

The code is generally database agnostic since it is written with
in sqlalchemy. I have tested it with sqlite and postgresql.

Sqlite
-----------------

To install irdata as a sqlite database at `path/to/database/irdata.db`.

:: 

  $ python build_irdata.py sqlite:///path/to/database/irdata.db


Postgresql
-----------------

To install irdata to the postgresql database **irdata** 

First create the database if it doesn't exist.

:: 

  $ createdb irdata

:: 

  $ python build_irdata.py postgresql://user@hostname/irdata


Dependencies
===================

Beyond the default python packages, the following packages are
required.

- `sqlalchemy <http://pypi.python.org/pypi/SQLAlchemy>`_
- `PyYAML <http://pypi.python.org/pypi/PyYAML/>`_
- `xlrd <http://pypi.python.org/pypi/xlrd>`_


Roadmap
=================

- documentation for all tables
- add all datasets currently in COW and EuGENE
- add a HTSQL frontend


