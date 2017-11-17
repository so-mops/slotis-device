#!/bin/bash

cp src/perl/controllino.pm /usr/local/lib/site_perl
cp src/perl/roof.pm /usr/local/lib/site_perl
cp src/perl/status_client.pm /usr/local/lib/site_perl
python setup.py install
