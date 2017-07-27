#!/usr/bin/env python2
from __future__ import print_function
import sys
import requests
import xml.etree.ElementTree as ET
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
import time
import argparse
import yaml

cfg = yaml.load(open('config.yml', 'r'))

def load_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-u', '--username', help='Username', required=True)
	parser.add_argument('-p', '--password', help='Password', required=True)
	parser.add_argument('-e', '--endpoint', help='Scalar LTFS API Endpoint', default=cfg['endpoint'])
	parser.add_argument('--volume', help='Volume name')
	parser.add_argument('--destvolume', help='Destination volume name')
	parser.add_argument('--media', help='Media barcode')
	parser.add_argument('--status', help='Show asset status', action='store_true')
	parser.add_argument('--format', help='Format media', action='store_true')
	parser.add_argument('--assign', help='Assign media to volume', action='store_true')
	parser.add_argument('--replicate', help='Replicate volume', action='store_true')
	parser.add_argument('--attach', help='Attach media', action='store_true')
	parser.add_argument('--detach', help='Detach media', action='store_true')
	parser.add_argument('--export', help='Export media', action='store_true')
	parser.add_argument('--create', help='Create volume', action='store_true')
	global args
	args = parser.parse_args()


def api_handler(session, method, path, payload):
        r = session.request(method, '{0}{1}'.format(args.endpoint, path), data=payload, headers=cfg['headers'], verify=False)
        r.raise_for_status()
	return r


def login(session):
	payload='<credentials><user>{0}</user><password>{1}</password><clientinfo>gui</clientinfo><ldap>false</ldap></credentials>'
	r = api_handler(session, 'POST', '/authenticate', payload.format(args.username, args.password))
	return r.text 


def list_media_in_volgroup(session, volume):
	media = []
	r = api_handler(session, 'GET', '/media/?volgroup_name={0}'.format(volume), None)
	api_response = ET.fromstring(r.text)

	if len(api_response) < 1: pass
	else:
	 	media = [ media.text for media in api_response[0].findall('barcode') ]
	return media

def volume_to_barcode(volume):
	volume_parsed = volume.split('_')
	volume_suffix = volume_parsed[-1]
	volume_id = int(volume_parsed[-2])
	barcode = '{0}{1:04}{2}'.format(volume[:1], volume_id, volume_suffix[:1])
	return barcode


def status_media(session, media):
	r = api_handler(session, 'GET', '/media/{0}'.format(media), None)
	return ET.fromstring(r.text)


def status_volume(session, volume):
	r = api_handler(session, 'GET', '/volume_groups/{0}'.format(volume), None)
	return ET.fromstring(r.text)


def assign_media(session, destvolume, barcode=None, **kwargs):
	if barcode is None:
		barcode = volume_to_barcode(destvolume)
	status = status_media(session, barcode)
	srcvolume = status.findall('volgroup_name')[0].text

	payload='<assign><volgroup_name>{0}</volgroup_name><dest_volgroup_name>{1}</dest_volgroup_name><volume_list><barcode>{2}</barcode></volume_list></assign>'
	r = api_handler(session, 'POST', '/operations/assign', payload.format(srcvolume, destvolume, barcode))
	print ('Assigning media {0} to volume {1}'.format(barcode, destvolume))

	while 1:
		time.sleep(1)
		media = list_media_in_volgroup(session, destvolume)
		if len(media) > 0 and barcode in media: break
	#FIXME return something


def replicate_volume(session, volume, destvolume):
	payload='<replicate><volgroup_name>{0}</volgroup_name><dest_volgroup_name>{1}</dest_volgroup_name><verify>false</verify></replicate>'
        r = api_handler(session, 'POST', '/operations/replicate', payload.format(volume, destvolume))
	print('Replicating volumegroup {0} to {1}'.format(volume, destvolume))
	print(r.text)

	while 1:
		time.sleep(10)
		# TODO finish testing
		status = status_volume(session, destvolume)
		try:
			vg_state = status.findall('idx_vg_state')[0].text
		except IndexError:
			vg_state = -1
			print(ET.tostring(status))
		if int(vg_state) == 2 : break

	#FIXME volume status
	#FIXME return something


def attach_media(session, media):
	payload='<volume><a_state>1</a_state></volume>'
	r = api_handler(session, 'PUT', '/media/{0}'.format(media), payload)
	print('Attaching media {0}'.format(media))

        while 1:
                time.sleep(1)
                status = status_media(session, media)
		a_state = status.findall('a_state')[0].text
                if a_state == 'attached' : break
	return r.text


def detach_media(session, media):
	payload='<volume><a_state>3</a_state></volume>'
	r = api_handler(session, 'PUT', '/media/{0}'.format(media), payload)
	print('Deatching media {0}'.format(media))

        while 1:
                time.sleep(1)
                status = status_media(session, media)
		a_state = status.findall('a_state')[0].text
                if a_state == 'sequestered' : break
	return r.text


