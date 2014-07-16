#!/usr/bin/env python3


"""Generate the dhcpd.conf file. """


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
__date__ = '2014, July 14'
__version__ = '0.0.7'


import os
import sys
import re
try:
    import ipaddr
except ImportError:
    print '\nERROR: You need the module called "ipaddr"!\n'
    sys.exit(1)


def assign_values():
    """Assign DHCP values. """
    print '\nNetwork configuration\n'
    while True:
        ipcidr = raw_input('- Enter IPv4/CIDR: ')
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

    print '\nDNS Servers:'
    print 'Multiple DNS servers as space separated list'
    dnssrv = raw_input('- Enter DNS server(s): ')

    # Append the DNS server(s) to the check list
    for dns in dnssrv.split(' '):
        check_ips.append(dns)

    valid_ip = []
    # Pass the elements in the check list off for validation
    for ips in check_ips:
        validip = check_ipv4(ips)
        # Append the returned IPv4 address to the valid_ip list 
        valid_ip.append(validip)

    # Show default lease times.
    print '\nDHCP lease settings:'
    print 'Default values:'
    print 'default-lease-time:  600'
    print 'max-lease-time:     7200'
    print 'Press ENTER to keep default settings.\n'

    # Get default-lease-time
    dltime = raw_input('- Default lease time: ')

    if len(dltime) == 0:
        dltime = '600'

    # Get max-lease-time
    mltime = raw_input('- Max lease time: ')

    if len(mltime) == 0:
        mltime = '7200'

    # Get domain-name.
    while True:
        dname = raw_input('- Domain name: ')

        if len(dname) < 2:
            print 'You have to enter a longer doamin name!'

        if len(dname) >= 2:
            break

    staticip = []
    # Get static IPv4 and MAC address
    print '\nStatic IPv4 addresse(s):'
    while True:
        # Get static IPv4 address,
        host_ip = raw_input('- IPv4: ')
        # validate IPv4.
        valid_host_ip = check_ipv4(host_ip) 

        # Get MAC address of static host,
        host_mac = raw_input('- MAC: ')
        # validate MAC address.
        valid_host_mac = check_mac(host_mac)

        # Get host name of static host
        valid_host_name = ''
        while True:
            host_name = raw_input('- Host name: ')

            if len(host_name) < 3:
                print 'The host name must be longer!'

            if len(host_name) >= 3:
                valid_host_name = host_name
                break

        #
        #   CHECK FOR PREVIOUSLY USED IP AND MAC ADDRESSES
        #
        staticip.append('{0} {1} {2}'.format(valid_host_ip, valid_host_mac, valid_host_name))

        print staticip
        verify = raw_input('\nAdd another static IPv4 address? Y/N ')

        if verify == 'Y':
            pass

        if verify == 'N':
            break

        if verify != 'Y' and verify != 'N':
            print 'Please enter "Y" for Yes or "N" for No'

    return valid_ip, cidr, dltime, mltime, dname, staticip


def check_mac(macadd):
    """Check for valid MAC address. """
    while True:
        if not re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", macadd.lower()):
            print 'MAC address "{0}" is not valid!'.format(macadd)
            macadd = raw_input('- MAC: ')

        if re.match("[0-9a-f]{2}([-:])[0-9a-f]{2}(\\1[0-9a-f]{2}){4}$", macadd.lower()):
            break

    return macadd


def check_ipv4(ipv4):
    """Checks for valid ipv4 addresses. """
    while True:
        try:
            ip = ipaddr.ip_address(ipv4)
            break
        except ValueError:
            print '[!] - IPv4 {0} is not valid!'.format(ipv4)
            ipv4 = raw_input('Enter a valid IPv4: ')

    return ipv4


def network_summary(dhcp_info):
    """ Processes the tuple thats returned from the assign_values function. The tuple contain six
    elements. This is a reference of those elements:

    dhcp_info[0]
        - valid_ip
          Type: list
          - 0: network
          - 1 - * : DNS servers

    dhcp_info[1]
        - cidr
          Type: str
          - CIDR of the network

    dhcp_info[2]
        - dltime
          Type: str
          - default-lease-time

    dhcp_info[3]
        - mltime
          Type: str
          - max-lease-time

    dhcp_info[4]
        - dname
          Type: str
          - domain-name

    dhcp_info[5]
        - staticip
          Type: list
          - each element contains three strings separated by a space
          -- str0: ipv4 address
          -- str1: mac address
          -- str2: host name
    """
    addr = dhcp_info[0][0].split('.')
    cidr = int(dhcp_info[1])

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

    print '\nDHCP range:'
    print 'Starting IP address: {0}'.format(firstip)
    print 'Ending IP address:   {0}\n'.format(finalip)
    # Get start range
    startrange = raw_input('- Enter starting IP address: ')
    # and make sure its a valid IPv4 address.
    valid_start = check_ipv4(startrange)

    # Get end range
    endrange = raw_input('- Enter ending IP address: ')
    # and make sure its a valid IPv4 address.
    valid_end = check_ipv4(endrange)

    # Append all the configuration details to the dhcpd_conf list.
    dhcpd_conf = []
    dhcpd_conf.append('authoritative;')
    dhcpd_conf.append('ddns-update-style none;')
    dhcpd_conf.append('log-facility local7;')
    dhcpd_conf.append('default-lease-time {0};'.format(dhcp_info[2]))
    dhcpd_conf.append('max-lease-time {0};\n'.format(dhcp_info[3]))
    dhcpd_conf.append('option domain-name "{0}";'.format(dhcp_info[4]))
    dhcpd_conf.append('option domain-name-servers {0};'.format(', '.join(dhcp_info[0][1:])))
    dhcpd_conf.append('option subnet-mask {0};'.format(netmask))
    dhcpd_conf.append('option broadcast-address {0};'.format(brdcast))
    dhcpd_conf.append('option routers {0};\n'.format(gateway))
    dhcpd_conf.append('subnet {0} netmask {1} {2}'.format(network, netmask, '{'))
    dhcpd_conf.append('\trange {0} {1};\n'.format(valid_start, valid_end))

    for static in dhcp_info[5]:
        ipaddress = static.split(' ')[0]
        macaddres = static.split(' ')[1]
        hostname = static.split(' ')[2]
        dhcpd_conf.append('\thost {0}.{1} {2}'.format(hostname, dhcp_info[4], '{'))
        dhcpd_conf.append('\thardware ethernet {0};'.format(macaddres))
        dhcpd_conf.append('\tfixed-address {0};'.format(ipaddress))
        dhcpd_conf.append('\t{0}\n'.format('}'))
    
    dhcpd_conf.append('{0}\n'.format('}'))

    print '\nThis is what your new dhcpd.conf will look like:\n'

    for line in dhcpd_conf:
        print line

    while True:
        verify = raw_input('\nIs this the correct network settings? Y/N ')

        if verify == 'Y':
            break

        if verify == 'N':
            python = sys.executable
            os.execl(python, python, * sys.argv)

        if verify != 'Y' and verify != 'N':
            print 'Please enter "Y" for Yes or "N" for No'

    return dhcpd_conf


def write_dhcpd(dhcpd_values):
    """Writes the assigned values to the new dhcpd.conf. """
    dhcpd_file = 'dhcpd.config.NEW'
    for values in dhcpd_values:
        with open(dhcpd_file, 'a') as config:
            config.write('{0}\n'.format(values))


def main():
    """...main..."""
    info = assign_values()
    dhcpd_config = network_summary(info)
    write_dhcpd(dhcpd_config)


if __name__ == '__main__':
    main()
