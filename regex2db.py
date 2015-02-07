#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import logging
import re
import sqlite3
import sys

def read_arguments(args):
    parser = argparse.ArgumentParser()

    parser.add_argument('--dbfile', required=True, type=str)
    parser.add_argument('--truncate', default=False, action='store_true')
    parser.add_argument('--regex', required=True, type=str)
    parser.add_argument('--tablename', required=True, type=str)
    parser.add_argument('--capture', nargs=3, action='append')
    parser.add_argument('infile', nargs='+')

    parser.add_argument('-d','--debug', action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING)
    parser.add_argument('-v','--verbose', action="store_const",dest="loglevel", const=logging.INFO)

    options = parser.parse_args(args)
    return options

def processLine(line, con, cur):
    m = re.match(options.regex, line)
    if m:
        logging.debug("matched line %s" % line.rstrip())
        # print(m)
        pairs = {}
        for cap in options.capture:
            idx = int(cap[0])
            val = m.group(idx)
            tfx = cap[1]
            col = cap[2]
            logging.debug("appling tfx %s to val %s and putting it into col %s" % (tfx, val, col))
            tfxval = val # TODO fixme
            pairs[col] = tfxval

        writeLineToDb(con, cur, options.tablename, pairs)
        return True
    return False

def writeLineToDb(con, cur, table, col_val_dict):
    columns = ', '.join(col_val_dict.keys())
    placeholders = ':' + ( ', :'.join(col_val_dict.keys()) )
    query = 'INSERT INTO %s (%s) VALUES (%s)' % (table, columns, placeholders)
    logging.debug('qry: %s' % query)
    cur.execute(query, col_val_dict)

def processFile(file, con, cur):
        matchcount = 0
        with open(file) as f:
            for line in f:
                if processLine(line, con, cur):
                    matchcount += 1
        logging.info("matched %d lines" % matchcount)

def main(options):
    logging.info("files are: %s" % options.infile)
    logging.info("captures are: %s" % options.capture)

    con = sqlite3.connect(options.dbfile)
    cur = con.cursor()

    if options.truncate:
        logging.warning("!!! TRUNCATING !!!")
        # TODO check the whole program for major sql injections
        cur.execute('DELETE FROM %s' % options.tablename)

    for file in options.infile:
        logging.info("processing file %s" % file)
        processFile(file, con, cur)

    con.commit()

if __name__ == '__main__':
    options = read_arguments(sys.argv[1:])
    logging.basicConfig(level=options.loglevel)
    main(options)
