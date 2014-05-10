#!/usr/bin/env python
# -*- coding: utf-8 -*-


"""
   Copyright (c) 2013, Are Hansen

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
__date__ = '2013, December 9'
__version__ = '1.0.4'


import argparse
import os
import time
import sys


def parse_args():
    """Defines the command line arguments. """
    parser = argparse.ArgumentParser('Builds a KVM from pre-defined templates.')
    kvm = parser.add_argument_group('- KVM options')
    kvm.add_argument('-N', dest='name', help='Name of KVM', required=True)
    kvm.add_argument('-I', dest='ip', help='KVM IP address', required=True)

    files = parser.add_argument_group('- Template file options')
    files.add_argument('-T', dest='template', help='Name of template', required=True)

    dest = parser.add_argument_group('- KVM destination location')
    dest.add_argument('-D', dest='dst', help='Full path to storage location', required=True)

    args = parser.parse_args()

    return args


def build_kvm(kvm_name, kvm_tmplt, kvm_dst, kvm_ip):
    """Builds the KVM. """
    kvm_dest = '{0}/{1}'.format(kvm_dst, kvm_name)
    template_bot = '{0}/boot.sh'.format(kvm_tmplt)
    template_cfg = '{0}/vmbuilder.cfg'.format(kvm_tmplt)
    template_prt = '{0}/vmbuilder.partitions'.format(kvm_tmplt)

    start = time.time()

    print '[-] - Checking KVM environment...'

    # Check if template directory exists
    if os.path.exists(kvm_tmplt) is not True:
        print '[!] - ERROR: {0} was not found!'.format(kvm_tmplt)
        sys.exit(1)

    # Check for vmbuilder.cfg
    if os.path.isfile(template_cfg) is not True:
        print '[!] - ERROR: Cant find {0}!!'.format(template_cfg)
        sys.exit(1)

    # Check for vmbuilder.partitons
    if os.path.isfile(template_prt) is not True:
        print '[!] - ERROR: Cant find {0}!!'.format(template_prt)
        sys.exit(1)

    # Check for boot.sh
    if os.path.isfile(template_bot) is not True:
        print '[!] - ERROR: Cant find {0}!!'.format(template_bot)
        sys.exit(1)

    # Check for if destination exists
    if os.path.exists(kvm_dst) is not True:
        print '[!] - ERROR: Cant find {0}!!'.format(kvm_dst)
        sys.exit(1)

    # Check if destination name for KVM is taken
    if os.path.exists(kvm_dest) is True:
        print '[!] - ERROR: The directory "{0}" already exists!!'.format(kvm_dest)
        sys.exit(1)

    print '[+] - Environment looks to be okay, lets try building this then...'

    vmbuilder = '/usr/bin/vmbuilder kvm ubuntu -o -v'
    kvm_cfigs = '-c {0} --part {1} --hostname {2} --ip {3} -d {4}'.format(template_cfg,
                                                                          template_prt,
                                                                          kvm_name,
                                                                          kvm_ip,
                                                                          kvm_dest)
    build_kvm = '{0} {1}'.format(vmbuilder, kvm_cfigs)
    try:
        os.system(build_kvm)
    except VMBuilder.exception, e:
	print 'ERROR: {0}'.format(e)
	sys.exit(1)

    end = time.time()
    build_time = end - start

    print '\n\n-------------------------------------------'
    print 'KVM name:        {0}'.format(kvm_name)
    print 'Using template:  {0}'.format(kvm_tmplt)
    print 'KVM destination: {0}'.format(kvm_dst)
    print 'KVM IP address:  {0}'.format(kvm_ip)
    print '-------------------------------------------'
    print 'KVM build time:  {0:.2f} min.'.format((build_time / 60.00))
    print '-------------------------------------------\n\n'
   

def process_args(args):
    """Process the command line arguments. """
    ip = args.ip
    dest = args.dst
    name = args.name
    template = args.template

    if os.getuid() == 0:
        build_kvm(name, template, dest, ip)
    elif os.getuid() != 0:
        print 'ERROR: You must be root to run this script!!'
        sys.exit(1)


def main():
    """Do what Main does best... """
    args = parse_args()
    process_args(args)


if __name__ == '__main__':
    main()
