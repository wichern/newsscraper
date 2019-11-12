#!/usr/bin/env python3

import pyscraper
import sys

report = 'report.json'
if len(sys.argv) > 1:
    report = sys.argv[1]

output = 'report.html'
if len(sys.argv) > 2:
    output = sys.argv[2]

pyscraper.html_report(report, output)