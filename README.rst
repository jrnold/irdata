=================================
International Relations Data
=================================

I got tired of merging and alternating the IR data that I use, so I
put together this database.  It is similar to `EUGene
<http://eugenesoftware.org/>`, but uses an relational database
backend.  

It includes 

- COW State System Membership 2008.1 http://www.correlatesofwar.org/
- COW Wars v 4.0 http://www.correlatesofwar.org/
- COW Wars v 3.0 http://www.correlatesofwar.org/
- COW National Material Capabilities v 4.0 http://www.correlatesofwar.org/
- COW Direct Contiguity v 3.1 http://www.correlatesofwar.org/
- Polity IV Annual Time-Series http://www.systemicpeace.org/inscr/inscr.htm
- Kristian Skrede Gleditsh (KSG) `List of independent states <http://privatewww.essex.ac.uk/~ksg/statelist.html>`
- Kristian Skrede Gleditsh (KSG) `Modified Polity data <http://privatewww.essex.ac.uk/~ksg/polity.html>`

Install
===============

Download data::

  $ ./download.sh

Create database (currently using PostgreSQL)::

  $ python builddb.py

Dependencies
===================

Beyond the default python packages, the following packages are
required.

- sqlalchemy
- yaml

