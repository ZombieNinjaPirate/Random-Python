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

"""
    Send email using the credentials of an existing account.
    Allows for sending the contents of a file or a string.
"""

__author__ = 'Are Hansen'
__date__ = '2014, 3 February'
__version__ = '0.0.3'


import argparse
import sys
import smtplib
from email.mime.text import MIMEText
from os import path, access, R_OK


def parse_args():
    """Command line options."""
    parser = argparse.ArgumentParser(description='Send mail')

    src = parser.add_argument_group('- Source')
    src.add_argument('-S', dest='send_from', help='Send from (Required)', required=True)
    src.add_argument('-A', dest='user_name', help='Username (default: first part of email)')
    src.add_argument('-U', dest='subject', help='Mail subject (Required)', required=True)
    src.add_argument('-M', dest='smtp_srv', help='SMTP server (Required)', required=True)
    src.add_argument('-P', dest='smtp_port', help='SMTP port (Required)', required=True)
    src.add_argument('-W', dest='passwd', help='Senders password (Required)', required=True)

    rec = parser.add_argument_group('- Recipient')
    rec.add_argument('-D', dest='send_to', help='Recipient (Required)', required=True)

    body = parser.add_argument_group('- Message body (One is Required)')
    body.add_argument('-Bs', dest='body_str', help='Body (string)', type=str)
    body.add_argument('-Bf', dest='body_file', help='Body (/path/to/file)')
    
    args = parser.parse_args()
    
    return args


def send_mail(sendf, uname, subj, smtps, smtpp, pwd, sendt, body, btype):
    """Send mail using the provided variables. """
    if btype == 'FILE':
        try:
            fp = open(body, 'rb')
            msg = MIMEText(fp.read())
            fp.close()
        except IOError:
            sys.exit(1)

    if btype == 'STR':
        msg = body

    myemail = sendf
    myuname = uname
    mypassw = pwd
    toemail = sendt

    msg['Subject'] = subj
    msg['From'] = '{0}'.format(sendf)
    msg['To'] = '{0}'.format(toemail)

    try:
        print('Connecting to {0}:{1}...'.format(smtps, smtpp))
        s = smtplib.SMTP('{0}:{1}'.format(smtps, smtpp))
    except smtplib.socket.gaierror:
        s.quit()
        print('Conection status: {0}:{1} FAILED!'.format(smtps, smtpp))
        sys.exit(1)

    print('Conection status: {0}:{1} OK'.format(smtps, smtpp))

    try:
        s.starttls()
        print('Authenticating to {0} as {1}...'.format(smtps, myuname))
        s.login(myuname, mypassw)
    except SMTPAuthenticationError:
        s.quit()
        print('Authentication to {0} as {1}: FAILED!'.format(smtps, myuname))
        sys.exit(1)

    print('Authentication to {0} as {1}: OK'.format(smtps, myuname))

    print myemail
    print [toemail]
    print('Sending mail...')
    s.sendmail(myemail, toemail, msg.as_string())
    s.quit()


def check_args(args):
    """Command line parsing. """
    send_from = args.send_from
    user_name = args.user_name
    subject = args.subject
    smtp_srv = args.smtp_srv
    smtp_port = args.smtp_port
    passwd = args.passwd
    send_to = args.send_to
    body_str = args.body_str
    body_file = args.body_file

    if not body_str and not body_file:
        print("ERROR: You are required to use either '-Bs' or '-Bf'!")
        sys.exit(1)

    if body_str and body_file:
        print("ERROR: You can only specify either '-Bs' or '-Bf', not both of them!")
        sys.exit(1)

    if body_str and not body_file:
        body = body_str
        btype = 'STR'

    if body_file and not body_str:
        if path.isfile(body_file) and access(body_file, R_OK):
            body = body_file
            btype = 'FILE'
        else:
            print('\nERROR: Unable to read/find "{0}"\n'.format(body_file))
            sys.exit(1)

    if not user_name:
        user_name = send_from.split('@')[0]

    send_mail(send_from, user_name, subject, smtp_srv, smtp_port, passwd, send_to, body, btype)


def main():
    """Main function. """
    args = parse_args()
    check_args(args)


if __name__ == '__main__':
    main()
