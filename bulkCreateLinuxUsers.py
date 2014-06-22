#!/usr/bin/env python
# -*- coding: utf-8 -*-


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


__author__ = 'Are Hansen'
__date__ = '2014, May 11'
__version__ = '0.0.3'


import sys

users = []
with open(sys.argv[1], 'rU') as accounts:
    for account in accounts.readlines():
        	users.append(account)

UID = sys.argv[2]
for user in users:
	username = user.split('/')[0].rstrip()
	password = user.split('/')[1].rstrip()
	print '{0}:{1}:{2}:{2}:{0}:/home/{0}:/bin/bash'.format(username, password, UID)
	UID = UID + 1

