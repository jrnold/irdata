import re

def camel2under(x):
    """Convert Camelcase words to underscore separated words

    >>> camel2under("HelloWorld")
    hello_world

    """
    return re.sub(r"(?<=[a-z])([A-Z])", r"_\1", x).lower()

def subset(d, keys):
    """ Subset a dictionary """
    return dict((k, v) for k, v in d.iteritems() if k in keys)
