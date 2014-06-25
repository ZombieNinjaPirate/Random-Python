#!/usr/bin/env python


"""Checks if the malware has been conpressed with UPX. """

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
__version__ = '0.0.6'


#
#   DEVELOPMENT NOTES:
#   -- 140623 --
#   - implement elftools for further decoding
#   - search for hardcoded IP addresses in the decompressed binaries
#   - search for system paths and commands in the decompressed binraies
#


import argparse
import glob
import hashlib
import os
import re
import sys
import time
from os import path, access, R_OK


def parse_args():
    """Defines the command line arguments. """
    parser = argparse.ArgumentParser('Checks for UPX compressed binaries')
    
    local = parser.add_argument_group('- File locations')
    local.add_argument('-T', dest='tdir', help='Target directory', required=True)
    local.add_argument('-D', dest='ddir', help='Decompress directory (default: UPX_yymmdd_hhmmss)',
                        default=time.strftime('UPX_%y%m%d_%H%M%S'))

    decomp = parser.add_argument_group('- Decompress UPX')
    decomp.add_argument('-X', dest='deco', help='Decompress the UPX files', action='store_true')
    
    args = parser.parse_args()

    return args


def find_files(dirpath):
    """Adds any files within the given directory to the file_list. If the the file_list contains
    zero files it will call sys.exit(1) after printing and error message. """
    binary_files = []

    os.chdir(dirpath)
    for find in glob.glob('*'):
        if os.path.isfile(find):
            binary_files.append(find)

    if len(binary_files) == 0:
        print 'ERROR: No files found in {0}'.format(dirpath)
        sys.exit(1)

    return binary_files


def check_files(binary_list):
    """Check each indovidual file for strings indicating the use of UPX. The file names are appended
    to the upx_files list and returened when the funtion completes."""
    upx_files = []

    for binary in binary_list:        
        binary_lines = []

        with open(binary, 'rU') as upxtest:
            for upx in upxtest.readlines():
                if re.search('the UPX executable packer', upx):
                    if binary not in upx_files:
                        upx_files.append('{0}'.format(binary))
    
    return upx_files


def md5sum_upx(upx_list):
    """Appends thegenerated md5 hash of the files in the upx_list and returns them from the
    function"""
    fprint_list = []
    md5_dict = {}
    md5_uniqe = []
    fpl = []

    for upxfile in upx_list:
        upxhash = hashlib.md5(open(upxfile).read()).hexdigest()
        fprint_list.append('{1} {0}'.format(upxfile, upxhash))

    for fprint in fprint_list:
        if fprint.split()[0] not in md5_dict.keys():
            md5_dict[fprint.split()[0]]=''

    for key in md5_dict:
        for fprint in fprint_list:
            if key in fprint:
                fpl.append(fprint.split()[1])
            
        md5_dict[key] = fpl   
        fpl = []

    for key in md5_dict.keys():
        md5_uniqe.append(key)

    return md5_dict


def summary(tdir, allfiles, upxfiles, md5ofupx, fid):
    """Summarize the findings."""
    head = '-' * 50

    print head
    print 'Files analyzed: {0}'.format(len(allfiles))
    print 'UPX compressed: {0}'.format(len(upxfiles))

    fingerp = []

    for key in md5ofupx.keys():
        fingerp.append(key)

    print 'Unique UPX hash: {0}'.format(len(fingerp))
    print head,'\n'

    upxdecom_list = []

    for key, value in md5ofupx.items():
        print '- {0}:'.format(key)

        if sorted(value)[0] not in upxdecom_list:
                upxdecom_list.append(sorted(value)[0])
        
        for mfile in sorted(value):
            print mfile
        
        print ''

    print head

    if fid == 'decompress':
        return upxdecom_list


def decompress_upx(upx_list, dest_dir):
    """Decompress the UPX files. """
    head = '-' * 50

    if not os.path.isdir(dest_dir):
        os.mkdir(dest_dir)

    print '\n        File size         Ratio      Format      Name'
    print '   --------------------   ------   -----------   -----------'
    
    for upx in upx_list:
        dodecomp = '/usr/bin/upx -q -d {0} -o {1}/UPX-{0} | grep "<-"'.format(upx, dest_dir, upx)
        os.system(dodecomp)

    print '\n{0}'.format(head)


def process_args(args):
    """Process the command line arguments."""
    if args.tdir:
        if not os.path.isdir(args.tdir):
            print 'ERROR: {0} does not appear to exist!'.format(args.tdir)
            sys.exit(1)

    if not args.deco:
        allfiles = find_files(args.tdir)
        upxfiles = check_files(allfiles)
        md5ofupx = md5sum_upx(upxfiles)
        summary(args.tdir, allfiles, upxfiles, md5ofupx, 'summary')

    if args.deco:
        allfiles = find_files(args.tdir)
        upxfiles = check_files(allfiles)
        md5ofupx = md5sum_upx(upxfiles)
        decolist = summary(args.tdir, allfiles, upxfiles, md5ofupx, 'decompress')
        decompress_upx(decolist, args.ddir)



def main():
    """Do what Main does best."""
    args = parse_args()
    process_args(args)


if __name__ == '__main__':
    main()