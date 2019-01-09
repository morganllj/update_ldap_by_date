#!/usr/bin/env python3
#

import getopt
import re
import sys
import yaml
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, MODIFY_ADD
from datetime import datetime, timezone, date, timedelta
import pytz

def print_usage():
    print ("usage: "+sys.argv[0]+" [-n] -c <config>.yml ")
    exit()


def change_values(e,ldapdateinldap):
    i=0
    changes = {};


    if not print_only:
        if (ldapdateinldap is None):
            conn.modify(e["dn"],
                { cfg["ldap"]["change_attr"]:       [(MODIFY_REPLACE, cfg["ldap"]["change_value"])],
                  cfg["ldap"]["acctstatuslogattr"]: [(MODIFY_ADD,
                      [ldapdatenow+" update_ldap_by_date.py set " + cfg["ldap"]["change_attr"] + " to " + cfg["ldap"]["change_value"] + ", " + cfg["ldap"]["dateattr"] + ": None"])]
                })
        else:
            conn.modify(e["dn"],
                { cfg["ldap"]["change_attr"]:       [(MODIFY_REPLACE, cfg["ldap"]["change_value"])],
                  cfg["ldap"]["acctstatuslogattr"]: [(MODIFY_ADD,
                      [ldapdatenow+" update_ldap_by_date.py set " + cfg["ldap"]["change_attr"] + " to " + cfg["ldap"]["change_value"] + ", " + cfg["ldap"]["dateattr"] + ": "+  ldapdateinldap])]
                })
            
        if conn.result["result"]:
            print ("modify failed:", conn.result)
            sys.exit()

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

datenow = datetime.now(pytz.utc);
ldapdatenow = datenow.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S') + "Z"

for e in conn.response:
    print (e["attributes"]["uid"][0], "!", sep="", end="")
    
    if cfg["ldap"]["dateattr"] in e["attributes"].keys():
        dateinldap = e["attributes"][cfg["ldap"]["dateattr"]][0]
        ldapdateinldap = dateinldap.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S') + "Z"
        
        print (dateinldap, "!", sep="", end="")
        lookbacktime = timedelta(days=cfg["other"]["lookback"])
        
        if cfg["ldap"]["change_attr"] in e["attributes"].keys():
            if e["attributes"][cfg["ldap"]["change_attr"]] == True:
                print ("alreadyset", sep="!")
                continue

        if dateinldap < (datenow-lookbacktime):
            print ("forceupdate", end="")
            change_values(e,ldapdateinldap)
        else:
            print ("noupdate", sep="!", end="")
    else:
        print ("None!", sep="!", end="")

        if cfg["ldap"]["change_attr"] in e["attributes"].keys():
            if e["attributes"][cfg["ldap"]["change_attr"]] == True:
                print ("alreadyset", sep="!")
                continue
            else:
                print ("forceupdate", end="")
                change_values(e,None)
        else:
            print ("forceupdate", end="")
            change_values(e,None)
    print ("")
        
