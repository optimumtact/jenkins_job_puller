import config_options as conf
import hashlib
import os
import requests
import re
import sys

#Utility functions
def get_final_path(job, match, filename):
    buildtype = match.group('buildtype')
    if buildtype in conf.buildtype_mapping:
        buildtype = conf.buildtype_mapping[buildtype]

    else:
        buildtype = conf.buildtype_mapping['default']

    release = match.group('release')
    if release in conf.release_mapping:
        release = conf.release_mapping[release]

    else:
        release = conf.release_mapping['default']

    final_path = conf.ship_directory.format(release,buildtype,filename)
    path_check = conf.ship_directory.format(release,buildtype,'')

    #Normalise the final path and determine it is still in the correct 
    #location (detect tree walking with .. and .) This works because we know 
    #they cannot forge the release/buildtype values as they are mappings, 
    #the normpath normalises ../../ trickery to the final path then we simply
    #compare the final path is still starting in the expected location
    if os.path.normpath(final_path).startswith(path_check):
        return final_path

    else:
        print(u'Naughty filename detected {0}, filecheck {1}'.format(final_path, path_check))
        sys.exit(2)

def download_file(url,filename):
    #if verbose:
    #    print(u'==> Downloading File: {0} URL:{1}'.format(filename, url))
    r = requests.get(url, verify=True, stream=True)
    with open(filename, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk: # filter out keep-alive new chunks
                f.write(chunk)


def hash_file(filename):
   """This function returns the SHA-1 hash
   of the file passed into it"""

   # make a hash object
   h = hashlib.sha1()

   # open file for reading in binary mode
   with open(filename,'rb') as file:

       # loop till the end of the file
       chunk = 0
       while chunk != b'':
           # read only 1024 bytes at a time
           chunk = file.read(1024)
           h.update(chunk)

   # return the hex representation of digest
   return h.hexdigest()

def same_hash(job, hash, cursor):
    if(not job_hash_exists(job, cursor)):
        return False #no job with that name (must not have seen it before)
    try:
        with cursor:
            result = cursor.execute('SELECT sha1hash FROM package_hash WHERE jobname = ?', (job,))
            storedhash = result.fetchone()[0]
            if hash == storedhash:
                return True
            else:
                return False
    except sqlite3.Error:
        return False

def job_hash_exists(job, cursor):
    try:
        with cursor:
            result = cursor.execute('SELECT sha1hash FROM package_hash WHERE jobname = ?', (job,))
            storedhash = result.fetchone()
            #if any result was got
            if(storedhash):
                return True

            else:
                return False

    except sqlite3.Error:
        return False

def update_hash(job, hash, cursor):
    if(job_hash_exists(job, cursor)):
        return update_hash_internal(job, hash, cursor)

    else:
        return store_new_hash_internal(job, hash, cursor)

def store_new_hash_internal(job, hash, cursor):
       try:
           with cursor:
               #print(u'No previous hash for this file, inserting')
               cursor.execute('INSERT INTO package_hash(sha1hash, jobname) VALUES (?, ?)',(hash, job))
               return True

       except sqlite3.Error:
           return False

def update_hash_internal(job, hash, cursor):
        try:
            with cursor:
                print(u'Previous hash for this file, updating')
                cursor.execute('UPDATE package_hash SET sha1hash = ? WHERE jobname = ?', (hash, job))
                return True

        except sqlite3.Error:
            return False

def fetch_job_file_paths(job, jobnames):
    file_paths = []
    buildurl = conf.last_build_api.format(job)
    data = requests.get(buildurl, verify=True).json()
    artifacts = data['artifacts']

#    if verbose:
#        print(u'Fetching artifacts for {0}'.format(job))

    correct_artifact_paths = calculate_artifact_paths(artifacts, jobnames[job])
    for path, filename in correct_artifact_paths:
        file_url=conf.last_build_artifact.format(job, path)
        file_paths.append((filename, file_url))

    return file_paths


def calculate_artifact_paths(artifacts, match):
    correct_artifacts = []
    for artifact in artifacts:
        if artifact['fileName'].find(match.group('packagetype')):
            correct_artifacts.append((artifact['relativePath'], artifact['fileName']))

    return correct_artifacts

