#!/usr/bin/env python3
#

import getopt
import re
import sys
import yaml

def print_usage():
    print ("usage: "+sys.argv[0]+" [-n] -c <config>.yml ")
    exit()

opts, args = getopt.getopt(sys.argv[1:], "nc:")

print_only = 0
config_file = None

for opt, arg in opts:
    if opt in ('-n'):
        print_only = 1
    elif opt in ('-c'):
        config_file = arg

if (config_file is None):
    print_usage()

# https://martin-thoma.com/configuration-files-in-python/
with open (config_file, 'r') as ymlfile:
    config = yaml.load(ymlfile)

print (config["ldap"]["user"])
