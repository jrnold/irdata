""" Dump metadata template for each 
"""
from os import path

import yaml

from irdata import model

TEMPLATE = {'description': "",
            'date': "",
            'creator': "",
            'source': "",
            'see_also': "",
            'columns': ""}

def dump_metadata(dirname):
    for tablename, table in model.Base.metadata.tables.iteritems():
        data = TEMPLATE.copy()
        data['columns'] = dict([(c.name, c.doc) for c in table.columns])
        with open(path.join(dirname, '%s.yaml' % tablename), 'w') as f:
            yaml.dump(data, f, default_flow_style=False)

def main():
    """ Dump a metadata template for each table in the database model to a directory""" 
    dirname = sys.argv[1]
    dump_metadata(dir)

if __name__ == '__main__':
    main()
    
    
        

