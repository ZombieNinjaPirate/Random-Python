#!/usr/bin/env python


"""
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
   STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF
   THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.


    Searches trough log files for potential issues on OS X.
"""


__author__ = 'Are Hansen'
__date__ = '2014, March 13'
__version__ = '1.0.2'


import argparse
import os
import re
import sys
import time
from os.path import expanduser


def parse_args():
    """Command line definitions """
    parser = argparse.ArgumentParser(description='''Searches trough log files for potential
                                                 issue on OS X. ''')
    host = parser.add_argument_group('- File arguments')
    host.add_argument('-F', dest='logfile', help='/path/to/file.log', required=True,
                      type=file)

    search = parser.add_argument_group('- Additional search queries')
    search.add_argument('-Q', dest='query', help='Search term (singel words, case sensitive)',
                        nargs='+')

    args = parser.parse_args()
    
    return args


def standard_search(log_lines):
    """Static search queries, return matching queries. """
    mackeeper = []
    cleanmy = []
    norton = []
    symantec = []
    sophos = []
    tmbackup = []
    error = []
    fail = []
    warn = []
    
    for line in log_lines:
        if re.search('mackeeper', line, re.IGNORECASE):
            mackeeper.append(line)

        if re.search('cleanmy', line, re.IGNORECASE):
            cleanmy.append(line)

        if re.search('norton', line, re.IGNORECASE):
            norton.append(line)

        if re.search('symantec', line, re.IGNORECASE):
            symantec.append(line)

        if re.search('sophos', line, re.IGNORECASE):
            sophos.append(line)

        if re.search('com.apple.backupd', line, re.IGNORECASE):
            tmbackup.append(line)

        if re.search('error', line, re.IGNORECASE):
            error.append(line)

        if re.search('fail', line, re.IGNORECASE):
            fail.append(line)

        if re.search('warning', line, re.IGNORECASE):
            warn.append(line)

    tuplists = (mackeeper, cleanmy, norton, symantec, sophos, tmbackup, error, fail, warn)

    return tuplists


def custom_search(log_lines, search_terms):
    """Uses custom search queries, returns matching lines."""
    for terms in search_terms:
        print('\n# =============================== {0}:\n'.format(terms))
        for line in log_lines:
            if re.search(terms, line):
                print line.rstrip()
        print('\n')


def results(tupl):
    """Prints the  """
    mac_len = len(tupl[0])
    clean_len = len(tupl[1])
    nor_len = len(tupl[2])
    sym_len = len(tupl[3])
    sop_len = len(tupl[4])
    tm_len = len(tupl[5])
    err_len = len(tupl[6])
    fail_len = len(tupl[7])
    warn_len = len(tupl[8])
    
    if mac_len > 0:
        print('\n# =============================== MacKeeper:\n')
        for mac in tupl[0]:
            print(mac.rstrip())
    if clean_len > 0:
        print('\n\n# =============================== CleanMyMac:\n')
        for clean in tupl[1]:
            print(clean.rstrip())

    if nor_len > 0:
        print('\n\n# =============================== Norton:\n')
        for nor in tupl[2]:
            print(nor.rstrip())

    if sym_len > 0:
        print('\n\n# =============================== Symantec:\n')
        for sym in tupl[3]:
            print(sym.rstrip())

    if sop_len > 0:
        print('\n\n# =============================== Sophos:\n')
        for sop in tupl[4]:
            print(sop.rstrip())

    if tm_len > 0:
        print('\n\n# =============================== TimeMachine:\n')
        for tm in tupl[5]:
            print(tm.rstrip())

    if err_len > 0:
        print('\n\n# =============================== Errors:\n')
        for err in tupl[6]:
            print(err.rstrip())

    if fail_len > 0:
        print('\n\n# =============================== Failures:\n')
        for fail in tupl[7]:
            print(fail.rstrip())

    if warn_len > 0:
        print('\n\n# =============================== Warnings:\n')
        for war in tupl[8]:
            print(err.rstrip())

    divider0 = '=' * 45
    divider1 = '-' * 45
    
    print('\n\n{0}\n'.format(divider0))

    if mac_len > 0:
        print('- MacKeeper:\t{0}'.format(mac_len))

    if clean_len > 0:
        print('- CleanMyMac:\t{0}'.format(clean_len))

    if nor_len > 0:
        print('- Norton:\t{0}'.format(nor_len))

    if sym_len > 0:
        print('- Symantec:\t{0}'.format(sym_len))

    if sop_len > 0:
        print('- Sophos:\t{0}'.format(sop_len))

    if tm_len > 0:
        print('- TimeMachine:\t{0}'.format(tm_len))

    if err_len > 0:
        print('- Error:\t{0}'.format(err_len))

    if fail_len > 0:
        print('- Failures:\t{0}'.format(fail_len))

    if warn_len > 0:
        print('- Warning:\t{0}'.format(warn_len))

    print('\n{0}'.format(divider1))
    print('Total run time:\t{0:.2f} seconds.'.format(time.time() - start_time))
    print('{0}\n'.format(divider0))





def check_argumetns(args):
    """Check the command line arguments. """
    logfile = args.logfile

    if args.query:
        query_list = args.query
        logfile = args.logfile
        custom_search(logfile, query_list)

    if not args.query:
        query_lists = standard_search(logfile)
        results(query_lists)


def main():
    """Bozz function. """
    args = parse_args()
    check_argumetns(args)


if __name__ == '__main__':
    start_time = time.time()
    try:
        main()
    except IOError, e:
        print('\nERROR: Log file does not exist or you dont have permission to read it\n')
        sys.exit(1)
