This script can be used to fetch files from any jenkins host with a public json web api. The files are hashed with sha1 and then on subsequent runs if the hash is not different the file is not included

We use this script to fetch packages built on our jenkins to the package repo for signing and release to the general public

It works by taking two variables from the jobname and using that to consruct the final path at which file should be stored at (allowing for multiple release channels/components based on job name of your package)

These end file path, etc are all highly configurable, check the config_options.py file for more

