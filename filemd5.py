#!/usr/bin/env python


"""
Calculate MD5 hash of a file.

Copyright (c) 2014, Are Hansen

All rights reserved.
 
Redistribution and use in source and binary forms, with or without modification, are
permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this list
of conditions and the following disclaimer.
 
2. Redistributions in binary form must reproduce the above copyright notice, this
list of conditions and the following disclaimer in the documentation and/or other
   materials provided with the distribution.
 
THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND AN
EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES
OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT
SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR
BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

__author__ = 'Are Hansen'
__date__ = '2014, May 11'
__version__ = '0.0.1'


import argparse
import hashlib
import sys
from os import path, access, R_OK


def parse_args():
    """Defines the command line arguments. """
    parser = argparse.ArgumentParser('Calculates the MD5 sum of a given file.')

    grp1 = parser.add_argument_group('- File')
    grp1.add_argument('-F', dest='md5file', help='Path to file', required=True)

    args = parser.parse_args()

    return args


def find_md5(target_file):
    """Calculate the md5sum of a file. """
    md5_out = hashlib.md5(open(target_file).read()).hexdigest()

    print('MD5 sum of {0}: {1}'.format(target_file, md5_out))



def process_args(args):
    """Process the command line arguments. """
    md5file = args.md5file

    if path.isfile(md5file) and access(md5file, R_OK):
        find_md5(md5file)
    else:
        print 'ERROR: Unable to either find and/or read {0}'.format(md5file)
        sys.exit(1)


def main():
    """Do what Main does best... """
    args = parse_args()
    process_args(args)


if __name__ == '__main__':
    main()
