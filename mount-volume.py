#!/usr/bin/env python2
from __future__ import print_function
import sys
import requests
import xml.etree.ElementTree as ET
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import time

username = sys.argv[1]
password = sys.argv[2]
volume_name=sys.argv[3]
url='https://172.23.9.101/ScalarLTFS'
auth_payload='<credentials><user>{0}</user><password>{1}</password><clientinfo>gui</clientinfo><ldap>false</ldap></credentials>'.format(username, password)
headers={'Content-Type':'application/xml'}


def login(session):
	r = session.post('{0}/authenticate'.format(url), data=auth_payload, headers=headers, verify=False)
	assert r.status_code < 400
	return session


def list_media(session, volume):
	media = []
	r = session.get('{0}/media/?volgroup_name={1}'.format(url, volume), headers=headers, verify=False)
	try:
	        assert r.status_code < 400
	except Exception as e:
		print(e)
	if len(ET.fromstring(r.text)) < 1: pass
	else:
	 	media = [ media.text for media in ET.fromstring(r.text)[0].findall('barcode') ]
	return media


def media_status(session, media):
	r = session.get('{0}/media/{1}'.format(url, media), headers=headers, verify=False)
	try:
	        assert r.status_code < 400
	except Exception as e:
		print(e)
	return r.text


def assign(session, volume):
	volume_parsed = volume.split('_')
	volume_suffix = volume_parsed[-1]
	volume_id = int(volume_parsed[-2])
	barcode = '{0}{1:04}{2}'.format(volume[:1], volume_id, volume_suffix[:1])
	src_volgroup = ET.fromstring(media_status(session, barcode)).findall('volgroup_name')[0].text
	assign_payload='<assign><volgroup_name>{0}</volgroup_name><dest_volgroup_name>{1}</dest_volgroup_name><volume_list><barcode>{2}</barcode></volume_list></assign>'.format(src_volgroup, volume, barcode)

	r = session.post('{0}/operations/assign'.format(url), data=assign_payload, headers=headers, verify=False)
	try:
	        assert r.status_code < 400
		print('Media allocation \"{0}\" SUCCESS!'.format(barcode))
	except:
		print('Media allocation \"{0}\" FAIL!'.format(barcode))
		print('Status: {0}'.format(r.status_code))
	return r.text


def attach(session, media):
	media_payload='<volume><a_state>1</a_state></volume>'
	
	r = session.put('{0}/media/{1}'.format(url, media), data=media_payload, headers=headers, verify=False)
	try:
	        assert r.status_code < 400
		print('Media attach \"{0}\" SUCCESS!'.format(media))
	except:
		print('Media attach \"{0}\" FAIL!'.format(media))
		print('Status: {0}'.format(r.status_code))
	return r.text


if __name__ == '__main__':
	session = login(requests.Session())
	media = list_media(session, volume_name)
	if len(media) < 1:
		print('No media, attempting to assign it.')
		assign(session, volume_name)
		while len(list_media(session, volume_name)) < 1:
			print ('waiting for physical allocation..')
			time.sleep(1)
		media = list_media(session, volume_name)
	for _media in media:
		assert attach(session, _media)

