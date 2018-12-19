#!/usr/bin/env python3
#

import getopt
import re
import sys
import yaml
from ldap3 import Server, Connection, ALL
from datetime import datetime, timezone, date
from dateutil.relativedelta import relativedelta

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
    cfg = yaml.load(ymlfile)

server = Server(cfg["ldap"]["host"])
conn = Connection(server, cfg["ldap"]["binddn"], cfg["ldap"]["bindpass"], auto_bind=True)
rc = conn.search(cfg["ldap"]["basedn"], cfg["ldap"]["search"], attributes=['*'])

for e in conn.response:
    frc_updt = "none"
    last_updd = "none"

    for change_attr in 
    if cfg["ldap"]["change_attr"] in e['attributes'].keys():
       frc_updt.append(e['attributes'][cfg["ldap"]["change_attr"]])
    if cfg["ldap"]["dateattr"]    in e['attributes'].keys():
        last_updd.append(e['attributes'][cfg["ldap"]["dateattr"]])

    if isinstance(last_updd[0], datetime):
        print (e['attributes']['uid'][0], last_updd[0].date(), last_updd[0].time() , frc_updt, " ", end='')
        months_ago = date.today() + relativedelta(months=-cfg["other"]["lookback"])
        if (last_updd[0].date() < months_ago):
                i = 0
                for a in cfg["ldap"]["change_attr"]:
                    print (a, ":", cfg["ldap"]["change_value"][i])
        else:
                print ("leave!")
    else:
        print (e['attributes']['uid'][0], last_updd, frc_updt)
