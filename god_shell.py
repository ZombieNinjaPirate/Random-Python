#!/usr/bin/env python
# -*- coding: utf-8 -*-

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

__author__ = 'Black September'
__date__ = '2014, Jan 1'
__version__ = '1.1.0'


import argparse
import logging
import os
import paramiko
import socket
import sys


def parse_args():
    """Define the command line arguments. """
    parser = argparse.ArgumentParser(prog=sys.argv[0],
    formatter_class=argparse.RawDescriptionHelpFormatter, description=(
    '\tThe God Shell - (C) 2014 Black September.\n\n'
    'This is acts as an interactive shell that can be used to execute commands\n'
    'on a number of remote hosts. The commands will be execute in sequential\n'
    'order.\n\n'
    'When the interactive shell you can enter any command as if you were on\n'
    'the remote host. The returned outpur will be returned to your stdout when\n'
    'execution is completed before it moves on to the next one.\n\n'
    'In addition to the optional arguments thats passed from the command line,\n'
    'the interactive shell also accepts certain arguments after started\n\n'
    'Interactive arguments:\n'
    '- HELP\t\t\tShows this help menu.\n'
    '- LIST\t\t\tLists the currently loaded hosts.\n'
    '- LDEL\t\t\tList the removed hosts.\n'
    '- ADD [host]\t\tAdd a host to the list.(NOT IMPLEMENTED YET)\n'
    '- DEL [host]\t\tDelete host from the list.(NOT IMPLEMENTED YET)\n'))

    remote = parser.add_argument_group('- Remote host arguments')
    remote.add_argument('-H', '--hosts', help='Hostname(s)', nargs='+')
    remote.add_argument('-F', '--file', help='One hostne pr.line', type=file)
    remote.add_argument('-U', '--user', help='Username', required=True)

    logs = parser.add_argument_group('- Log arguments')
    logs.add_argument('-L', '--log', help='''Generates a separate log file for each
                                                host.''', action='store_true')
    args = parser.parse_args()

    return args


def interactive_startup():
    """Interactive startup banner. """
    os.system('/usr/bin/clear')
    print('''
    +------------------------------------------------------------+
    |            God Shell - (C) 2014 Black September            |
    +------------------------------------------------------------+

              Type HELP to see view interactive options.
                      Press CTRL + C to exit.
    ''')


def interactive_help():
    """Help menu called for the interactive shell. """
    print('''
    - HELP\t\t\tShows this help menu.
    - LIST\t\t\tLists the currently loaded hosts.
    - LDEL\t\t\tList the removed hosts.
    - ADD [host]\t\tAdd a host to the list.(NOT IMPLEMENTED YET)
    - DEL [host]\t\tDelete host from the list.(NOT IMPLEMENTED YET)
    ''')


def mass_execution(server_list, user, mode):
    """Cleans out any trailing new lines, tabs and spaces from the server_list and
    populates the target_list before the interactive shell is started in the while loop.
    Any linux command entered into the interactive shell is then executed using paramiko.
    If the remote host returns and error from not accepting the id_key or user name it
    will be added to the server_error list. Any host that has been entered into the
    server_error list will be removed from the target_list after the while loop has
    completed. The server_error list is cleared out before control is handed back to the
    interactive shell."""
    target_list = []
    server_error = []
    removed_list = []

    header = '-' * 55
    id_key = os.path.expanduser('~/.ssh/id_rsa')

    for server in server_list:
        target_list.append(server.rstrip())

    interactive_startup()

    while 1 == 1:
        for err_host in server_error:
            removed_list.append(err_host)

            if err_host in target_list:
                target_list.remove(err_host)
                log.warning('{0} has been removed.'.format(err_host))

        if len(server_error) > 0:
            print('\n{0} error host(s) has been excluded.'.format(len(server_error)))
            server_error = []

        cmd = raw_input('God_Shell> ')

        if cmd == 'HELP':
            interactive_help()
            continue

        if cmd == 'LIST':
            print('\nCurrent target list:')
            for target in target_list:
                print('- {0}'.format(target))
            print('\nTarget hosts: {0}'.format(len(target_list)))
            print('\n')
            continue

        if cmd == 'LDEL':
            print('\nCurrently removed hosts:')
            for removed in removed_list:
                print('- {0}'.format(removed))
            print('\nRemoved hosts: {0}'.format(len(removed_list)))
            print('\n')
            continue

        for host in target_list:
            print('# {0} [ {1} ]\n'.format(header, host))

            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, username=user, key_filename=id_key, timeout=1.0)
            except paramiko.AuthenticationException, err:
                server_error.append(host)
                print('ERROR: {0}\n'.format(err))
                log.error('{0}: {1}'.format(host, err))
                ssh.close()
                continue
            except socket.error, err:
                server_error.append(host)
                print('ERROR: {0}\n'.format(err))
                log.error('{0}: {1}'.format(host, err))
                ssh.close()
                continue

            _, stdout, stderr = ssh.exec_command(cmd)
            exit_status = stdout.channel.recv_exit_status()

            if 'LOGS' in mode:
                if str(exit_status) == '0':
                    fname = '{0}/{1}.log'.format(base_dir, host)
                    for lines in stdout.readlines():
                        print('{0}'.format(lines.rstrip()))
                        with open(fname, 'a') as logfile:
                            logfile.write('{0}'.format(lines))
                    with open(fname, 'a') as logfile:
                        logfile.write('\n')

                if str(exit_status) != '0':
                    for lines in stderr.readlines():
                        print('{0}'.format(lines.rstrip()))
                        log.warning('{0}'.format(lines))

                print('\n')

            if 'STDOUT' in mode:
                if str(exit_status) == '0':
                    for lines in stdout.readlines():
                        print('{0}'.format(lines.rstrip()))

                if str(exit_status) == '0':
                    for lines in stderr.readlines():
                        print('{0}'.format(lines.rstrip()))
                        log.warning('{0}'.format(lines))

                print('\n')

            ssh.close()


def check_args(args):
    """Preform basic checking of the arguments. """
    hostname = args.hosts
    username = args.user
    host_file = args.file
    logg_logs = args.log
    logg_mode = 'STDOUT'

    if len(sys.argv) == 0:
        print('Usage {0} -h/--help').format(sys.argv[0])
        sys.exit(1)

    if logg_logs:
        logg_mode = 'LOGS'

    if hostname and username:
        mass_execution(hostname, username, logg_mode)

    if host_file and username:
        targets = host_file.readlines()
        mass_execution(targets, username, logg_mode)


def main():
    """Process command line arguments, pass them to chack_args() and execute. """
    if len(sys.argv) == 1:
        print('\nUSAGE: {0} -h/--help\n').format(sys.argv[0])
        sys.exit(1)

    args = parse_args()
    check_args(args)


if __name__ == '__main__':
    base_dir = os.path.expanduser('~/God_Shell')
    log_file = os.path.expanduser('{0}/God_Shell.log'.format(base_dir))
    log = logging.getLogger('God_Shell')

    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',
                        filename=log_file, level=logging.WARNING)

    try:
        main()
    except KeyboardInterrupt:
        print '\nLeaving interactive shell. Good bye!\n'
        sys.exit(0)
