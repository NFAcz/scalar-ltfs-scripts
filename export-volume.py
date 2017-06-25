#!/usr/bin/env python2
from __future__ import print_function
import sys
import requests
import xml.etree.ElementTree as ET
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

username = sys.argv[1]
password = sys.argv[2]
volume_name=sys.argv[3]
url='https://172.23.9.101/ScalarLTFS'
auth_payload='<credentials><user>{0}</user><password>{1}</password><clientinfo>gui</clientinfo><ldap>false</ldap></credentials>'.format(username, password)
volume_payload='<prepare_export><volgroup_list><volgroup_name>{0}</volgroup_name></volgroup_list></prepare_export>'
media_payload='<volume><a_state>9</a_state></volume>'
headers={'Content-Type':'application/xml'}




def login(session):
	r = session.post('{0}/authenticate'.format(url), data=auth_payload, headers=headers, verify=False)
	assert r.status_code < 400
	return session

def prepare_export(session, volume):
	r = session.post('{0}/operations/prepare_export'.format(url), data=volume_payload.format(volume), headers=headers, verify=False)
	try:
	        assert r.status_code < 400
	except:
		print('Volume prepare export \"{0}\" FAIL!'.format(volume))
	return r.text

def list_media(session, volume):
	r = session.get('{0}/media/?volgroup_name={1}'.format(url, volume), headers=headers, verify=False)
	try:
	        assert r.status_code < 400
	except Exception as e:
		print(e)
	media = [ media.text for media in ET.fromstring(r.text)[0].findall('barcode') ]
	return media

def export(session, media):
	r = session.put('{0}/media/{1}'.format(url, media), data=media_payload, headers=headers, verify=False)
	try:
	        assert r.status_code < 400
		print('Media export \"{0}\" SUCCESS!'.format(media))
	except:
		print('Media export \"{0}\" FAIL!'.format(media))
	return r.text



if __name__ == '__main__':
	session = login(requests.Session())
	assert prepare_export(session, volume_name)
	media = list_media(session, volume_name)
	for _media in media:
		assert export(session, _media)

