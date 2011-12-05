""" Check consistency of metadata files with database metadata """
import sys
import pkgutil
import os
import glob
from os import path

import yaml

import irdata
from irdata import model

def main():
    """ Check irdata metadata

    This checks whether 

    - all metadata files correspond to a database tables
    - all columns in the metadata correspond to columns in the database table

    """
    db_tables = model.Base.metadata.tables.iteritems()
    db_tablenames = [k for k,v in model.Base.metadata.tables.iteritems()]

    ## Check that all tables have files
    for tablename, table in db_tables:
        metadata = "data/metadata/%s.yaml" % tablename
        #print("loading %s" % metadata)
        try:
            src = pkgutil.get_data("irdata", metadata)
        except IOError:
            print("WARNING: data/metadata/%s.yaml missing" % tablename)
            continue

        try:
            data = yaml.load(src)
        except yaml.parser.ParserError as e:
            print("WARNING: %s did not parse" % metadata)
            print(e)
            continue

        colnames = [c.name for c in table.columns]
        for col in colnames:
            if col not in data['columns']:
                print("WARNING: %s, column %s missing" % (metadata, col))
        for col in data['columns']:
            if col not in colnames:
                print("WARNING: %s, column %s does not exist" % (metadata, col))

    d = path.dirname(sys.modules['irdata'].__file__)
    meta_files = [path.splitext(path.basename(x))[0] for x in
                  glob.glob('%s/*.yaml' % path.join(d, 'data', 'metadata'))]

    ## Check for files without a table
    for tblname in meta_files:
        if tblname not in db_tablenames:
            print("WARNING: %s.yaml exists but no table" % tblname)

if __name__ == '__main__':
    main()
