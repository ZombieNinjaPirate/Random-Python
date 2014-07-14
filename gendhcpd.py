#!/usr/bin/env python


"""Generate the dhcpd.conf file. """


#
#   DEVELOPMENT NOTES:
#   - assign static IP's by MAC address
#       - verify MAC address validity
#       - assign multiple static IP's
#   - output in dhcpd.conf format
#   - wait for user to confirm configuration
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
__version__ = '0.0.2'


import sys
try:
    import ipaddr
except ImportError:
    print '\nERROR: You need the module called "ipaddr"!\n'
    sys.exit(1)


def check_ipv4():
    """Verifies that the ipv4 is valid. """
    while True:
        ipcidr = raw_input('Enter IPv4/CIDR: ' )
        ipv4 = ipcidr.split('/')[0]
        cidr = ipcidr.split('/')[1]
        try:
            ip = ipaddr.IPAddress(ipv4)
            break
        except ValueError:
            print '[!] - IPv4 {0} is not valid!'.format(ipv4)

    return ipv4, cidr


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

    print 'Network:   {0}'.format('.'.join(map(str, net)))
    print 'Gateway:   {0}.1'.format('.'.join(map(str, net[0:3])))
    print 'First IP:  {0}.2'.format('.'.join(map(str, net[0:3])))
    print 'Last IP:   {0}.{1}'.format('.'.join(map(str, broad[0:3])), int(broad[3]) - 1)
    print 'Broadcast: {0}'.format('.'.join(map(str, broad)))
    print 'Netmask:   {0}'.format('.'.join(map(str, mask)))


def main():
    """...main..."""
    ipv4 = check_ipv4()
    network_summary(ipv4)


if __name__ == '__main__':
    main()
