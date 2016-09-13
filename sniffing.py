#!/usr/bin/python2.7


__author__ = 'Are Hansen'
__credits__ = 'Thomas Nicholson'
__date__ = '2016, September 13'
__version__ = '0.0.2-POC'


import binascii
import re
import socket
import sys


ip_num = 0
s = socket.socket(socket.AF_PACKET, socket.SOCK_RAW, socket.ntohs(0x0003))
s.bind((sys.argv[1], 0))


while True:
    packet = s.recvfrom(65565)
    packet = packet[0]
    dst_mac = packet[0:6]
    src_mac = packet[6:12]
    ether_type = packet[12:14]
    everything_else = packet[14:]

    if ether_type == '\x08\x00' and ip_num < 1:
        if 'GET' in everything_else:
            pull_get = re.search(r'(GET\s\/.+)', repr(everything_else))
            get_req = pull_get.group().replace(r'\r', '').replace(r'\n', '\n')
            print 'GET request found!'
            print '- Destination MAC: {0}'.format(binascii.b2a_hex(dst_mac))
            print '- Source MAC: {0}'.format(binascii.b2a_hex(src_mac))
            print '- Ether type: {0}'.format(binascii.b2a_hex(ether_type))
            #print '- Everything else: {0}'.format(repr(everything_else))
            print '- Request: {0}'.format(get_req)
            ip_num = ip_num + 1

    if ip_num == 1:
        break

