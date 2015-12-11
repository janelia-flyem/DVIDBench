from setuptools import setup, find_packages

import dvidbench

setup(
    name = 'dvidbench',
    version = dvidbench.__version__,
    author = 'Jody Clements',
    author_email = 'clementsj@janelia.hhmi.org',
    url = 'https://github.com/janelia-flyem/dvid',
    keywords = 'dvid benchmarking',
    install_requires = [
        'argparse',
        'tabulate',
        'requests',
    ],
    packages = find_packages(),
    scripts = ['scripts/dvid-bench'],
    package_data={
        'dvidbench': ['*.dat']
    }
)
