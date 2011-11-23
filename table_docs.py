""" For each table in irdata.model write out a rst documenting """
from os import path
import codecs

from irdata import model

METADIR = path.join(irdata.__path__[0], 'data', 'metadata')

def fkey_string(x):
    return "%s.%s" % (x.column.table.name, x.column.name)

def db_metadata(x):
    y = []
    for c in x.columns:
        fkeylist = ', '.join([fkey_string(x) for x in c.foreign_keys])
        y.append((c.name, "%s; %s" % (str(c.type), fkeylist)))
    return y

def format_db_column(x):
    return ":%s: %s" % x

def fieldlist(x):
    fields = []
    indent = 2
    for k, v in x.iteritems():
        if isinstance(v, list):
            vstr = '\n' + '\n'.join(['%s- %s' % ('  ' * indent, x) for x in v])
        else:
            vstr = str(v)
        fields.append(":%s: %s" % (k, vstr))
    return '\n'.join(fields)

def format_title(x, character = "="):
    return "%s\n%s" % (x, character * len(x))

def column_descriptions(x):
    return'\n'.join([":%s: %s" % (k, v) for k, v  in x.iteritems()])

TEMPLATE = u"""
{title}

{tablecols}

Description
-------------

{coldescriptions} 

{description}

{metadata}
"""

destination = 'doc/source/tables'
for tablename, table in model.Base.metadata.tables.iteritems():
    with open(path.join(METADIR, '%s.yaml' % tablename), 'r') as f:
        metadata = yaml.load(f)
    title = format_title(tablename)
    tablecols = '\n'.join(format_db_column(x) for x in db_metadata(table))
    description = metadata['description']
    del metadata['description']
    coldescriptions = column_descriptions(metadata['columns'])
    del metadata['columns']
    document = TEMPLATE.format(title = title, tablecols = tablecols,
                               coldescriptions = coldescriptions,
                               description = description,
                               metadata = fieldlist(metadata))
    with codecs.open(path.join(destination, '%s.rst' % tablename), 'w', 'utf8') as f:
        f.write(document)
        
    
    
        


