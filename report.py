#!/usr/bin/env python3

import pyscraper.report
import sys
import tempfile
import os

input = sys.argv[1]
if len(sys.argv) > 2:
    fd, path = tempfile.mkstemp()
    pyscraper.merge_results(sys.argv[1:], path)
    input = path
    os.close(fd)

pyscraper.report.HTML5Report(input).write(sys.stdout)