def format_media(session, media):
	payload='<volume><a_state>5</a_state></volume>'
	r = api_handler(session, 'PUT', '/media/{0}'.format(media), payload)
	print('Formatting media {0}'.format(media))

        while 1:
                time.sleep(1)
                status = status_media(session, media)
		a_state = status.findall('a_state')[0].text
                if a_state == 'auto-attachable' : break
	return r.text


def prepare_export(session, volume):
	payload='<prepare_export><volgroup_list><volgroup_name>{0}</volgroup_name></volgroup_list></prepare_export>'
        r = api_handler(session, 'POST', '/operations/prepare_export', payload.format(volume))
	print('Preparing volume {0} for export'.format(volume))

        while 1:
                time.sleep(1)
                status = status_volume(session, volume)
		vg_state = status.findall('idx_vg_state')[0].text
                if int(vg_state) == 3 : break
        return r.text


def export_media(session, media):
	payload='<volume><a_state>9</a_state></volume>'
        r = api_handler(session, 'PUT', '/media/{0}'.format(media), payload)
	print('Exporting media {0}'.format(media))

        while 1:
                time.sleep(1)
                status = status_media(session, media)
		a_state = status.findall('a_state')[0].text
                if a_state == 'pending export' : break
        return r.text


def create_volume(session, volume):
	payload='<volume_group><online>true</online><comment>{0}</comment><low_free_threshold>100</low_free_threshold><scratch_enabled>false</scratch_enabled></volume_group>'
        r = api_handler(session, 'POST', '/volume_groups/{0}'.format(volume), payload.format(volume))
	print('Creating volume {0}'.format(volume))
	return r.text


if __name__ == '__main__':
	load_args()
	with requests.Session() as session:
		login(session)

		if args.status:
			if args.volume is not None:
				status = ET.tostring(status_volume(session, args.volume)).replace('><','>\n<')
				print(status)
			elif args.media is not None:
				status = ET.tostring(status_media(session, args.media)).replace('><','>\n<')
				print(status)

		if args.create:
			create_volume(session, args.volume)

		if args.attach:
			if args.volume is not None:
				media = list_media_in_volgroup(session, args.volume)
			elif args.media is not None:
				media = [args.media]
			if len(media) < 1:
				print('No media, attempting to assign it.')
				assign_media(session, args.volume)
			for _media in media:
				attach_media(session, _media)

		if args.detach:
			if args.volume is not None:
				media = list_media_in_volgroup(session, args.volume)
			elif args.media is not None:
				media = [args.media]
			if len(media) < 1:
				media = []
			for _media in media:
				detach_media(session, _media)

		if args.format:
			if args.volume is not None:
				media = list_media_in_volgroup(session, args.volume)
			elif args.media is not None:
				media = [args.media]
			if len(media) < 1:
				media = []
			for _media in media:
				status = status_media(session, _media)
				a_state = status.findall('a_state')[0].text
				if a_state not in ['sequestered', 'auto-attachable'] :
					detach_media(session, _media)
				format_media(session, _media)

		if args.export:
			media = list_media_in_volgroup(session, args.volume)
			prepare_export(session, args.volume)
			for _media in media:
			        while 1:
			                time.sleep(1)
			                status = status_media(session, media)
					a_state = status.findall('a_state')[0].text
			                if a_state == 'ready for export' : break
				export_media(session, _media)

		if args.assign:
			if args.media is not None and args.volume is not None:
				status = status_media(session, args.media)
				a_state = status.findall('a_state')[0].text
				volgroup_name = status.findall('volgroup_name')[0].text
				if a_state not in ['sequestered', 'auto-attachable'] :
					detach_media(session, args.media)
				if volgroup_name == '[holding_volume]':
					format_media(session, args.media)
				assign_media(session, args.volume, barcode=args.media)
			else:
				print('Missing media or volume arguments!')
				sys.exit(1)
		if args.replicate:
			if args.volume is not None:
				media = volume_to_barcode(args.destvolume)
				scratch_media = list_media_in_volgroup(session, '[scratch media]')
				if media in scratch_media:
					scratch_media.pop(scratch_media.index(media))
				for _media in scratch_media:
					assign_media(session, '[holding_volume]', barcode=_media)
                                status = status_media(session, media)
                                a_state = status.findall('a_state')[0].text
                                if a_state not in ['sequestered', 'auto-attachable'] :
                                        detach_media(session, media)
				if media not in list_media_in_volgroup(session, '[scratch media]'):
					format_media(session, media)
				replicate_volume(session, args.volume, args.destvolume)



