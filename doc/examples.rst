Examples
###########

Some example queries

National Military Capabilities using KSG States
=================================================

NMC data using the KSG international system country codes.

.. code-block:: sql
  
   SELECT b.ksg_ccode as ccode, a.year, a.cinc 
   FROM nmc as a, ksg_to_cow_year as b 
   WHERE b.end_year and a.ccode = b.cow_ccode;

Countries in which non-internationalized civil wars occurred 
============================================================

Find the ccode of the country in which non-internationalized
intra-state wars occurred.

.. code-block:: sql

    SELECT a.war_num, c.ccode as num 
    FROM war4 as a, war4_partic as b, war4_belligerents as c 
    WHERE a.war_type in (4, 5, 6) 
    and not intnl
    and a.war_num = b.war_num 
    and b.belligerent = c.belligerent 
    and c.ccode is not null 
    GROUP BY a.war_num, c.ccode ;
