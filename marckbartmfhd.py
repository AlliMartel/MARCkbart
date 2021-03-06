#!/usr/bin/env python

import csv
from pymarc import MARCReader
import os
import shutil
import zipfile
import re
from os import listdir
from re import search

# change the source directory to whatever directory your .mrc files are in
SRC_DIR = 'marc/'

# get a list of all .mrc files in source directory
file_list = filter(lambda x: search('.mrc', x), listdir(SRC_DIR))

#create tab delimited text file that only quotes fields if there is a special character present in the field
csv_out = csv.writer(open('kbart.txt', 'w'), delimiter = '\t', quotechar = '"', quoting = csv.QUOTE_MINIMAL)

#create the header row
csv_out.writerow(['publication_title', 'print_identifier', 'online_identifier', 'date_first_issue_online', 'num_first_vol_online', 'num_first_issue_online', 'date_last_issue_online', 'num_last_vol_online', 'num_last_issue_online', 'title_url', 'first_author', 'title_id', 'embargo_info', 'coverage_depth', 'coverage_notes', 'publisher_name', 'location', 'title_notes', 'staff_notes', 'vendor_id', 'oclc_collection_name', 'oclc_collection_id', 'oclc_entry_id', 'oclc_linkscheme', 'oclc_number', 'ACTION','rectype'])

