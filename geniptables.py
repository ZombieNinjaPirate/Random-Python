#!/usr/bin/env python


"""Generates a iptables file thats configured to act as data control. This script is intended to be
used on the Bifrozt honeypot router, http://sourceforge.net/projects/bifrozt/, but it should work on
any system with iptables. """


"""
   Copyright (c) 2014, Are Hansen - Honeypot Development

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
__date__ = '2014, July 17'
__version__ = '0.0.0'


cidr = '24'
network = '10.48.139.0'
gateway = '10.48.139.1'
brdcast = '10.48.139.255'

# Holds all the iptable values
iptables_list = []
iptables_list.append('*filter')
iptables_list.append(':INPUT ACCEPT [0:0]')
iptables_list.append(':FORWARD ACCEPT [0:0]')
iptables_list.append(':OUTPUT ACCEPT [0:0]')
iptables_list.append(':syn-flood - [0:0]')
iptables_list.append(':udp-flood - [0:0]')
iptables_list.append('-A INPUT -i lo -j ACCEPT')
iptables_list.append('-A INPUT -d 224.0.0.1/32 -j DROP')
# INPUT
iptables_list.append('-A INPUT -d {0}/32 -i eth1 -j ACCEPT'.format(brdcast))
iptables_list.append('-A INPUT -s {0}/{1} -d {2} -i eth1 -p tcp -m tcp --dport 22 -j DROP'.format(network, cidr, gateway))
iptables_list.append('-A INPUT -s {0}/{1} -p tcp -m tcp --sport 22 -i eth1 -j ACCEPT'.format(network, cidr))
iptables_list.append('-A INPUT -s {0}/{1} ! -d {0}/{1} -i eth1 -j DROP'.format(network, cidr))
iptables_list.append('-A INPUT -i eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT')
iptables_list.append('-A INPUT -i eth0 -p tcp -j ACCEPT')
iptables_list.append('-A INPUT -i eth0 -p udp -j ACCEPT')
iptables_list.append('-A INPUT -i eth0 -p icmp -j ACCEPT')
iptables_list.append('-A INPUT -i eth0 -p tcp -m tcp --dport 22 -j ACCEPT')

# Can not be excluded. 
# Get Admin sshd port from user.
while True:
   sshd_port = raw_input('- Bifrozt SSHD Admin port: ')

   if int(sshd_port) > 65535 or int(sshd_port) == 0:
      print 'Choose a port number between 1 and 65535'

   if int(sshd_port) <= 65535 or int(sshd_port) > 0:
      iptables_list.append('-A INPUT -i eth0 -p tcp -m tcp --dport {0} -j ACCEPT'.format(sshd_port))
      break

# FORWARD
iptables_list.append('-A FORWARD -i eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT')
iptables_list.append('-A FORWARD -i eth0 -m state --state RELATED,ESTABLISHED -j ACCEPT')


# Get UDP flood values from user
while True:
   udp_flood = raw_input('- UDP flood pkts/sec: ')

   if int(udp_flood) > 200 or int(udp_flood) <= 49:
      print 'You might consider keeping this value between 50 and 200 pkts/sec.'
      new_value = raw_input('- Press [ENTER] to keep current value ({0}), or enter new here: '.format(udp_flood))

      if len(new_value) == 0:
         iptables_list.append('-A FORWARD -p udp -j udp-flood')
         iptables_list.append('-A udp-flood -s {0}/{1} -i eth1 -p udp -m udp -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 20 -j LOG --log-prefix "BIFROZT - UDP-flood attack: "'.format(network, cidr, udp_flood))
         iptables_list.append('-A udp-flood -s {0}/{1} -i eth1 -p udp -m udp -m state --state NEW -m recent --update --seconds 1 --hitcount 20 -j DROP'.format(network, cidr))
         break

      if len(new_value) > 0:
         udp_flood = new_value
         iptables_list.append('-A FORWARD -p udp -j udp-flood')
         iptables_list.append('-A udp-flood -s {0}/{1} -i eth1 -p udp -m udp -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 20 -j LOG --log-prefix "BIFROZT - UDP-flood attack: "'.format(network, cidr, udp_flood))
         iptables_list.append('-A udp-flood -s {0}/{1} -i eth1 -p udp -m udp -m state --state NEW -m recent --update --seconds 1 --hitcount 20 -j DROP'.format(network, cidr))
         break      

   if int(udp_flood) <= 200 or int(udp_flood) >= 50:
      iptables_list.append('-A FORWARD -p udp -j udp-flood')
      iptables_list.append('-A udp-flood -s {0}/{1} -i eth1 -p udp -m udp -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 20 -j LOG --log-prefix "BIFROZT - UDP-flood attack: "'.format(network, cidr, udp_flood))
      iptables_list.append('-A udp-flood -s {0}/{1} -i eth1 -p udp -m udp -m state --state NEW -m recent --update --seconds 1 --hitcount 20 -j DROP'.format(network, cidr))
      break


# Get UDP flood values from user
while True:
   tcp_flood = raw_input('- TCP SYN flood pkts/sec: ')

   if int(tcp_flood) > 120 or int(tcp_flood) < 20:
      print 'You might consider keeping this value between 20 and 120 pkts/sec.'
      new_value = raw_input('- Press [ENTER] to keep current value ({0}), or enter new here: '.format(tcp_flood))

      print len(new_value)
      if len(new_value) == 0:
         iptables_list.append('-A FORWARD -p tcp --syn -j syn-flood')
         iptables_list.append('-A syn-flood -s {0}/{1} -i eth1 -p tcp -m tcp -m state --state NEW -m recent --set -m limit --limit 30/s --limit-burst 20 -j LOG --log-level 4 --log-prefix "BIFROZT - SYN-flood attack: "'.format(network, cidr, tcp_flood))
         iptables_list.append('-A syn-flood -s {0}/{1} -i eth0 -p tcp -m tcp -m state --state NEW -m recent --update --seconds 1 --hitcount 20 -j DROP'.format(network, cidr))
         break

      if len(new_value) > 0:
         tcp_flood = new_value
         iptables_list.append('-A FORWARD -p tcp --syn -j syn-flood')
         iptables_list.append('-A syn-flood -s {0}/{1} -i eth1 -p tcp -m tcp -m state --state NEW -m recent --set -m limit --limit 30/s --limit-burst 20 -j LOG --log-level 4 --log-prefix "BIFROZT - SYN-flood attack: "'.format(network, cidr, tcp_flood))
         iptables_list.append('-A syn-flood -s {0}/{1} -i eth0 -p tcp -m tcp -m state --state NEW -m recent --update --seconds 1 --hitcount 20 -j DROP'.format(network, cidr))
         break 

   if int(tcp_flood) <= 120 or int(tcp_flood) >= 20:
      iptables_list.append('-A FORWARD -p tcp --syn -j syn-flood')
      iptables_list.append('-A syn-flood -s {0}/{1} -i eth1 -p tcp -m tcp -m state --state NEW -m recent --set -m limit --limit 30/s --limit-burst 20 -j LOG --log-level 4 --log-prefix "BIFROZT - SYN-flood attack: "'.format(network, cidr, tcp_flood))
      iptables_list.append('-A syn-flood -s {0}/{1} -i eth0 -p tcp -m tcp -m state --state NEW -m recent --update --seconds 1 --hitcount 20 -j DROP'.format(network, cidr))
      break 


allowed_services = ['53']
#  Get FTP values from user
while True:
   ftp_values = raw_input('- Press [ENTER] to exclude FTP or enter pkts/sec: ')

   if len(ftp_values) == 0:
      print 'EXLUDED: FTP traffic'
      break

   if len(ftp_values) > 0:
      allowed_services.append('20:21')
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 20:21 -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 15 -j LOG --log-prefix "BIFROZT - FTP: " --log-level 7'.format(network, cidr, ftp_values))
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 20:21 -m state --state NEW -m recent --update --seconds 1 --hitcount 15 -j DROP'.format(network, cidr))
      break

#  DNS
iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p udp -m udp --dport 53 -m state --state NEW -j LOG --log-prefix "BIFROZT - DNS: " --log-level 7'.format(network, cidr))


#  Get HTTP values from user
while True:
   http_values = raw_input('- Press [ENTER] to exclude HTTP or enter pkts/sec: ')

   if len(http_values) == 0:
      print 'EXLUDED: HTTP traffic'
      break

   if len(http_values) > 0:
      allowed_services.append('80')
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 80 -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 20 -j LOG --log-prefix "BIFROZT - HTTP: " --log-level 7'.format(network, cidr, http_values))
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 80 -m state --state NEW -m recent --update --seconds 1 --hitcount 20 -j DROP'.format(network, cidr))
      break


#  Get HTTP values from user
while True:
   https_values = raw_input('- Press [ENTER] to exclude HTTPS or enter pkts/sec: ')

   if len(https_values) == 0:
      print 'EXLUDED: HTTPS traffic'
      break

   if len(https_values) > 0:
      allowed_services.append('443')
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 443 -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 20 -j LOG --log-prefix "BIFROZT - HTTPS: " --log-level 7'.format(network, cidr, https_values))
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 443 -m state --state NEW -m recent --update --seconds 1 --hitcount 20 -j DROP'.format(network, cidr))
      break


#  Get SMB values from user
while True:
   smb_values = raw_input('- Press [ENTER] to exclude SMB or enter pkts/sec: ')

   if len(smb_values) == 0:
      print 'EXLUDED: SMB traffic'
      break

   if len(smb_values) > 0:
      allowed_services.append('445')
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 445 -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 3 -j LOG --log-prefix "BIFROZT - SMB: " --log-level 7'.format(network, cidr, smb_values))
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 445 -m state --state NEW -m recent --update --seconds 1 --hitcount 3 -j DROP'.format(network, cidr))
      break


#  Get AFP values from user
while True:
   afp_values = raw_input('- Press [ENTER] to exclude AFP or enter pkts/sec: ')

   if len(afp_values) == 0:
      print 'EXLUDED: AFP traffic'
      break

   if len(afp_values) > 0:
      allowed_services.append('548')
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 548 -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 3 -j LOG --log-prefix "BIFROZT - AFP: " --log-level 7'.format(network, cidr, afp_values))
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 548 -m state --state NEW -m recent --update --seconds 1 --hitcount 3 -j DROP'.format(network, cidr))
      break


#  Get SMTP values from user
while True:
   smtp_values = raw_input('- Press [ENTER] to exclude SMTP or enter pkts/sec: ')

   if len(smtp_values) == 0:
      print 'EXLUDED: SMTP traffic'
      break

   if len(smtp_values) > 0:
      allowed_services.append('587')
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 587 -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 6 -j LOG --log-prefix "BIFROZT - SMTP: " --log-level 7'.format(network, cidr, smtp_values))
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 587 -m state --state NEW -m recent --update --seconds 1 --hitcount 6 -j DROP'.format(network, cidr))
      break


#  Get POP3S values from user
#  Get SMTP values from user
while True:
   pop3s_values = raw_input('- Press [ENTER] to exclude POP3S or enter pkts/sec: ')

   if len(pop3s_values) == 0:
      print 'EXLUDED: POP3S traffic'
      break

   if len(pop3s_values) > 0:
      allowed_services.append('995')
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 995 -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 6 -j LOG --log-prefix "BIFROZT - POP3S: " --log-level 7'.format(network, cidr, pop3s_values))
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 995 -m state --state NEW -m recent --update --seconds 1 --hitcount 6 -j DROP'.format(network, cidr))
      break

#  Get MSSQL values from user
while True:
   mssql_values = raw_input('- Press [ENTER] to exclude MSSQL or enter pkts/sec: ')

   if len(mssql_values) == 0:
      print 'EXLUDED: MSSQL traffic'
      break

   if len(mssql_values) > 0:
      allowed_services.append('1433')
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 1433 -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 3 -j LOG --log-prefix "BIFROZT - MSSQL: " --log-level 7'.format(network, cidr, mssql_values))
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 1433 -m state --state NEW -m recent --update --seconds 1 --hitcount 3 -j DROP'.format(network, cidr))
      break

#  Get MYSQL values from user
while True:
   mysql_values = raw_input('- Press [ENTER] to exclude MySQL or enter pkts/sec: ')

   if len(mysql_values) == 0:
      print 'EXLUDED: MySQL traffic'
      break

   if len(mysql_values) > 0:
      allowed_services.append('3306')
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 3306 -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 3 -j LOG --log-prefix "BIFROZT - MYSQL: " --log-level 7'.format(network, cidr, mysql_values))
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 3306 -m state --state NEW -m recent --update --seconds 1 --hitcount 3 -j DROP'.format(network, cidr))
      break


#  Get MS-RDP values from user
while True:
   ms_rdp_values = raw_input('- Press [ENTER] to exclude MS-RDP or enter pkts/sec: ')

   if len(ms_rdp_values) == 0:
      print 'EXLUDED: MS-RDP traffic'
      break

   if len(ms_rdp_values) > 0:
      allowed_services.append('3389')
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 3389 -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 6 -j LOG --log-prefix "BIFROZT - MS-RDP: " --log-level 7'.format(network, cidr, ms_rdp_values))
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 3389 -m state --state NEW -m recent --update --seconds 1 --hitcount 6 -j DROP'.format(network, cidr))
      break


#  Get IRC values from user
while True:
   irc_values = raw_input('- Press [ENTER] to exclude IRC or enter pkts/sec: ')

   if len(irc_values) == 0:
      print 'EXLUDED: MySQL traffic'
      break

   if len(irc_values) > 0:
      allowed_services.append('6660:6667')
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 6660:6667 -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 20 -j LOG --log-prefix "BIFROZT - IRC: " --log-level 7'.format(network, cidr, irc_values))
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 6660:6667 -m state --state NEW -m recent --update --seconds 1 --hitcount 20 -j DROP'.format(network, cidr))
      break


#  Get HTTP-Alt values from user
while True:
   http_alt_values = raw_input('- Press [ENTER] to exclude HTTP-Alt or enter pkts/sec: ')

   if len(http_alt_values) == 0:
      print 'EXLUDED: HTTP-Alt traffic'
      break

   if len(http_alt_values) > 0:
      allowed_services.append('8080:8081')
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 8080:8081 -m state --state NEW -m recent --set -m limit --limit {2}/s --limit-burst 20 -j LOG --log-prefix "BIFROZT - HTTP-Alt: " --log-level 7'.format(network, cidr, http_alt_values))
      iptables_list.append('-A FORWARD -s {0}/{1} -o eth0 -p tcp -m tcp --dport 8081:8081 -m state --state NEW -m recent --update --seconds 1 --hitcount 20 -j DROP'.format(network, cidr))
      break

# Define the port list
if len(allowed_services) > 10:
   iptables_list.append('-A FORWARD -s {0}/{1} ! -d {0}/{1} -p tcp -m tcp -m multiport ! --dports {2} -j LOG --log-prefix "BIFROZT - FORWARD TCP DROP: " --log-level 7'.format(network, cidr, ','.join(allowed_services[0:9])))
   iptables_list.append('-A FORWARD -s {0}/{1} ! -d {0}/{1} -p tcp -m tcp -m multiport ! --dports {2} -j DROP'.format(network, cidr, ','.join(allowed_services[0:9])))
   iptables_list.append('-A FORWARD -s {0}/{1} ! -d {0}/{1} -p tcp -m tcp -m multiport ! --dports {2} -j LOG --log-prefix "BIFROZT - FORWARD TCP DROP: " --log-level 7'.format(network, cidr, ','.join(allowed_services[10:])))
   iptables_list.append('-A FORWARD -s {0}/{1} ! -d {0}/{1} -p tcp -m tcp -m multiport ! --dports {2} -j DROP'.format(network, cidr, ','.join(allowed_services[10:])))

if len(allowed_services) <= 10:
   iptables_list.append('-A FORWARD -s {0}/{1} ! -d {0}/{1} -p tcp -m tcp -m multiport ! --dports {2} -j LOG --log-prefix "BIFROZT - FORWARD TCP DROP: " --log-level 7'.format(network, cidr, ','.join(allowed_services)))
   iptables_list.append('-A FORWARD -s {0}/{1} ! -d {0}/{1} -p tcp -m tcp -m multiport ! --dports {2} -j DROP'.format(network, cidr, ','.join(allowed_services)))


# OUTPUT
iptables_list.append('-A OUTPUT -s 127.0.0.1/32 -j ACCEPT')
iptables_list.append('-A OUTPUT -o lo -j ACCEPT')
iptables_list.append('-A OUTPUT -s {0}/{1} -j ACCEPT'.format(network, cidr))
iptables_list.append('-A OUTPUT -o eth1 -j ACCEPT')
iptables_list.append('-A OUTPUT -o eth0 -j ACCEPT')
iptables_list.append('COMMIT')
#
#
#
# MANGLE
#
iptables_list.append('*mangle')
iptables_list.append(':PREROUTING ACCEPT [11555:635648]')
iptables_list.append(':INPUT ACCEPT [5541:383028]')
iptables_list.append(':FORWARD ACCEPT [6014:252620]')
iptables_list.append(':OUTPUT ACCEPT [1133:203218]')
iptables_list.append(':POSTROUTING ACCEPT [7147:455838]')
iptables_list.append('COMMIT')
#
#
#
# NAT
#
iptables_list.append('*nat')
iptables_list.append(':PREROUTING ACCEPT [3275:176962]')
iptables_list.append(':INPUT ACCEPT [297:45950]')
iptables_list.append(':OUTPUT ACCEPT [12:3424]')
iptables_list.append(':POSTROUTING ACCEPT [0:0]')
iptables_list.append('-A POSTROUTING -o eth0 -j MASQUERADE')
iptables_list.append('COMMIT')

for iptables in iptables_list:
   print iptables
