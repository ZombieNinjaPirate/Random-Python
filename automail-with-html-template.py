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

__author__ = 'Are Hansen'
__date__ = '2014, 3 February'
__version__ = '0.0.7'

import argparse
import sys
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from os import path, access, R_OK


def parse_args():
    """Command line options."""
    parser = argparse.ArgumentParser(description='Send mail')
    #
    #   Development notes:
    #
    #   Some of these arguments could be omitted by hardcoding them. Let me know if you
    #   want me to set that up.
    #
    src = parser.add_argument_group('- Source')
    src.add_argument('-S', dest='send_from', help='Send from', required=True)
    src.add_argument('-A', dest='user_name', help='Username (default: first part of email)')
    src.add_argument('-M', dest='smtp_srv', help='SMTP server', required=True)
    src.add_argument('-P', dest='smtp_port', help='SMTP port', required=True)
    src.add_argument('-W', dest='passwd', help='Senders password', required=True)

    body = parser.add_argument_group('- Body of email')
    body.add_argument('-Ba', dest='advisor', help='Name of Advisor', nargs='+', type=str, required=True)
    body.add_argument('-Bk', dest='komptime', help='Komp start time', type=str, required=True)
    body.add_argument('-Bl', dest='teamleader', help='Name of Team leader', type=str, required=True)
    body.add_argument('-Bn', dest='teamname', help='Name of Team', type=str, required=True)

    rec = parser.add_argument_group('- Recipient')
    rec.add_argument('-D', dest='send_to', help='Recipient(s)', required=True, nargs='+')
    
    args = parser.parse_args()
    
    return args


def send_as_html(sendf, uname, smtps, smtpp, pwd, sendt, body):
    """Send mail in HTML format. """
    nowtime = time.strftime("%Y %B %d - %H:%M:%S")
    #
    #   Development notes:
    #
    #   If you want to change this template, make sure to change the 'text'
    #   AND the 'html' template. Changing just one of them will end in tears.
    #
    text = '''Hi {0}, submission for {1} is accepted!\nApproved by\n{2} - {3}\n
            Name of company Here\n{4}'''.format(body[0], body[1], body[2], body[3], nowtime)

    html = '''\
    <html>
    <body>
        <h2>
            Hi {0}, submission for {1} is accepted!<br/><br/>
        </h2>
        <h4>
            Approved by<br/>
            {2} - {3}<br/>
            Name of company Here<br>
            {4}<br>
        </h4>
    </body>
    </html>
    '''.format(body[0], body[1], body[2], body[3], nowtime)
    #
    #   Development notes:
    #
    #   The script will itterate trough the email recepients and send a separete email to them
    #   instead of sending as a bulk email. This would also improve the privacy of the recipients
    #   as the mail only contains a singel email address.
    #
    for email in sendt:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Your komprequest has been aproved!'
        msg['From'] = sendf
        msg['To'] = email
    
        part1 = MIMEText(text, 'plain')
        part2 = MIMEText(html, 'html')

        msg.attach(part1)
        msg.attach(part2)

        try:
            s = smtplib.SMTP('{0}:{1}'.format(smtps, smtpp))
        except smtplib.socket.gaierror:
            s.quit()
            sys.exit(1)

        try:
            s.starttls()
            s.login(uname, pwd)
        except SMTPAuthenticationError:
            s.quit()
            sys.exit(1)

        s.sendmail(sendf, email, msg.as_string())
        s.quit()


def check_args(args):
    """Command line parsing. """
    send_from = args.send_from
    user_name = args.user_name
    smtp_srv = args.smtp_srv
    smtp_port = args.smtp_port
    passwd = args.passwd
    send_to = args.send_to
    advisor = ' '.join(args.advisor)
    body = [advisor, args.komptime, args.teamleader, args.teamname]

    if not user_name:
        user_name = send_from.split('@')[0]

    send_as_html(send_from, user_name, smtp_srv, smtp_port, passwd, send_to, body)


def main():
    """Main function. """
    args = parse_args()
    check_args(args)


if __name__ == '__main__':
    main()
