#!/usr/bin/env python


__author__ = 'Are Hansen'
__date__ = '2015, Feb 10'
__version__ = 'DEV-0.0.2'


import argparse
import os
import sys


def parse_args():
    """Command line options."""
    parser = argparse.ArgumentParser(description='Add DROP rules to iptables file')

    files = parser.add_argument_group('- Sources to DROP')
    files.add_argument(
                      '-s', 
                      dest='ipadds', 
                      help='File containing single ip address(es) that should be blocked' 
                      )
    files.add_argument(
                      '-r', 
                      dest='iprange', 
                      help='File containing iprange(s) that should be blocked'
                      )
    outfile = parser.add_argument_group('- Output file')
    outfile.add_argument(
                       '-O', 
                       dest='linesec', 
                       help='Output file (default: /etc/network/iptables.TODAY)'
                       )

    args = parser.parse_args()
    
    return args



def srcrngdrop(srcrnglist):
    """Create source range rules. Returns the rules as a list object. """
    srlo = []

    for srcrng in srcrnglist:
        append.srlo('-A INPUT -m iprange --src-range {0} -j DROP'.format(srcrng))

    return srlo


def srcipdrop(srciplist):
    """Create single ip rules. Returns the rules as a list object. """
    silo = []

    for srcip in srciplist:
        append.silo('-A INPUT -i eth0 -s {0} -j DROP'.format(srcip))

    return silo


# ========== Generate OUT_FILE(MERGE)
#
# Write HEAD to OUT_FILE.tmp
#   Append HEAD EOF in OUT_FILE.tmp
#
# Create DROP rules from SRC in MERGE
#   Append DROP rules to OUT_FILE.tmp
#   Append MERGE EOF in OUT_FILE.tmp
#
# Append TAIL to OUT_FILE.tmp
#


def parse_args(args):
    """Parse and check the arguments. """
    # verify that we are getting argumetns
    # verify that all files are present
    # verify what arguments are being executed


def main():
    """The main brain... """
    args = parse_args()
    process_args(args)


if __name__ == '__main__':
    main()

