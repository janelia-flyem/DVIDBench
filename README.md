DVID Bench
===========

Benchmarking tool for checking response times of a DVID server.

Prerequisites
=============

+ [siege](https://www.joedog.org/siege-home/)

> OSX Note: It seems OSX 10.10 has issues when compiling siege.
> to get around this disable ssl support in siege:
> ./configure --prefix=/opt --without-ssl

Installation
============

```bash
> python setup.py install
```

Usage
=====

```bash
> dvid-bench /path/to/config/file
```

Configuration File
==================

The configuration file contains all the important settings needed to get the correct
benchmark run.

It is written in JSON and has the following required fields:

+ host
+ urls
+ logs

Here is an example:

```json
{
  "host": "localhost:4000",
  "urls": [
    "http://localhost:4000"
  ],
  "logs": "/tmp/dvid-bench"
}
```
