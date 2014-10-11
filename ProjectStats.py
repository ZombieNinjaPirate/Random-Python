#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""PoC for getting download statistics for a project on SourceForge. """

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


#
#	DEVELOPMENT NOTES
#	- get rid of static values, the script should be able to accept dymanic values
#	- output to text file
#	- output in html format
#


__author__ = 'Are Hansen'
__date__ = '2014, 11 October'
__version__ = 'PoC - 0.0.0'


import json
import time
import urllib2


# Todays date
today = time.strftime("%Y-%m-%d")
# Base URL for geting stats
base = 'http://sourceforge.net/projects/bifrozt/files/stats/'
# Select the JSON formatted date range
date_span = 'json?start_date=2014-02-24&end_date={0}'.format(today)
# Compiled URL
json_url = '{0}{1}'.format(base, date_span)

# Request the JSON data from SourceForge
sf_response = urllib2.urlopen(json_url)

try:
	# Returned JSON data 
	sf_output = json.load(sf_response)
	# Formatted JSON output (for debugging only)
	sf_format = json.dumps(sf_output, sort_keys=True, indent=4)
	# Total downloads
	total_dls = sf_output['summaries']['time']['downloads']
	# Top 10 download countries
	count_one = sf_output['countries'][0]
	count_two = sf_output['countries'][1]
	count_tre = sf_output['countries'][2]
	count_for = sf_output['countries'][4]
	count_fiv = sf_output['countries'][5]
	count_six = sf_output['countries'][6]
	count_sev = sf_output['countries'][7]
	count_eig = sf_output['countries'][8]
	count_nin = sf_output['countries'][9]
	count_ten = sf_output['countries'][10]
except (ValueError, KeyError, TypeError):
	print "JSON format error"


# Format and output the results
print '''
	   Bifrozt download statistics
	   2014-02-24  <->  {0}
	=================================
	{3:<25} {4:>7}
	{5:<25} {6:>7}
	{7:<25} {8:>7}
	{9:<25} {10:>7}
	{11:<25} {12:>7}
	{13:<25} {14:>7}
	{15:<25} {16:>7}
	{17:<25} {18:>7}
	{19:<25} {20:>7}
	{21:<25} {22:>7}
	---------------------------------
	{1:<25} {2:>7}
	=================================
'''.format(today, 'Total downloads', total_dls, 
	       count_one[0], count_one[1], count_two[0], count_two[1], 
	       count_tre[0], count_tre[1], count_for[0], count_for[1], 
	       count_fiv[0], count_fiv[1], count_six[0], count_six[1], 
	       count_sev[0], count_sev[1], count_eig[0], count_eig[1], 
	       count_nin[0], count_nin[1], count_ten[0], count_ten[1])
