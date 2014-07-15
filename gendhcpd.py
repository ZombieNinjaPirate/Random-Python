#!/usr/bin/env python3


"""Generate the dhcpd.conf file. """


#
#   DEVELOPMENT NOTES:
#   - assign DNS
#   - assign domain name
#   - show default values, let user accept or change
#      - assign default lease
#      - assign max lease time 
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


def check_ipv4(ip_list):
    """Checks for valid ipv4 addresses. The ip_list should be of len 2. The first index should be
    a CIDR formatted IP address. The second index should be one or more ipv4 adresses that will be
    used as DNS servers. The function will extract the plain ipv4 addresses and itterate over them.
    In the event of one, or more, ipv4 addresses being flagged as invalid the user will be forced to
    enter that IP address once more. When the function has verified that all ipv4 addresses are
    valid they are returned from the function in the valid_ip list after the CIDR has been appended
    as the last index of that list."""
    # Separate IPv4 and CIDR and add the IPv4 address to the ip_check list
    ipv4 = ip_list[0].split('/')[0]
    cidr = ip_list[0].split('/')[1]
    ip_check = [ipv4]

    # Itterate trough the IPv4 addresses in ip_list[1] and appends them to the ip_check list.
    for dns in ip_list[1].split(' '):
        ip_check.append(dns)

    count = 0
    while count < len(ip_check):
        for check in ip_check:
            try:
                ip = ipaddr.ip_address(check)
                count = count + 1
            except ValueError:
                # If ValueError is raised
                print '[!] - IPv4 {0} is not valid!'.format(check)
                # Request a valid IPv4 address from the user
                newip = raw_input('Enter valid IP: ')
                # and replace the old value with the new IPv4 address before running the loop again
                ip_check[ip_check.index(check)] = newip
                count = 0

    print ip_check


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

def main():
    """...main..."""
    ipcidr = raw_input('Enter IPv4/CIDR: ')
    dnssrv = raw_input('Enter DNS server(s): ')
    ipv4 = check_ipv4([ipcidr, dnssrv])
    #network_summary(ipv4)


if __name__ == '__main__':
    main()
