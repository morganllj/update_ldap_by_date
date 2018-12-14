#!/usr/bin/env python3
#

import getopt
import re
import sys
import yaml
from ldap3 import Server, Connection, ALL
from datetime import datetime

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

# https://martin-thoma.com/configuration-files-in-python/open
with open (config_file, 'r') as ymlfile:
    config = yaml.load(ymlfile)

server = Server(config["ldap"]["host"])
conn = Connection(server, config["ldap"]["binddn"], config["ldap"]["bindpass"], auto_bind=True)
rc = conn.search(config["ldap"]["basedn"], config["ldap"]["search"], attributes=['*'])
print (conn.entries)

for e in conn.response:

    print ()
    
    frc_updt = "none"
    last_updd = "none"

    if config["ldap"]["change_attr"] in e['attributes'].keys():
       frc_updt   = e['attributes'][config["ldap"]["change_attr"]]
    if config["ldap"]["dateattr"]    in e['attributes'].keys():
        last_updd =  e['attributes'][config["ldap"]["dateattr"]]

    if isinstance(last_updd[0], datetime):
        print (e['attributes']['uid'][0], last_updd[0].date() , frc_updt)
    else:
        print (e['attributes']['uid'][0], last_updd, frc_updt)
