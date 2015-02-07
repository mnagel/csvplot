#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import code
import csv
import datetime
import matplotlib
# import happens later
#import matplotlib.pyplot as plot
import numpy
import re

import sys
import sqlite3

def read_arguments(args):
    parser = argparse.ArgumentParser()

    parser.add_argument('--dbfile', required=True, type=str)
    parser.add_argument('--regex', required=True, type=str)
    parser.add_argument('--tablename', required=True, type=str)
    parser.add_argument('--capture', nargs=3, action='append')
    parser.add_argument('infile', nargs='+')

    options = parser.parse_args(args)
    return options

def processLine(line, con, cur):
    m = re.match(options.regex, line)
    if m:
        print("matched line %s" % line)
        print(m)
        pairs = {}
        for cap in options.capture:
            idx = int(cap[0])
            val = m.group(idx)
            tfx = cap[1]
            col = cap[2]
            print("appling tfx %s to val %s and putting it into col %s" % (tfx, val, col))
            tfxval = val # TODO fixme
            pairs[col] = tfxval

        writeLineToDb(con, cur, options.tablename, pairs)
        return True
    return False

def writeLineToDb(con, cur, table, col_val_dict):
    columns = ', '.join(col_val_dict.keys())
    placeholders = ':' + ( ', :'.join(col_val_dict.keys()) )
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (table, columns, placeholders)
    print('qry: %s' % query)
    cur.execute(query, col_val_dict)
    # con.commit() # TODO check if good idea

def processFile(file, con, cur):
        matchcount = 0
        with open(file) as f:
            for line in f:
                if processLine(line, con, cur):
                    matchcount += 1
        print("matched %d lines" % matchcount)

def main(options):


    print("files are: %s" % options.infile)
    print("captures are: %s" % options.capture)


    con = sqlite3.connect(options.dbfile)
    cur = con.cursor()

    for file in options.infile:
        print("processing file %s" % file)
        processFile(file, con, cur)

    con.commit()

if __name__ == '__main__':
    options = read_arguments(sys.argv[1:])
    main(options)
