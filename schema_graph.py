#!/usr/bin/env python
import sys

import sadisplay
from irdata import model

if __name__ == '__main__':
    outfile = sys.argv[1]
    desc = sadisplay.describe([getattr(model, attr) for attr in dir(model)])
    open(outfile, 'w').write(sadisplay.dot(desc))

