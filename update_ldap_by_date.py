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


def change_values(e):
    i=0
    changes = {};


    if not print_only:
        # conn.modify(e["dn"],
        #     { cfg["ldap"]["change_attr"]:   [(MODIFY_REPLACE, ["ldap"]["change_value"])],
        #       cfg["ldap"]["statuslogattr"]: [(MODIFY_ADD,     [ldapdatenow+" update_ldap_by_date.py set "+changefrom+" to "+changeto])]
        #     })

        conn.modify(e["dn"],
            { cfg["ldap"]["change_attr"]:       [(MODIFY_REPLACE, cfg["ldap"]["change_value"])],
              cfg["ldap"]["acctstatuslogattr"]: [(MODIFY_ADD,     [ldapdatenow+" update_ldap_by_date.py set "+cfg["ldap"]["change_attr"]+" to "+cfg["ldap"]["change_value"]])]
            })        
        if conn.result["result"]:
            print ("modify failed:", conn.result)
            sys.exit()

        print("")
        sys.exit()




#        changes[cfg["ldap"]["acctstatusattr"]] = [(MODIFY_ADD, [ldapdatenow+" update_ldap_by_date.py set "+changefrom+" to "+changeto])]

    

    
#    changes[cfg["ldap"]["acctstatusattr"]: [(MODIFY_ADD, [ldapdatenow+" update_ldap_by_date.py"])]]
#     for a in cfg["ldap"]["change_attrs"]:
# #        changes[cfg["ldap"]["change_attrs"][i]] =  [(MODIFY_REPLACE, [cfg["ldap"]["change_values"[i]]])]
# #        changes["sdpForceAccountUpdate"] =  [(MODIFY_REPLACE, [cfg["ldap"]["change_values"[i]]])]
#         changes["sdpForceAccountUpdate"] =  [(MODIFY_REPLACE, [)]
#         i=i+1
#     print ("changes:", changes)
# #    conn.modify(dn, changes)
    

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

 # olddatetime=olddatetime.astimezone(pytz.UTC)
 #        priorldapdateexp = olddatetime.strftime('%Y%m%d%H%M%S') + "Z"

 #    ldapdatenow = datetime.utcnow().strftime('%Y%m%d%H%M%S') + "Z"

datenow = datetime.now(pytz.utc);
ldapdatenow = datenow.astimezone(pytz.UTC).strftime('%Y%m%d%H%M%S') + "Z"

for e in conn.response:
    print (e["attributes"]["uid"][0], "!", sep="", end="")
    if cfg["ldap"]["dateattr"] in e["attributes"].keys():
        dateinldap = e["attributes"][cfg["ldap"]["dateattr"]][0]
        print (dateinldap, "!", sep="", end="")
        lookbacktime = timedelta(days=cfg["other"]["lookback"])
        if dateinldap < (datenow-lookbacktime):
            print ("forceupdate", end="")
            change_values(e)
        else:
            print ("noupdate", sep="!", end="")
    else:
        print ("None","forceupdate", sep="!", end="")
        change_values(e)
    print ("")
        


    
    # frc_updt = "none"
    # last_updd = "none"

    # for change_attr in 
    # if cfg["ldap"]["change_attr"] in e['attributes'].keys():
    #    frc_updt.append(e['attributes'][cfg["ldap"]["change_attr"]])
    # if cfg["ldap"]["dateattr"]    in e['attributes'].keys():
    #     last_updd.append(e['attributes'][cfg["ldap"]["dateattr"]])

    # if isinstance(last_updd[0], datetime):
    #     print (e['attributes']['uid'][0], last_updd[0].date(), last_updd[0].time() , frc_updt, " ", end='')
    #     months_ago = date.today() + relativedelta(months=-cfg["other"]["lookback"])
    #     if (last_updd[0].date() < months_ago):
    #             i = 0
    #             for a in cfg["ldap"]["change_attr"]:
    #                 print (a, ":", cfg["ldap"]["change_value"][i])
    #     else:
    #             print ("leave!")
    # else:
    #     print (e['attributes']['uid'][0], last_updd, frc_updt)
