from setuptools import setup, find_packages

import dvidbench

setup(
    name = 'dvidbench',
    version = dvidbench.__version__,
    author = 'Jody Clements',
    author_email = 'clementsj@janelia.hhmi.org',
    url = 'https://github.com/janelia-flyem/dvid',
    keywords = 'dvid benchmarking',
    install_requires = ['argparse'],
    packages = find_packages(),
    package_data = {
      '': [ '*.dat' ]
    },
    scripts = ['scripts/dvid-bench'],
)
