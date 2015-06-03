#!/usr/bin/env python


"""
Copyright (c) 2015, Are Hansen

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
STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""


import argparse
import os
import re
import sys
import urllib2


__app__ = sys.argv[0].split('/')[-1].split('.')[-2]
__author__ = 'Are Hansen'
__date__ = '2015, June 2'
__version__ = '0.0.2'



def parse_args():
    """Command line options."""
    parser = argparse.ArgumentParser(
             description='{0} - v{1}, {2} - {3}\n'.format(__app__, __version__, __date__, __author__)
             )

    src = parser.add_argument_group('- Target source')
    trg = src.add_mutually_exclusive_group(required=True)
    trg.add_argument(
                     '-U', 
                     dest='url', 
                     help='URL to page containing IPv4 objects',
                     nargs=1 
                     )
    trg.add_argument(
                     '-F',
                     dest='ipfile',
                     help='File containing IPv4 objects',
                     nargs='?',
                     type=argparse.FileType('r')
                     )

    atk = parser.add_argument_group('- Offensive options')
    atk.add_argument(
                     '-s',
                     dest='nmap',
                     help='Scan IPv4 objects with Nmap',
                     action='store_true'
                     )
    atk.add_argument(
                     '-b',
                     dest='bf',
                     help='File format Password:Username. Used against open SSH ports',
                     nargs='?',
                     type=argparse.FileType('r')
                     )

    args = parser.parse_args()    
    return args


def getTargets(gurl):
    """Requests a web page, extracts any in the format of an IPv4 address and returns those objects
    in the form of a list."""
    try:
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        req = urllib2.Request(gurl)
        res = opener.open(req)
        page = str(res.readlines())
        ipv4 = re.findall( r'[0-9]+(?:\.[0-9]+){3}', page)
        return ipv4
    except urllib2.URLError, err:
         return err

def process_args(args):
    """Parse and check the arguments. """


def main():
    """The main brain... """
    args = parse_args()
    process_args(args)


if __name__ == '__main__':
    main()
