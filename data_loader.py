#! /usr/bin/env python

import json
import requests
from tile_generator import generate_tiles
from delete_repo import delete_repo

HOST   = 'localhost:4000'
SERVER = 'http://' + HOST

def create_repo():
    ''' connect to provided server and create new repo. '''
    url = SERVER + '/api/repos'
    repo_meta = '{"alias": "benchmarking", "description": "test repo for running benchmarks"}'
    response = requests.post(url, data=repo_meta)

    if response.status_code == 200 :
        return response.json()['root']
    else:
        return None

def create_data_instance(uuid, typename='imagetile', dataname='tiles'):
    ''' connect to new repo and create new data instance for the tiles. '''
    url = SERVER + '/api/repo/' + uuid + '/instance'
    payload = {
            'typename': typename,
            'versioned': '1',
            'sync': '',
            'dataname': dataname
    }
    response = requests.post(url, data=json.dumps(payload))
    return dataname

def upload_tile(uuid, instance, tile, num):
    coords = '%s_%s_10' % (num, num)
    url = SERVER + '/api/node/' + uuid + '/' + instance + '/tile/xy/0/' + coords
    response = requests.post(url, data=tile)


def set_instance_meta(uuid, instance):
    url = SERVER + '/api/node/' + uuid + '/' + instance + '/metadata'
    metadata = '{"0": {  "Resolution": [10.0, 10.0, 10.0], "TileSize": [512, 512, 512] }, "MaxTileCoord" :[100,100,100], "MinTileCoord": [0,0,0]}'
    response = requests.post(url, data=metadata)


def upload_tiles(args):


    uuid = create_repo()

    instance = create_data_instance(uuid)

    set_instance_meta(uuid, instance)

    # generate 100 tiles and upload to the new data instance.
    for i in range(100):
        tile = generate_tiles(None, i + 1)
        upload_tile(uuid, instance, tile, i + 1)

    delete_repo({'server': HOST, 'uuid': uuid})

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Upload test data.')
    parser.add_argument('--server', help='dvid server url')
    cl_args = vars(parser.parse_args())
    defaults = {
        'server': 'http://localhost:8000'
    }

    import pdb; pdb.set_trace()
    args = defaults.copy()
    print args.get('server')
    args.update(cl_args)
    upload_tiles(args)
