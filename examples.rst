Examples
###########


National Military Capabilities using KSG States
=================================================

NMC data using the KSG international system country codes.

.. code-block:: sql
  
   SELECT b.ksg_ccode as ccode, a.year, a.cinc 
   FROM nmc as a, ksg_to_cow_year as b 
   WHERE b.end_year and a.ccode = b.cow_ccode;
