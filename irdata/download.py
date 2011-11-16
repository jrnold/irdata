""" Download external sources needed to build the database """
import sys
import os 
from os import path
import argparse
import subprocess as sp

import yaml

def wget(filename, dirname):
    """ wget wrapper

    :param filename: str. file to download
    :param dirname: str. directory in which to download the file.

    Runs `wget -xN -P [dirname] [filename]`.
    
    """
    sp.call(["wget", "-x", "-N", "-P", dirname, filename])
    

def download_all(dirname):
    """ Download all external data sources

    :param dir: directory to download to (optional)
    :rtype: none

    """
    if dir:
        if not os.path.isdir(dirname):
            print("creating %s" % dirname)
            os.makedirs(dirname)
    with open(path.join(path.dirname(__file__),
                        'data', 'filelist.yaml')) as f:
        filelist = yaml.load(f)
    for fname in filelist:
        wget(fname, dirname)
 
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Download external data for irdata ')
    parser.add_argument('directory', metavar='dir', type=str,
                        help='directory in which to download data sources.')
    parser.print_help()
    opts = parser.parse_args()
    print(opts)
    download_all(opts.directory)
