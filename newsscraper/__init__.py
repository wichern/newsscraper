#!/usr/bin/env python3

'''newsscraper

Copyright (C) 2019 Paul Wichern
This code is published under the MIT license.
'''

__version__ = "0.1.3"

import argparse
from bs4 import BeautifulSoup
import csv
import datetime
import json
import os
import pickle
from selenium import webdriver
import sys
import urllib.request
import uuid

def default_report(items, output, report_type):
    '''Create a report.

    Takes the provided ``items`` and writes a report of type ``report_type``
    to ``output``.

    Args:
        items (list):       List of item objects.
        output (stream):    Destination for report string.
        report_type (str):  Type of output (e.g. "json", "html", "csv")
    '''

    if report_type == 'json':
        json.dump(items, output, indent=4)
    elif report_type == 'csv':
        writer = csv.DictWriter(output, items.keys())
        writer.writeheader()
        writer.writerow(items)
    elif report_type == 'html':
        template_path = os.path.dirname(os.path.abspath(__file__)) + '/report.html'
        with open(template_path, 'r') as infile:
            template = infile.read()
            output.write(template.replace('__ITEMS__', json.dumps(items)))

# pylint: disable=too-many-instance-attributes
class Scraper(object):
    '''Scraper

    Create a new Scraper module form which web drivers our a soup can be
    optained and that stores all collected news items.
    '''

    def __init__(self, \
                 argv, \
                 parser=argparse.ArgumentParser(prog='pyscraper'), \
                 report=default_report,
                 script=None):
        '''Constructor
        Args:
            argv (list):                Typically just sys.argv.
            parser (argument parser):   Override the default argparser to add
                                        custom arguments to a script.
            report (func):              Report creation function.
            script (str):               Script name (defaults to argv[0]).
        '''

        parser.add_argument('--out', \
                            type=argparse.FileType('w'), \
                            default=sys.stdout, help='Report output')
        parser.add_argument('--report', \
                            type=str, \
                            default='json', \
                            help='Report type (json|csv|html). Default: json')
        parser.add_argument('--headless', \
                            action='store_true')
        parser.add_argument('--verbose', \
                            action='store_true', \
                            help='Print some logs')
        parser.add_argument('--dry', \
                            action='store_true', \
                            help='Do not add keys to list of known keys. Do not download anything.')
        parser.add_argument('--pickle', \
                            type=str, \
                            default='./.pickle/__script__.pickle', \
                            help='Pickle file containing all known urls.')
        parser.add_argument('--download_dir', \
                            type=str, \
                            default='./downloads/__script__/')
        parser.add_argument('--asset_dir', \
                            type=str, \
                            default='./assets/')
        parser.add_argument('--clear', \
                            action='store_true', \
                            help='Clear all known keys.')

        self.report = report
        self.args = parser.parse_args(argv[1:])

        if self.args.verbose and self.args.out == sys.stdout:
            raise ValueError('Should not use --verbose with stdout output.')

        if script:
            self.script = script
        else:
            self.script = os.path.splitext(os.path.basename(argv[0]))[0]
        self.pickle = self.args.pickle.replace('__script__', self.script)
        self.download_dir = self.args.download_dir.replace('__script__', self.script)

        self.keys = set()
        if os.path.exists(self.pickle):
            if self.args.clear:
                os.remove(self.pickle)
            else:
                with open(self.pickle, 'rb') as infile:
                    data = pickle.load(infile)
                    self.keys = data['keys']
                    self.say('Opened {:s} from {:s}'.format(self.pickle, data['date']))

        self.items = []
        self.firefox = None
        self.chrome = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if self.firefox:
            self.firefox.close()
        if self.chrome:
            self.chrome.close()
        if exc_type:
            return

        # Write report.
        self.say('Report {:d} items.'.format(len(self.items)))
        self.report(self.items, self.args.out, self.args.report)

        if not self.args.dry:
            # Write pickle.
            pickle_path = os.path.dirname(os.path.abspath(self.pickle))
            if not os.path.exists(pickle_path):
                os.makedirs(pickle_path)
            with open(self.pickle, 'wb') as outfile:
                pickle.dump({
                    'keys': self.keys,
                    'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }, outfile)

    def __contains__(self, key):
        return key in self.keys

    def download(self, url, dest=None, overwrite=False):
        '''Download file.

        Args:
            url (str):          The remote files URL.
            dest (str):         Destination path.
                                Defaults to './downloads/' and the original file name.
            overwrite (bool)    Whether to overwrite an existing local file.
        '''
        if self.args.dry:
            return
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
        if not dest:
            dest = url[url.rfind("/")+1:]
        dest_path = self.download_dir + dest
        if overwrite == False and os.path.exists(dest_path):
            raise ValueError('{:s} already exists.'.format(dest_path))
        urllib.request.urlretrieve(url, dest_path)

    def get_soup(self, url, parser='html.parser', header={'User-Agent': 'Mozilla/5.0'}):
        request = urllib.request.Request(url, header)
        return BeautifulSoup(urllib.request.urlopen(url), parser)

    def get_firefox(self, width=1024, heigth=768):
        if not self.firefox:
            options = webdriver.FirefoxOptions()
            options.headless = self.args.headless
            options.add_argument('--width={:d}'.format(width))
            options.add_argument('--height={:d}'.format(heigth))
            profile = webdriver.FirefoxProfile()
            for extension in os.listdir(self.args.asset_dir):
                if extension.endswith('.xpi'):
                    self.say('Add firefox extension: {:s}'.format(extension))
                    profile.add_extension(self.args.asset_dir + extension)
            self.firefox = webdriver.Firefox(
                executable_path=self.args.asset_dir + 'geckodriver',
                options=options,
                firefox_profile=profile)
        return self.firefox

    def get_chrome(self, width=1024, heigth=768):
        if not self.chrome:
            options = webdriver.ChromeOptions()
            if self.args.headless:
                # Headless chrome does not support extensions.
                options.add_argument('headless')
            else:
                for extension in os.listdir(self.args.asset_dir):
                    if extension.endswith('.crx'):
                        self.say('Add chrome extension: {:s}'.format(extension))
                        options.add_extension(self.args.asset_dir + extension)
            options.add_argument('window-size={:d},{:d}'.format(width, heigth))
            self.chrome = webdriver.Chrome(
                self.args.asset_dir + 'chromedriver', \
                chrome_options=options)
        return self.chrome

    def add(self, *,
            key,
            title='',
            url='',
            thumb='',
            tags=[],
            date=datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            data=dict(),
            script=None):
        '''Add item to report.

        An item with an already known key will be ignored.

        Args:
            key (str):      A unique key for this item.
                            Different scripts can use the same keys.
            title (str):    Item title.
            url (str):      The url to follow if interested.
            thumb (str):    Path to a thumbnail picture.
            tags (list):    Tags.
            date (date):    Item date (default: now())
            data (dict):    Additional key-value pairs that shall be added to
                            the item.
            script (str):   Override the script name.
        '''
        if key in self.keys:
            return

        self.say('+ {:s}'.format(title if title else key))
        self.keys.add(key)
        item = { 'script': script if script else self.script }
        if title:
            item['title'] = title
        if url:
            item['url'] = url
        if thumb:
            item['thumb'] = thumb
        if tags:
            item['tags'] = tags
        if date:
            item['date'] = date
        if data:
            item.update(data)
        self.items.append(item)

    def say(self, msg):
        if self.args.verbose:
            print(msg)

# ------------------------------------------------------------------------------

def merge_results(inputs, output):
    items = []

    for file in inputs:
        if os.stat(file).st_size == 0:
            continue
        with open(file, 'r', encoding='utf-8') as infile:
            items += json.load(infile)

    with open(output, 'w') as out:
        json.dump(items, out, indent=4)
