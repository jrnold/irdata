""" Dump metadata template for each 
"""
import sys
from os import path

import yaml

from irdata import model

TEMPLATE = {'description': "",
            'date': "",
            'creator': "",
            'source': "",
            'see_also': "",
            'columns': ""}

def dump_metadata(tablename):
    """ Dump yaml metadata file template of table to stdout"""
    table = model.Base.metadata.tables[tablename]
    data = TEMPLATE.copy()
    data['columns'] = dict([(c.name, c.doc) for c in table.columns])
    for k, v  in data['columns'].iteritems():
        if v is None:
            data['columns'][k] = ""
    print(yaml.dump(data, default_flow_style=False))

def main():
    """ Dump a metadata template for a table"""
    table = sys.argv[1]
    dump_metadata(table)

if __name__ == '__main__':
    main()
    
    
        

