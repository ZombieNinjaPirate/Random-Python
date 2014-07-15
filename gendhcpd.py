#!/usr/bin/env python3


"""Generate the dhcpd.conf file. """


#
#   DEVELOPMENT NOTES:
#   - assign domain name
#   - assign DHCP range by start and end IP ||
#     assign DHCP range by number of hosts
#   - assign static IP's by MAC address
#       - assign host name
#       - verify MAC address validity
#       - assign multiple static IP's
#   - output in dhcpd.conf format
#   - if user confirms configuration
#   - write output to file
#


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
__date__ = '2014, July 14'
__version__ = '0.0.4'


import sys
import os
try:
    import ipaddr
except ImportError:
    print '\nERROR: You need the module called "ipaddr"!\n'
    sys.exit(1)

"""
authoritative;
ddns-update-style none;
log-facility local7;
default-lease-time 600;
max-lease-time 7200;

option domain-name "internal";
option domain-name-servers 8.8.8.8;
option subnet-mask 255.255.255.0;
option broadcast-address 10.199.115.255;
option routers 10.199.115.1;

subnet 10.199.115.0 netmask 255.255.255.0 {
    range 10.199.115.2 10.199.115.250;

    host microcloud-sshsrv028 {
       hardware ethernet 00:11:22:33:44:55;
       fixed-address 10.199.115.154;
       }

}
"""
def assign_calues():
    """Assign DHCP values. """
    valid_ip = []

    while True:
        ipcidr = raw_input('Enter IPv4/CIDR: ')
        ipv4 = ipcidr.split('/')[0]
        cidr = ipcidr.split('/')[1]

        # CIDR cannot be greater than 31
        if int(cidr) > 31:
            print 'The CIDR can not be higher than 31'

        # CIDR is less or equal to 31
        if int(cidr) <= 31:
            break

    # Setup the IPv4 address for validation
    check_ips = [ipv4]

    dnssrv = raw_input('Enter DNS server(s): ')

    # Append the DNS server(s) to the check list
    for dns in dnssrv.split(' '):
        check_ips.append(dns)

    # Pass the elements in the check list off for validation
    for ips in check_ips:
        validip = check_ipv4(ips)
        # Append the returned IPv4 address to the valid_ip list 
        valid_ip.append(validip)

    # Get the default-lease-time
    print '\nDHCP lease settings:'
    print 'Default values:'
    print '- default-lease-time:  600'
    print '- max-lease-time:     7200\n'
    print 'Press ENTER to keep default settings.\n'

    dltime = raw_input('Default lease time: ')

    if dltime == '':
        dltime = '600'

    mltime = raw_input('Max lease time: ')

    if mltime == '':
        mltime = '7200'

    print valid_ip, cidr, dltime, mltime


def check_ipv4(ipv4):
    """Checks for valid ipv4 addresses. """
    while True:
        try:
            ip = ipaddr.ip_address(ipv4)
            break
            #count = count + 1
        except ValueError:
            print '[!] - IPv4 {0} is not valid!'.format(ipv4)
            ipv4 = raw_input('Enter a valid IPv4: ')

    return ipv4


def network_summary(ipcidr):
    """Calculate gateway, netmask, network and broadcast. """
    addr = ipcidr[0].split('.')
    cidr = int(ipcidr[1])

    mask = [0, 0, 0, 0]
    for i in range(cidr):
        mask[i/8] = mask[i/8] + (1 << (7 - i % 8))

    net = []
    for i in range(4):
        net.append(int(addr[i]) & mask[i])

    broad = list(net)
    brange = 32 - cidr
    for i in range(brange):
        broad[3 - i/8] = broad[3 - i/8] + (1 << (i % 8))

    network = '.'.join(map(str, net))
    gateway = '{0}.1'.format('.'.join(map(str, net[0:3])))
    firstip = '{0}.2'.format('.'.join(map(str, net[0:3])))
    finalip = '{0}.{1}'.format('.'.join(map(str, broad[0:3])), int(broad[3]) - 1)
    brdcast = '{0}'.format('.'.join(map(str, broad)))
    netmask = '{0}'.format('.'.join(map(str, mask)))

    print 'Network:   {0}'.format(network)
    print 'Gateway:   {0}'.format(gateway)
    print 'First IP:  {0}'.format(firstip)
    print 'Last IP:   {0}'.format(finalip)
    print 'Broadcast: {0}'.format(brdcast)
    print 'Netmask:   {0}'.format(netmask)

    while True:
        verify = raw_input('\nIs this the correct network settings? Y/N ')

        if verify == 'Y':
            netsum = [network, gateway, firstip, finalip, brdcast, netmask]
            break

        if verify == 'N':
            python = sys.executable
            os.execl(python, python, * sys.argv)

        if verify != 'Y' and verify != 'N':
            print 'Please enter "Y" for Yes or "N" for No'

    return netsum


def main():
    """...main..."""
    assign_calues()


if __name__ == '__main__':
    main()
