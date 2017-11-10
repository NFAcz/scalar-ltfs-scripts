# Scalar LTFS scripts

This repo contains a python script used to communicate with a Quantum Scalar LTFS Appliance XMLRPC API.

## Usage

```
$ python scalar-ltfs-api.py -h
usage: scalar-ltfs-api.py [-h] -u USERNAME -p PASSWORD [-e ENDPOINT]
                          [--volume VOLUME] [--destvolume DESTVOLUME]
                          [--media MEDIA] [--status] [--format] [--assign]
                          [--replicate] [--attach] [--detach] [--export]
                          [--create]

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Username
  -p PASSWORD, --password PASSWORD
                        Password
  -e ENDPOINT, --endpoint ENDPOINT
                        Scalar LTFS API Endpoint
  --volume VOLUME       Volume name
  --destvolume DESTVOLUME
                        Destination volume name
  --media MEDIA         Media barcode
  --status              Show asset status
  --format              Format media
  --assign              Assign media to volume
  --replicate           Replicate volume
  --attach              Attach media
  --detach              Detach media
  --export              Export media
  --create              Create volume
```

## Examples

```
$ python scalar-ltfs-api.py -u **** -p **** --volume VOLUME001 --create
Creating volume VOLUME001
```

```
$ python scalar-ltfs-api.py -u **** -p **** --volume VOLUME001 --format
Deatching media VOLUME001
Formatting media VOLUME001
```

```
$ python scalar-ltfs-api.py -u **** -p '****' --volume VOLUME001 --export
Preparing volume VOLUME001 for export
Exporting media VOL001
```
