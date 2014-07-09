#!/usr/bin/env python


"""Generate useraccounts that can be imported by newusers under Linux. """


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


__author__ = 'Are Hansen'
__date__ = '2014, July 8'
__version__ = '0.0.1'


import argparse
import os
import re
import sys
try:
  import names
except ImportError:
  print '\nERROR: You need the module called "names"!\n'
  sys.exit(1)


def parse_args():
    """Defines the command line arguments. """
    parser = argparse.ArgumentParser(description='Extract data from IRC transcripts')

    genusr = parser.add_argument_group('- Generation options')
    genusr.add_argument('-N', dest='number', help='Number of user accounts to create (Required)',
                        required=True, type=int)
    genusr.add_argument('-P', dest='passfile', help='File with one password/line (Required)',
                        type=file)
    genusr.add_argument('-G', dest='startgid', help='Starting GID (Required)', required=True,
                         type=int)

    args = parser.parse_args()

    return args


def make_users(numb):
    """Generate a list of unique account names and returns the list. """
    user_list = []
    start = 0

    # Keep running the loop until the number of unique names has been
    # generated and appended to the list
    while start != numb:
        user = names.get_full_name()
        if user not in user_list:
            user_list.append(user)
            start = start + 1

    account_list = []
    xnumb = 0
    # Create unique account names and append to the list
    for user in user_list:
        account = '{0}{1}'.format(user.split(' ')[0].lower()[0:2], user.split(' ')[1].lower())
        if account not in account_list:
            account_list.append(account)
        elif account in account_list:
            account_list.append('{0}{1}'.format(account, xnumb))
            xnumb = xnumb + 1

    return account_list


def make_passwd(pwd_lines, user_list, startgid):
    """Reads the needed number of passwords from an existing file and mangles then slightly before
    the entire list is returned from the function. """
    pwd_lines = pwd_lines[0:len(user_list)]
    lists = zip(pwd_lines, user_list)
    gid = startgid

    for pwd, user in lists:
        print '{0}:{1}:{2}:{2}:{0}:/home/{0}:/bin/bash'.format(user, pwd, gid)
        gid = gid + 1


def process_args(args):
    """Process the command line arguments."""
    number = args.number

    pwd_list = []
    for passwd in args.passfile:
        pwd_list.append(passwd.rstrip())

    # Check that number of users dont exceed the number of avalible passwords
    if int(number) > int(len(pwd_list)):
        print 'ERROR:\nCan are trying to create {0} user accounts'.format(number)
        print 'but you only have {0} passwords.\n'.format(len(pwd_list))
        sys.exit(1)

    accounts = make_users(number)
    make_passwd(pwd_list, accounts, args.startgid)


def main():
    """Do what Main does best."""
    args = parse_args()
    process_args(args)


if __name__ == '__main__':
    main()
