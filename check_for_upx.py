#!/usr/bin/env python


#
#     THIS CODE IS NOT COMPLETE !!!!
#

"""Preforms very simple static analyzis of malware binaries."""

"""
   Copyright (c) 2014, Are Hansen - Honeypot Development.

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
__date__ = '2014, June 23'
__version__ = '0.0.9'


#
#   DEVELOPMENT NOTES:
#   -- 140623 --
#   - implement elftools for further decoding
#   DONE - search for hardcoded IP addresses in the decompressed binaries
#   -- preform iplookup against found ipaddresSes (not RFC 1918)
#   - search for system paths and commands in the decompressed binraies
#   -- 140625 --
#   - change the script to be used on existing binaries without decompressing them
#   -- sould be possible to set arguments for analyzing single file or entire directory
#


import argparse
import glob
import hashlib
import operator
import os
import re
import sys
import time
from collections import defaultdict
from os import path, access, R_OK


def parse_args():
    """Defines the command line arguments. """
    parser = argparse.ArgumentParser(prog=sys.argv[0],
    formatter_class=argparse.RawDescriptionHelpFormatter, description=(
    '\n\t\tSimple static malware analyzis\n'
    '\nThis script has one required argument that must be given, -T or -F.\n'
    '-T is used to assign a target directory and -F to assign a target file.\n'
    'This will decompress any UPX files and preform some simple static analyzis\n'
    'on them. Using -T will examine every file within that directory, while -F\n'
    'can be used on a single file. If the script encounters a UPX compressed \n'
    'binary it will create a separate directory into which those files will\n'
    'be decompressed. When analyzing multiple binaries, the script will only\n'
    'analyze binaries with different hashes.\n').format(sys.argv[0].split('/')[-1]))
    
    local = parser.add_argument_group('- File/directory path')
    local.add_argument('-T', dest='tdir', help='Target directory')
    local.add_argument('-F', dest='mfile', help='(NOT READY) Target file')
    local.add_argument('-D', dest='ddir', help='Decompress directory (default: UPX_yymmdd_hhmmss)',
                        default=time.strftime('UPX_%y%m%d_%H%M%S'))
    
    args = parser.parse_args()

    return args


def find_files(dirpath, fid):
    """Adds any files within the given directory to the file_list. If the the file_list contains
    zero files it will call sys.exit(1) after printing and error message. """
    binary_files = []

    if fid == 'dir':
        os.chdir(dirpath)
        for find in glob.glob('*'):
            if os.path.isfile(find):
                binary_files.append(find)

        if len(binary_files) == 0:
            print 'ERROR: No files found in {0}'.format(dirpath)
            sys.exit(1)

    if fid == 'file':
        binary_files.append(dirpath)

    return binary_files


def check_files(binary_list):
    """Check each indovidual file for strings indicating the use of UPX. Any files that appears to be
    compressed with UPX is appended to the upx_files list, the remaining files are added to the
    noupx_files list before both lists are returned from the function as a single touple. """
    upx_files = []
    noupx_files = []

    for binary in binary_list:        
        binary_lines = []

        with open(binary, 'rU') as upxtest:
            for upx in upxtest.readlines():
                if re.search('the UPX executable packer', upx):
                    if binary not in upx_files:
                        upx_files.append('{0}'.format(binary))
 
    for binary in binary_list:
        if not re.search('the UPX executable packer', upx):
            if binary not in upx_files:
                noupx_files.append(binary)

    return upx_files, noupx_files


def md5sum_upx(upx_tuple):
    """Appends the generated md5 hash of the files in the upx_list and returns them from the
    function"""
    upx_list = []
    fprint_list_upx = []
    md5_dict_upx = {}
    md5_uniqe_upx = []
    fpl = []
    noupx_list = []
    nofprint_list = []
    nomd5_dict = {}
    md5_uniqe = []
    nofpl = []

    # Processing UPX files
    if len(upx_tuple[0]) != 0:
        for upx in upx_tuple[0]:
            upx_list.append(upx)

    for upxfile in upx_list:
        upxhash = hashlib.md5(open(upxfile).read()).hexdigest()
        fprint_list_upx.append('{1} {0}'.format(upxfile, upxhash))

    for fprint in fprint_list_upx:
        if fprint.split()[0] not in md5_dict_upx.keys():
            md5_dict_upx[fprint.split()[0]]=''

    for key in md5_dict_upx:
        for fprint in fprint_list_upx:
            if key in fprint:
                fpl.append(fprint.split()[1])
            
        md5_dict_upx[key] = fpl   
        fpl = []

    for key in md5_dict_upx.keys():
        md5_uniqe.append(key)

    # Processing non-UPX files
    if len(upx_tuple[1]) != 0:
        for upx in upx_tuple[1]:
            noupx_list.append(upx)

    for noupxfile in noupx_list:
        noupxhash = hashlib.md5(open(noupxfile).read()).hexdigest()
        nofprint_list.append('{1} {0}'.format(noupxfile, noupxhash))

    for nofprint in nofprint_list:
        if nofprint.split()[0] not in nomd5_dict.keys():
            nomd5_dict[nofprint.split()[0]]=''

    for key in nomd5_dict:
        for nofprint in nofprint_list:
            if key in nofprint:
                nofpl.append(nofprint.split()[1])
            
        nomd5_dict[key] = nofpl   
        nofpl = []

    for key in nomd5_dict.keys():
        md5_uniqe.append(key)

    return md5_dict_upx, nomd5_dict


def summary(allfiles, md5_tuple):
    """Summarize the findings."""
    head = '-' * 50

    print '{0} Summary'.format(head)
    print '\n{0:>8} - Total files'.format(len(allfiles))
    print '{0:>8} - Unique not UPX compressed files'.format(len(md5_tuple[1]))
    print '{0:>8} - Unique UPX compressed files'.format(len(md5_tuple[0]))
    print '{0:>8} - Total unique files'.format(len(md5_tuple[0]) + len(md5_tuple[1]))

    print '\n{0} Matching hash of UPX files\n'.format(head)

    upxdecom_list = []

    for key, value in md5_tuple[0].items():
        print '- {0}:'.format(key)

        if sorted(value)[0] not in upxdecom_list:
                upxdecom_list.append(sorted(value)[0])
        
        for mfile in sorted(value):
            print mfile
        print ''

    print '\n{0} Matching hash of files\n'.format(head)

    noupx_list = []

    for key, value in md5_tuple[1].items():
        print '- {0}:'.format(key)

        if sorted(value)[0] not in noupx_list:
                noupx_list.append(sorted(value)[0])
        
        for mfile in sorted(value):
            print mfile
        print ''

    return upxdecom_list, noupx_list


def decompress_upx(upx_tuple_list, dest_dir):
    """Decompress the UPX files. Appends them to the binary_upx list thats returned for generating
    md5 hashes of the decompressed files."""
    binary_dict = {}
    head = '-' * 50

    if len(upx_tuple_list[0]) != 0:
        if not os.path.isdir(dest_dir):
            os.mkdir(dest_dir)
        
        for upx in upx_tuple_list[0]:
            dodecomp = '/usr/bin/upx -q -d {0} -o {1}/UPX-{0} >/dev/null'.format(upx, dest_dir, upx)
            os.system(dodecomp)

        os.chdir(dest_dir)
        for find in glob.glob('*'):
            if os.path.isfile(find):
                dec_hash = hashlib.md5(open(find).read()).hexdigest()
                binary_dict[dec_hash] = find

        return binary_dict, upx_tuple_list[1]

    if len(upx_tuple_list[0]) == 0:
        return upx_tuple_list[0], upx_tuple_list[1]


def decompress_summary(decupx_tuple):
    """Print a summary of the deompressed files."""
    head = '-' * 50

    decupx_list = []

    print '{0} Decompressed UPX hashes\n'.format(head)

    for key, value in decupx_tuple[0].items():
        print '- {0}:\n{1}\n'.format(key, value)
        decupx_list.append(value)

    return decupx_list, decupx_tuple[1]


def decomp_get_ipadds(check_tuple, tdir):
    """"Search the binary files in the check_list for IP addresses. """
    head = '-' * 50
    ipadd_dict_upx = {}
    ipadd_list_upx = []
    noipadd_dict = {}
    noipadd_list = []
    ipadd_total = []
    origin_total = []
    
    pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
    pattern_re = re.compile(pattern)

    print '{0} IP addresses found (UPX decompressed)\n'.format(head)

    for check in check_tuple[0]:
        with open(check, 'rU') as bfile:
            for ipaddline in bfile.readlines():
                if pattern_re.findall(ipaddline):
                    for ipadd in pattern_re.findall(ipaddline):
                        ipadd_list_upx.append(ipadd)

        if len(ipadd_list_upx) != 0:
            print '- {0} contained {1} IP addresses'.format(check, len(ipadd_list_upx))
            for ipaddress in sorted(ipadd_list_upx):
                print ipaddress
                ipadd_total.append(ipaddress)
            print '\n'

        ipadd_list_upx = []

    print '{0} IP addresses found\n'.format(head)

    os.chdir('../')
    for check in check_tuple[1]:
        with open(check, 'rU') as bfile:
            for ipaddline in bfile.readlines():
                if pattern_re.findall(ipaddline):
                    for ipadd in pattern_re.findall(ipaddline):
                        noipadd_list.append(ipadd)

        if len(noipadd_list) != 0:
            print '- {0} contained {1} IP addresses'.format(check, len(noipadd_list))
            for ipaddress in sorted(noipadd_list):
                print ipaddress
                ipadd_total.append(ipaddress)
            print '\n'

        noipadd_list = []

    #
    #   DEVELOPMENT NOTES
    #
    #   This might have to go. I should prolly do somehting better with this entire function.
    #
    counts = defaultdict(int)

    for ips in ipadd_total:
        counts[ips] += 1

    print '{0} Occurences of IP addresses\n'.format(head)

    for key, value in sorted(counts.iteritems(), key=operator.itemgetter(1), reverse=True):
        print '{0:>4} {1}'.format(value, key)
        origin_total.append(key)


def process_args(args):
    """Process the command line arguments."""

    if args.tdir:
        if not os.path.isdir(args.tdir):
            print 'ERROR: {0} does not appear to exist!'.format(args.tdir)
            sys.exit(1)

        allfiles = find_files(args.tdir, 'dir')
        upxfiles = check_files(allfiles)
        md5ofupx = md5sum_upx(upxfiles)
        decolist = summary(allfiles, md5ofupx)
        expalist = decompress_upx(decolist, args.ddir)
        decommd5 = decompress_summary(expalist)
        decomp_get_ipadds(decommd5, args.tdir) 

def main():
    """Do what Main does best."""
    args = parse_args()
    process_args(args)


if __name__ == '__main__':
    if len(sys.argv) == 1:
        print 'USAGE: {0} -h'.format(sys.argv[0].split('/')[-1])
        sys.exit(1)
    main()
