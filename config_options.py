import re
#Options you can play with to change behaviours

#regex to match info in packages
#update this to match your project (must have packagetype and release)
package_regex = re.compile('(?P<packagetype>[\w]+)_(?P<release>[\w]+)')

#Jenkins host
build_host = 'yourbuildhost'
url = 'https://' + build_host + '/api/json'

#Give this jobname to get json data about last successful build
last_build_api = 'https://' + build_host + '/job/{0}/lastSuccessfulBuild/api/json'

#Give this jobname and artifact relative path to get file url
last_build_artifact = 'https://' + build_host + '/job/{0}/lastSuccessfulBuild/artifact/{1}'

#Where to put the files (will contain nightly-debug etc folders)
ship_directory = '/path/to/fileendpoint/{0}-{1}/{2}'

#the mapping between regex extracted jobname variables and actual folders
#in case they don't match exactly
release_mapping = {'nightly':'nightly', 'default':'table'}
buildtype_mapping = {'debug':'debug', 'default':'release'}

#sqlitedb containing the hash of each job's file
sqlitepath='/path/to/packagehash.db'