#define the MARC fields to use for each element and parse them     
for item in file_list:
  fd = file(SRC_DIR + '/' + item, 'r')
  reader = MARCReader(fd)
  for record in reader:
    publication_title = print_identifier = online_identifier = date_first_issue_online = num_first_vol_online = num_first_issue_online = date_last_issue_online = num_last_vol_online = num_last_issue_online = title_url = first_author = title_id = embargo_info = coverage_depth = coverage_notes = publisher_name = location = title_notes = staff_notes = vendor_id = oclc_collection_name = oclc_collection_id = oclc_entry_id = oclc_linkscheme = oclc_number = ACTION = rectype = ''

    # publication_title
    if record['245'] is not None:
      rectype = "bib"
      if record['245']['a'] is not None:
        publication_title = record['245']['a'].rsplit('/', 1)[0]
      if record['245']['b'] is not None:
        publication_title = publication_title + " " + record['245']['b']
    
    # print_identifier
    if record['020'] is not None:
      if record['020']['z'] is not None:
        print_identifier = record ['020']['z'].rsplit('(', 1)[0]
        if record['020']['a'] is not None:
          print_identifier = record['020']['a'].rsplit('(', 1)[0] 
    elif record['022'] is not None:
      if record['022']['y'] is not None:
        print_identifier = record['022']['y'].rsplit('(', 1)[0]
        if record['022']['a'] is not None:
          print_identifier = record['022']['a'].rsplit('(', 1)[0]
      
    # online_identifier
    if record['020'] is not None:
      online_identifier = record['020']['a'].rsplit('(', 1)[0]
    elif record['022'] is not None:
      if '(' in record ['022']:
        online_identifier = record['022']['a'].rsplit('(', 1)[0] 
      else:
        online_identifier = record['022']['a']
    
    # date_first_issue_online
    if record ['866'] is not None:
      date_first_issue_online = record['866']['a'].rsplit('-', 1)[0]
      if '(' in date_first_issue_online:
        date_first_issue_online = date_first_issue_online.rsplit('(',1)[-1][:4]
    
    # num_first_vol_online
    if record['866'] is not None:
      #if 'v' in record ['866']['a']:
      num_first_vol_online = record['866']['a']
      if 'v.' in num_first_vol_online:
        num_first_vol_online = num_first_vol_online.split('v.', 1)[1]
        for match in re.findall('\d+', num_first_vol_online):
          num_first_vol_online = re.findall('\d+', num_first_vol_online)[0]
    elif record ['863'] is not None:
      if '-' in record ['863']:
        num_first_vol_online = record['863']['a'].rsplit('-', 1)[0]
      else:
        num_first_vol_online = record['863']['a'] 
        
    # num_first_issue_online
    num_first_issue_online = ''
    
    # date_last_issue_online
    if record ['866'] is not None:
      date_last_issue_online = record['866']['a'].rsplit('-', 1)[-1][:4]
    
    # num_last_vol_online
    if record['866'] is not None:
      num_last_vol_online = record['866']['a']
      if '-v.' in num_last_vol_online:
        num_last_vol_online = num_last_vol_online.split('-v.', 1)[1]
        for match in re.findall('\d+', num_last_vol_online):
          num_last_vol_online = re.findall('\d+', num_last_vol_online)[0]
      elif '-' in num_last_vol_online:
        num_last_vol_online = num_last_vol_online.split('-', 1)[1]
        for match in re.findall('\d+', num_last_vol_online):
          num_last_vol_online = re.findall('\d+', num_last_vol_online)[0]
      else:
        num_last_vol_online = ''
    elif record ['863'] is not None:
      if '-' in record ['863']:
        num_last_vol_online = record['863']['a'].rsplit('-', 1)[-1]
      else:
        num_last_vol_online = record['863']['a']
    
    # num_last_issue_online
    num_last_issue_online = ''
    
    #title_url
    if record ['856'] is not None:
      title_url = record['856']['u']
     
    # determine first_author for ebooks
    if record['100'] is not None:
      first_author = record['100']['a']
    elif record['110'] is not None:
      first_author = record['110']['a']
    elif record['700'] is not None:
      first_author = record['700']['a']
    elif record['710'] is not None:
      first_author = record['710']['a']
      
    #titleid
    title_id = ''
    
    #embargoinfo
    embargo_info = ''
    
    #coverage_depth (options fulltext, ebook, print)
    if record['856'] is not None:
      coverage_depth = ('fulltext')
    else: 
      coverage_depth = ('print')
    
    #coverage_notes (e.g., graphics excluded)
    if record['866'] is not None:
      coverage_notes = record['866']['a']
    
    # publisher
    if record['260'] is not None:
      publisher_name = record['260']['b']
    
    #location (shelving location, collection, or available online)
    if record['852'] is not None:
      if record['852']['b'] is not None:
        location = record['852']['b']
        if record['852']['c'] is not None:
          location = record['852']['b'] + " " + record['852']['c']
          if record['852']['h'] is not None:
            location = record['852']['b'] + " " + record['852']['c'] + " " + record['852']['h']
            if record['852']['i'] is not None:
              location = record['852']['b'] + " " + record['852']['c'] + " " + record['852']['h'] + " " + record ['852']['i']

    #title_notes
    if record['852'] is not None:
      title_notes = record['852']['z']
    
    #oclc_collection_name
    oclc_collection_name = ''
    
    #staff_notes
    staff_notes = ''
    
    #vendor_id
    vendor_id = ''
    
    #oclc_collection_id
    oclc_collection_id = ''
    
    #oclc_entry_id
    oclc_entry_id = ''
    
    #oclc_linkscheme
    oclc_linkscheme = ''

    if record['035'] is not None:
      if record['035']['a'] is not None:
        oclc_number = record['035']['a']
        if oclc_number.find("OCoLC") >= 0:
          oclc_number = oclc_number.replace('(OCoLC)', '')
          oclc_number = oclc_number
        else:
          oclc_number = ''
      else:
       oclc_number = ''
    elif record['004'] is not None:
      oclc_number = record['004']
      oclc_number = str(oclc_number)
      oclc_number = oclc_number.replace('=004  ocm', '')
      oclc_number = oclc_number.replace('\\', '')
    else:
      oclc_number = ''
       
    #action
    action = ('RAW')
    
    #write each row   
    csv_out.writerow([publication_title, print_identifier, online_identifier, date_first_issue_online, num_first_vol_online, num_first_issue_online, date_last_issue_online, num_last_vol_online, num_last_issue_online, title_url, first_author, title_id, embargo_info, coverage_depth, coverage_notes, publisher_name, location, title_notes, staff_notes, vendor_id, oclc_collection_name, oclc_collection_id, oclc_entry_id, oclc_linkscheme, oclc_number, action, rectype])
  fd.close()

#copy files to a web directory
#shutil.copy2(filematch, config.destination)
#shutil.copy2('sorted' + str(yesterday) + '.txt', config.destination)

#Zip the file
#zf = zipfile.ZipFile('sorted.zip', "w", zipfile.ZIP_DEFLATED)
#zf.write('sorted' + str(yesterday) + '.txt')
#zf.close()