import re
import sqlalchemy as sa

from sqlalchemy import types

def camel2under(x):
    """Convert Camelcase words to underscore separated words

    >>> camel2under("HelloWorld")
    hello_world

    """
    return re.sub(r"(?<=[a-z])([A-Z])", r"_\1", x).lower()

def subset(d, keys):
    """ Subset a dictionary """
    return dict((k, v) for k, v in d.iteritems() if k in keys)

## 
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
    """Day of the month

    An integer column with a check constraint that the
    values are in 1-31.
    
    """
    
    def __init__(self, name=None):
        self.values = range(1, 32)
        self.name = name

class Month(IntegerConstrained, types.SchemaType):
    """ Month

    An integer column with a check constraint that the
    values are in 1-12.
    """
    
    def __init__(self, name=None):
        self.values = range(1, 13)
        self.name = name

        
