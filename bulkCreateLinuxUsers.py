#!/usr/bin/env python
# -*- coding: utf-8 -*-


__author__ = 'Are Hansen'
__date__ = '2014, May 11'
__version__ = '0.0.4'


"""
   Reads file with USERNAME/PASSWORD. The USERNAME and PASSWORD will be used to generate a 'newusers'
   compatible format. The output could be piped directly to 'newusers' or to a file that can be read
   by 'newusers' later.

   The script takes two arguments.
   - 1: Path to the USERNAME/PASSWORD file
   - 2: Starting UID/GID, this is incremented by one for each user account.
"""

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
"""


import argparse
import random
import sys


def parse_args():
    """Command line options."""
    parser = argparse.ArgumentParser(description='Cenerate bulk Linux accounts')

    files = parser.add_argument_group('- Files')
    files.add_argument('-I', dest='infile', help='Delimiter separated user/passwd file.',
                       required=True, type=argparse.FileType('rt'))
    files.add_argument('-D', dest='delim', help='Column separator (default: "/")', type=str,
                        default='/')

    account = parser.add_argument_group('- Account')
    account.add_argument('-U', dest='uid', help='Starting number for user UID/GID', required=True,
                          type=int)

    args = parser.parse_args()
    
    return args


def generate_accounts(usr_lines, delim, uid):
    """Check and resolve issues with duplicate names. Generate passwd formated output that can be
    handed off to 'newusers'. """
    addstr = ['13', '29', '37', '49', '56', '68', '72', '18', '19', '007', '666', '22', '82', '404',
              '1337', '76', '77', '14', '2014', '1999', '0', '4', '111', '88', '1', '2', '3', '5']

    user_list = {}

    for item in usr_lines:
        group = item.split(delim)[0].strip()
        user = item.split(delim)[1].strip()
        passwd = item.split(delim)[2].strip()

        if  user in user_list:
            multi = '{0}{1}'.format(user, random.choice(addstr))
            user_list[multi] = group, passwd
        else:
            user_list[user] = group, passwd

    for key, value in user_list.items():
        print '{0}:{1}:{3}:{3}:{2}:/home/{0}:/bin/bash'.format(key, value[1], value[0].lower(), uid)
        uid = uid + 1


def check_args(args):
    """Command line parsing. """
    output = []

    for line in args.infile:
        output.append(line.rstrip())

    generate_accounts(output, args.delim, args.uid)


def main():
    """Main function. """
    args = parse_args()
    check_args(args)


if __name__ == '__main__':
    main()
