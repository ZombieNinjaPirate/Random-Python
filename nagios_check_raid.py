#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Nagios plugin for checking software RAID status.
"""

__date__ = '2013, November 5'
__author__ = 'Black September'
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
