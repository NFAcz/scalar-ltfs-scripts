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
from methods import *

cfg = yaml.load(open('config.yml', 'r'))

parser = argparse.ArgumentParser()
parser.add_argument('-u', '--username', help='Username', required=True)
parser.add_argument('-p', '--password', help='Password', required=True)
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
args = parser.parse_args()


with requests.Session() as session:
	login(session, args.username, args.password)

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
		format_media(session, args.media)

	if args.export:
		media = list_media_in_volgroup(session, args.volume)
		prepare_export(session, args.volume)
		for _media in media:
			export_media(session, _media)

	if args.replicate:
		replicate_volume(session, volume)

