#! /usr/bin/env python

import json


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description='Benchmark a DVID server')
    parser.add_argument('--server', required=True, help='DVID server url')
    cl_args = vars(parser.parse_args())


