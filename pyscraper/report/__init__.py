#!/usr/bin/env python3

import csv
import json
import os

class HTML5Report(object):
    def __init__(self, input):
        self.items = json.load(input)
        template_path = os.path.dirname(os.path.abspath(__file__)) + '/report.html'
        with open(template_path, 'r') as infile:
            self.template = infile.read()

    def write(self, output):
        output.write(self.template.replace('__ITEMS__', json.dumps(self.items)))

class CSVReport(object):
    def __init__(self, input):
        self.items = json.load(input)

    def write(self, output):
        writer = csv.DictWriter(output, self.items.keys())
        writer.writeheader()
        writer.writerow(self.items)
