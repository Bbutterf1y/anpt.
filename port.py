#!/usr/bin/env python

import nmap

scan_range='127.0.0.1'
scan_ports='22,23,53,80,443,445'

nm=nmap.PortScanner()
f=nm.scan(scan_range, scan_ports)

print(f)



