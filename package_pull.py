#!/usr/bin/env python
#-*-coding:utf-8-*-
import config_options as conf
import os
from optparse import OptionParser
import sys
import sqlite3
import requests
import util as u

parser = OptionParser()
parser.add_option('-d', '--dry_run', action='store_true', dest='dryrun', default=False, help='Only list what will happen')
parser.add_option('-v', '--verbose', action='store_true', dest='verbose', default=False, help='Verbose debugging output')

(options, args) = parser.parse_args()
dryrun = options.dryrun
verbose = options.verbose

conn = sqlite3.connect(conf.sqlitepath)#Store package hashes and any other data (later)
if(verbose):
    print(u'Creating data table if it does not exist')
conn.execute('CREATE TABLE IF NOT EXISTS package_hash (id INTEGER PRIMARY KEY, sha1hash VARCHAR(1000), jobname VARCHAR(1000))')

#pull json api for build host
data = requests.get(conf.url, verify=True).json()


print(u'Fetching jobs')
jobnames = {}
for job in data['jobs']:
    match = conf.package_regex.match(job['name'])
    if(match):
        jobnames[job['name']] = match

if jobnames:
    print(u'Matched jobs found')

else:
    print(u'No package jobs found, aborting')
    sys.exit(1)

if dryrun:
    print(u'Dry Run only, no files will be downloaded')

for job in jobnames:
    file_paths = u.fetch_job_file_paths(job, jobnames)
    match = jobnames[job]
    for filename, url in file_paths:
        print(u'Downloading file {0}'.format(filename))
        path = u.get_final_path(job, match, filename)
        u.download_file(url, path)
        #Hash file, if it has not changed sha1 hash for this job, we unlink it so it won't be updated by the rest of the script
        hash = u.hash_file(path)
        if u.same_hash(filename, hash, conn):
            print(u'==> File not changed since last run, skipping')
            os.remove(path)
            continue
        elif not dryrun:#as long as we are not a dry run, update the hash
            if not u.update_hash(filename, hash, conn):
                print(u'==> Could not save hash, deleting file')
                os.remove(path)
                continue
        else:
            #always remove file in dryrun
            os.remove(path)
