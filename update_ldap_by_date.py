#!/usr/bin/env python3
#

import getopt
import re
import sys
import yaml
import ldap

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

try:
    ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)
    l = ldap.initialize(config["ldap"]["host"])
    l.simple_bind(config["ldap"]["binddn"], config["ldap"]["bindpass"]);
    r = l.search(config["ldap"]["basedn"], ldap.SCOPE_SUBTREE, config["ldap"]["search"]);
    result_set = []

    while 1:
        result_type, result_data = l.result(r, 0)
        if (result_data == []):
            break

            print ("result:", result_data)
except ldap.LDAPError as ldap_error:
    print ("problem searching ldap: ", ldap_error)
