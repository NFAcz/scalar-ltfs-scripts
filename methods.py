import yaml
import xml.etree.ElementTree as ET

cfg = yaml.load(open('config.yml', 'r'))

def api_handler(session, method, path, payload):
	r = session.request(method, '{0}{1}'.format(cfg['endpoint'], path), data=payload, headers=cfg['headers'], verify=False)
	r.raise_for_status()
	return r

def login(session, username, password):
	payload='<credentials><user>{0}</user><password>{1}</password><clientinfo>gui</clientinfo><ldap>false</ldap></credentials>'
	r = api_handler(session, 'POST', '/authenticate', payload.format(username, password))
	return r.text 

def gen_barcode_from_volume(volume):
 	volume_parsed = volume.split('_')
	volume_suffix = volume_parsed[-1]
	volume_id = int(volume_parsed[-2])
	barcode = '{0}{1:04}{2}'.format(volume[:1], volume_id, volume_suffix[:1])
	return barcode

def list_media_in_volgroup(session, volume):
	media = []
	r = api_handler(session, 'GET', '/media/?volgroup_name={0}'.format(volume), None)
	api_response = ET.fromstring(r.text)

	if len(api_response) < 1: pass
	else:
	 	media = [ media.text for media in api_response[0].findall('barcode') ]
	return media

def status_media(session, media):
	r = api_handler(session, 'GET', '/media/{0}'.format(media), None)
	return ET.fromstring(r.text)

def status_volume(session, volume):
	r = api_handler(session, 'GET', '/volume_groups/{0}'.format(volume), None)
	return ET.fromstring(r.text)

def assign_media(session, volume):
	barcode = gen_barcode_from_volume(volume)
	status = status_media(session, barcode)
	src_volgroup = status.findall('volgroup_name')[0].text

	payload='<assign><volgroup_name>{0}</volgroup_name><dest_volgroup_name>{1}</dest_volgroup_name><volume_list><barcode>{2}</barcode></volume_list></assign>'
	r = api_handler(session, 'POST', '/operations/assign', payload.format(src_volgroup, volume, barcode))

	while 1:
		time.sleep(1)
		media = list_media_in_volgroup(session, volume)
		if len(media) > 0 and barcode in media: break
	#FIXME return something
	print ('Media {0} assigned to volume {1}'.format(media, volume))

def replicate_volume(session, volume, destvolume):
	payload='<replicate><volgroup_name>{0}</volgroup_name><dest_volgroup_name>{1}</dest_volgroup_name><verify>true</verify></replicate>'
	r = api_handler(session, 'POST', '/operations/replicate', payload.format(volume, destvolume))

	while 1:
		time.sleep(1)
		# TODO finish testing
		status = status_volume(session, destvolume)
		vg_state = status[0].findall('idx_vg_state')[0].text
		if int(vg_state) == 1 : break

	#FIXME volume status
	#FIXME return something

def attach_media(session, media):
	payload='<volume><a_state>1</a_state></volume>'
	r = api_handler(session, 'PUT', '/media/{0}'.format(media), payload)

	while 1:
		time.sleep(1)
		status = status_media(session, media)
		a_state = status.findall('a_state')[0].text
		if a_state == 'attached' : break
	return r.text

def detach_media(session, media):
	payload='<volume><a_state>3</a_state></volume>'
	r = api_handler(session, 'PUT', '/media/{0}'.format(media), payload)

	while 1:
		time.sleep(1)
		status = status_media(session, media)
		a_state = status.findall('a_state')[0].text
		if a_state == 'sequestered' : break
	return r.text

def format_media(session, media):
	payload='<volume><a_state>5</a_state></volume>'
	r = api_handler(session, 'PUT', '/media/{0}'.format(media), payload)

	while 1:
		time.sleep(1)
		status = status_media(session, media)
		a_state = status.findall('a_state')[0].text
		if a_state == 'auto-attachable' : break
	return r.text

def prepare_export(session, volume):
	payload='<prepare_export><volgroup_list><volgroup_name>{0}</volgroup_name></volgroup_list></prepare_export>'
	r = api_handler(session, 'POST', '/operations/prepare_export', payload.format(volume))

	while 1:
		time.sleep(1)
		status = status_volume(session, volume)
		vg_state = status[0].findall('idx_vg_state')[0].text
		if int(vg_state) == 3 : break
	return r.text

def export_media(session, media):
	payload='<volume><a_state>9</a_state></volume>'
	r = api_handler(session, 'PUT', '/media/{0}'.format(media), payload)

	while 1:
		time.sleep(1)
		status = status_media(session, media)
		a_state = status.findall('a_state')[0].text
		if a_state == 'pending export' : break
	return r.text

def create_volume(session, volume):
	payload='<volume_group><online>true</online><comment>{0}</comment><low_free_threshold>100</low_free_threshold><scratch_enabled>false</scratch_enabled></volume_group>'
	r = api_handler(session, 'POST', '/volume_groups/{0}'.format(volume), payload.format(volume))
	return r.text

