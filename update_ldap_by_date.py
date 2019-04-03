#!/usr/bin/env python3
#

import getopt
import re
import sys
import yaml
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, MODIFY_ADD
from datetime import datetime, timezone, date, timedelta
import pytz
import syslog

def print_usage():
    print ("usage: "+sys.argv[0]+" [-d] [-n] -c <config>.yml")
    print ("    -n print-only")
    print ("    -d debug: also print accounts that won't be changed")
    print ()
    exit()

datenow = datetime.now(pytz.utc);
ldapdatenow = datenow.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S') + "Z"

def my_print(*args):
    if (print_only and not args[0].startswith('-n')):
        print ("ro ", end="")
    print (*args)
    a = ' '.join(args)

    r = ""
    if (print_only and not args[0].startswith('-n')):
        r = " ro"
    syslog.syslog(syslog.LOG_INFO, ldapdatenow + r + " " + a)

def change_values(e,ldapdateinldap):
    i=0
    changes = {};

    if not print_only:
        if (ldapdateinldap is None):
            conn.modify(e["dn"],
                { cfg["ldap"]["change_attr"]:       [(MODIFY_REPLACE,
                      cfg["ldap"]["change_value"])],
                  cfg["ldap"]["acctstatuslogattr"]: [(MODIFY_ADD,
                      [ldapdatenow+" update_ldap_by_date.py set " +
                          cfg["ldap"]["change_attr"] + " to " + cfg["ldap"]["change_value"] +
                          ", " + cfg["ldap"]["dateattr"] + ": None"])]
                })
        else:
            conn.modify(e["dn"],
                { cfg["ldap"]["change_attr"]:       [(MODIFY_REPLACE,
                      cfg["ldap"]["change_value"])],
                  cfg["ldap"]["acctstatuslogattr"]: [(MODIFY_ADD,
                      [ldapdatenow+" update_ldap_by_date.py set " +
                          cfg["ldap"]["change_attr"] + " to " + cfg["ldap"]["change_value"] +
                          ", " + cfg["ldap"]["dateattr"] + ": "+  ldapdateinldap])]
                })
            
        if conn.result["result"]:
            print ("modify failed:", conn.result)
            sys.exit()

opts, args = getopt.getopt(sys.argv[1:], "nc:d")

print_only = 0
debug = 0
config_file = None

for opt, arg in opts:
    if opt in ('-n'):
        print_only = 1
    elif opt in ('-c'):
        config_file = arg
    elif opt in ('-d'):
        debug = 1

if (config_file is None):
    print_usage()

syslog.syslog(syslog.LOG_INFO, ldapdatenow + " starting " +
                  datetime.now(pytz.utc).astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S') + "Z")
    
if (print_only):
    my_print("-n used, no changes will be made")
    
# https://martin-thoma.com/configuration-files-in-python/open
with open (config_file, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

server = Server(cfg["ldap"]["host"])
conn = Connection(server, cfg["ldap"]["binddn"], cfg["ldap"]["bindpass"], auto_bind=True)
rc = conn.search(cfg["ldap"]["basedn"], cfg["ldap"]["search"], attributes=['*'])

for e in conn.response:
    outstr = None    
    
    outstr = e["attributes"]["uid"][0] + "!"
    
    if cfg["ldap"]["dateattr"] in e["attributes"].keys():
        dateinldap = e["attributes"][cfg["ldap"]["dateattr"]][0]
        ldapdateinldap = dateinldap.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S') + "Z"
        
        outstr = outstr + dateinldap.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S') + "Z" + "!"
        
        lookbacktime = timedelta(days=cfg["other"]["lookback"])
        
        if cfg["ldap"]["change_attr"] in e["attributes"].keys():
            if e["attributes"][cfg["ldap"]["change_attr"]] == True:
                outstr = outstr + "alreadyset"
                if debug:
                    my_print (outstr)
                continue
        if dateinldap < (datenow-lookbacktime):
            outstr = outstr + "forceupdate"
            my_print (outstr)
            change_values(e,ldapdateinldap)
        else:
            outstr = outstr + "noupdate"
            if debug:
                my_print (outstr)
    else:
        outstr = outstr + "None" + "!";

        if cfg["ldap"]["change_attr"] in e["attributes"].keys():
            if e["attributes"][cfg["ldap"]["change_attr"]] == True:
                outstr = outstr + "alreadyset"
                if debug:
                    my_print (outstr)
                continue
            else:
                oustr = outstr + "forceupdate";
                my_print (outstr)
                change_values(e,None)
        else:
            outstr = outstr + "forceupdate"
            my_print (outstr)
            change_values(e,None)
        
syslog.syslog(syslog.LOG_INFO, ldapdatenow + " finished " +
                  datetime.now(pytz.utc).astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S') + "Z")
