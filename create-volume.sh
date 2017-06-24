#!/bin/bash
#set -x
USERNAME="$1"
PASSWORD="$2"
URL="https://172.23.9.101/ScalarLTFS"
AUTH_PAYLOAD="<credentials><user>$USERNAME</user><password>$PASSWORD</password><clientinfo>gui</clientinfo><ldap>false</ldap></credentials>"
CURL_PARAMS="-H Content-Type:application/xml -b ltfs_cookies.txt"
VOLUME_NAME="$3"
VOLUME_PAYLOAD="<volume_group><online>false</online><comment>$VOLUME_NAME</comment><low_free_threshold>100</low_free_threshold><scratch_enabled>false</scratch_enabled></volume_group>"
#LOGIN
if (curl -ks ${URL}/authenticate -H Content-Type:application/xml -c ltfs_cookies.txt -d $AUTH_PAYLOAD); then
	echo "Login successful!"
else
	echo "Login FAIL!"
fi
#EXEC
if (curl -ks ${URL}/volume_groups/$VOLUME_NAME $CURL_PARAMS -d $VOLUME_PAYLOAD); then
	echo "Volume creation \"$VOLUME_NAME\" successful!"
else
	echo "Volume creation \"$VOLUME_NAME\" FAIL!"
fi
