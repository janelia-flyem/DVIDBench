DVID Bench
===========

Benchmarking tool for checking response times of a DVID server.

Prerequisites
=============

Installation
============

```bash
> python setup.py install
```

Usage
=====

```bash
> dvid-bench --master
> dvid-bench --slave
```

Configuration File
==================

The configuration file contains all the important settings needed to get the correct
benchmark run.

It is written in JSON and has the following required fields:

+ urls
+ logs

Here is an example:

```json
{
  "urls": [
    "http://localhost:4000"
  ],
  "logs": "/tmp/dvid-bench"
}
```
