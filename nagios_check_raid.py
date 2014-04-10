#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
   Copyright (c) 2013, Are Hansen

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
   
    Nagios plugin for checking software RAID status.
"""

__date__ = '2013, November 5'
__author__ = 'Are Hansen'
__version__ = '1.1.0'


import argparse
import paramiko
import sys
import socket


def parse_args():
    """
    Parse command line arguments. Both RHOST and RUSER is required arguments, script will
    halt if not present.
    """
    parser = argparse.ArgumentParser(description='''Checks the RAID status on a remote
                                                    machine''')
    host = parser.add_argument_group('- Host agruments')
    host.add_argument('-rh', '--rhost', help='Remote hostname (IP/FQDN)', required=True)
    host.add_argument('-ru', '--ruser', help='Remote username', required=True)
    
    args = parser.parse_args()
    
    return args


def ssh_rexec(rhost, ruser):
    """
    Connects to the server and checks the RAID status, any returned value thats NOT
    'RAID OK' is treated as WARNINIG.
    """
    raid_status = ''
    cmd = "sudo megaclisas-status --nagios"
    
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(rhost, username=ruser)
    except paramiko.AuthenticationException:
        print 'ERROR: Authentication as {0}@{1} failed.'.format(ruser, rhost)
        ssh.close()
        sys.exit(1)
    except socket.error:
        print 'ERROR: Connection to {0} failed.'.format(rhost)
        ssh.close()
        sys.exit(1)
    
    stdin, stdout, stderr = ssh.exec_command(cmd)
    raid_status = stdout.readline()
    ssh.close()
    
    return raid_status


def nagiosify(raid_status):
    """
    Check value of raid_status against raid_string.
    """
    exit_message = ""
    exit_code = 0
    
    if 'RAID OK' in raid_status:
        exit_message += 'OK: {0}'.format(raid_status)
    else:
        exit_message += 'WARNING: {0}'.format(raid_status)
        exit_code = 2
    
    print(exit_message)
    sys.exit(exit_code)


def check_args(args):
    """
    Preform basic checking of the arguments.
    """
    rhost = args.rhost
    ruser = args.ruser
    nagiosify(ssh_rexec(rhost, ruser))


def main():
    """
    Main: Being a function, like a Bozz!
    """
    args = parse_args()
    check_args(args)


if __name__ == '__main__':
    main()
