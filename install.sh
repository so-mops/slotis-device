#!/bin/bash

cp src/perl/controllino.pm /usr/local/lib/site_perl
cp src/perl/roof.pm /usr/local/lib/site_perl
cp src/perl/status_client.pm /usr/local/lib/site_perl
cp src/perl/slotis_email.pm /usr/local/lib/site_perl

cp systemd/slotisSafe.service /etc/systemd/system
systemctl enable slotisSafe
systemctl daemon-reload
python setup.py install
