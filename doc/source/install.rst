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

First, create the database if it doesn't exist.

:: 

  $ createdb irdata

Then run the script to load the data into the dataset

:: 

  $ python build_irdata.py postgresql://user@hostname/irdata


