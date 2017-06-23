#!/bin/bash

a=0

while true; do
	b=$(curl -s 'https://172.23.9.101/ScalarLTFS/media' -H 'Cookie: sltfsWS=%A0%EA%A0%E9%1F%8BATD%3D%5D%AB%D0%87%E1%F5%D8%EC%96%3A%C0%5C%86Zs%8CK%A3J%85%60D%C5O%E4%99%A2%BB%A2Y' -H 'Origin: https://172.23.9.101' -H 'Accept-Encoding: gzip, deflate, br' -H 'Accept-Language: en-US,en;q=0.8' -H 'X-Requested-With: ShockwaveFlash/26.0.0.131' -H 'Connection: keep-alive' -H 'X-HTTP-Method-Override: GET' -H 'Pragma: no-cache' -H 'User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.104 Safari/537.36' -H 'Content-Type: application/xml' -H 'Accept: */*' -H 'Cache-Control: no-cache' -H 'Referer: https://172.23.9.101/SLTFSMain.html' -H 'DNT: 1' --data-binary '<>' --compressed --insecure|xmlstarlet sel -t -v "/media/volume[barcode='P0034B']/f_blocksused")
	c=$(($b - $a))
	echo $(($c * 524288 / 1024 / 1024 / 15 ))
	a=$b
	sleep 15
done
