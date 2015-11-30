#! /usr/bin/env python

import json
import requests

def delete_repo(args):
    ''' delete the repo '''
    url = 'http://' + args.get('server') + '/api/repo/' + args.get('uuid')
    response = requests.delete(url, params={'imsure': 'true'})
    if response.status_code == 200:
        print 'repo %s removed' % args.get('uuid')

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Delete a repo')
    parser.add_argument('--server', required=True, help='dvid server url')
    parser.add_argument('--repo', required=True, dest='uuid', help='the uuid of the repository to be removed.')
    cl_args = vars(parser.parse_args())
    delete_repo(cl_args)
