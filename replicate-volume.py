#!/usr/bin/env python2
from __future__ import print_function
import sys
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

username = sys.argv[1]
password = sys.argv[2]
volume_name=sys.argv[3]
url='https://172.23.9.101/ScalarLTFS'
auth_payload='<credentials><user>{0}</user><password>{1}</password><clientinfo>gui</clientinfo><ldap>false</ldap></credentials>'.format(username, password)
volume_payload='<replicate><volgroup_name>{0}_A</volgroup_name><dest_volgroup_name>{0}_B</dest_volgroup_name><verify>true</verify></replicate>'.format(volume_name)
headers={'Content-Type':'application/xml'}

s = requests.Session()

try:
	r1 = s.post('{0}/authenticate'.format(url), data=auth_payload, headers=headers, verify=False)
except Exception as e:
	print(e)

if r1.status_code < 400:
	print("Login successful!")
else:
	print("Login FAIL!")
	sys.exit(1)

try:
	r2 = s.post('{0}/operations/replicate'.format(url), data=volume_payload, headers=headers, verify=False)
except Exception as e:
	print(e)

if r2.status_code < 400:
	print('Volume replicate \"{0}\" successful!'.format(volume_name))
else:
	print('Volume replicate \"{0}\" FAIL!'.format(volume_name))

