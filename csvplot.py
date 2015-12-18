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
import sqlite3

def add_common_arguments(parser):
    parser.add_argument('--title', help="graph title", default="simple plot by csvplot", type=str)
    parser.add_argument('--xsize', help="size of graph", default=8, type=int)
    parser.add_argument('--xtransform', help="transformation to apply to x values (float/date/ping)", default="float", type=str)
    parser.add_argument('--xlog', help="ise logarithmic x axis", default=False, action="store_true")
    parser.add_argument('--xlabel', help="label for x axis", default="x-values", type=str)
    parser.add_argument('--ysize', help="size of graph", default=6, type=int)
    parser.add_argument('--ytransform', help="see xtransform", default="float", type=str)
    parser.add_argument('--ylog', help="use logarithmic y axis", default=False, action="store_true")
    parser.add_argument('--ylabel', help="label for y axis", default="y-values", type=str)
    parser.add_argument('--outfile', help="file to save plot to", default=None, type=str)
    parser.add_argument('--show', help="if set, opens plot in an interactive window", default=False, action="store_true")
    parser.add_argument('--marker', help="matplotlib marker style ala ./x/o", default='.', type=str)
    parser.add_argument('--linestyle', help="matplotlib line style ala ''/-/.", default='', type=str)
    parser.add_argument('--interact', help="if set, drop to python shell before plotting", default=False, action="store_true")
    parser.add_argument('--nolatex', help="if set, no latex is required to run", default=False, action="store_true")
    parser.add_argument('--dateformat', help="the date format used to parse dates", default='%Y-%m-%d@%H:%M:%S', type=str)
    parser.add_argument('--datelocator', help="where to put date markers ala auto/day/minute", default="auto", type=str)
0
parser = argparse.ArgumentParser(prog='csvplot', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

subparsers = parser.add_subparsers(dest="operationmode")
# workaround http://stackoverflow.com/a/23354355/2536029
subparsers.required = True
sql_parser = subparsers.add_parser('sqlmode', help="plot sql data", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
sql_parser.add_argument('--dbfile', help="db file to open", required=True, type=str)
sql_parser.add_argument('--sql', help="sql query that returns (at least) 'x' and 'y' column", required=True, type=str)
add_common_arguments(sql_parser)

csv_parser = subparsers.add_parser('csvmode', help="plot csv data", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
csv_parser.add_argument('--sep', help="seperator used in csv file ala ','/' '/'\\t'", default=",", type=str)
csv_parser.add_argument('--x', dest='x', help="index of column with x values", default=1, type=int)
csv_parser.add_argument('--y', dest='y', help="index of column with y values", default=2, type=int)
csv_parser.add_argument('--infile', help="csv file to open", default=None, type=str)
add_common_arguments(csv_parser)

options = parser.parse_args()

if options.operationmode == "csvmode":
    # csvplot columns are indexed 1-based
    options.x = options.x - 1
    options.y = options.y - 1

    if options.infile is None:
        exit("--infile argument is mandatory")

    if options.sep == '\\t':
        options.sep = '\t'

    r = csv.DictReader(open(options.infile), delimiter=options.sep)
    # index to name
    i2n = r.fieldnames

elif options.operationmode == "sqlmode":
    def dict_factory(cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    print('connecting to %s' % options.dbfile)
    con = sqlite3.connect(options.dbfile)
    con.row_factory = dict_factory
    cur = con.cursor()
    print('execing: %s' % options.sql)
    rs = cur.execute(options.sql)

# need options before matplotlib can be imported
if not options.show:
    matplotlib.use('Agg') # allow creating pngs without X server
import matplotlib.pyplot as plot

numpy.set_printoptions(linewidth=200)
numpy.set_printoptions(suppress=True)
numpy.set_printoptions(precision=5)

# TODO move the supported transformers elsewhere
def transform(value, transformation):
    if transformation == "float":
        return float(value)
    if transformation == "date":
        dt = datetime.datetime.strptime(value, options.dateformat)
        timestamp = matplotlib.dates.date2num(dt)
        return timestamp
    if transformation == "ping":
        exp = "time=([0-9.]+)"
        try:
            match = re.match(exp, value)
            return transform(match.group(1), "float")
        except:
            print("regex did not work on value %s" % (value))
            return None
    return value

if options.operationmode == "csvmode":
    allmylines = r
    xind = i2n[options.x]
    yind = i2n[options.y]
elif options.operationmode == "sqlmode":
    allmylines = iter(rs.fetchone, None)
    xind = 'x'
    yind = 'y'

print('fetching')
x,y = [],[]
cnt = 0
for res in allmylines:
    cnt += 1
    if not cnt % 1000:
        print("got to iteration %d" % cnt)
        print(res)

    xval = res[xind]
    yval = res[yind]
    xt = transform(xval, options.xtransform)
    yt = transform(yval, options.ytransform)
    if xt is None or yt is None:
        print("could not process line %s" % res)
        continue
    x.append(xt)
    y.append(yt)

x = numpy.array(x)
y = numpy.array(y)

print("x has length %s" % len(x))
print("y has length %s" % len(y))
print("x is %s" % x)
print("y is %s" % y)

if options.interact:
    code.interact(local=locals())

if not options.nolatex:
    #Direct input
    matplotlib.pyplot.rcParams['text.latex.preamble']=[r"\usepackage{lmodern}"]
    #Options
    params = {
        'text.usetex' : True,
        'font.size' : 11,
        'font.family' : 'lmodern',
        'text.latex.unicode': True,
    }
    matplotlib.pyplot.rcParams.update(params)

figure = plot.figure(figsize=(options.xsize, options.ysize))
subplot = figure.add_subplot(111)

if options.xtransform == "date":
    subplot.plot_date(x,y, c="blue", marker=options.marker, linestyle=options.linestyle,  antialiased=True)
else:
    subplot.scatter(x,y, c="blue", marker=options.marker, antialiased=True)

dx = numpy.amax(x) - numpy.amin(x)
dy = numpy.amax(y) - numpy.amin(y)
subplot.set_xlim([numpy.amin(x) - 0.05*dx, numpy.amax(x) + 0.05*dx])
subplot.set_ylim([numpy.amin(y) - 0.05*dy, numpy.amax(y) + 0.05*dy])

if options.xlog:
    subplot.set_xscale('log')
if options.ylog:
    subplot.set_yscale('log')

subplot.grid(True)
subplot.set_title(options.title, fontsize=30)
subplot.set_xlabel(options.xlabel, fontsize=20)
subplot.set_ylabel(options.ylabel, fontsize=20)

if options.xtransform == "date":
    plot.xticks(rotation=30)
    if options.datelocator == 'day':
        loccer = matplotlib.dates.DayLocator()
    elif options.datelocator == 'minute':
        loccer = matplotlib.dates.MinuteLocator(interval=5)
    else:
        loccer = matplotlib.dates.AutoDateLocator()
    loccer.MAXTICKS = 2000
    subplot.xaxis.set_major_locator(loccer)
    subplot.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(options.dateformat))

box = "tight"
pad = 0.2
if options.outfile is not None:
    plot.savefig(options.outfile, dpi=80, bbox_inches=box, pad_inches=pad)
    print("saved to %s" % options.outfile)

if options.show:
    plot.show()

if options.interact:
    code.interact(local=locals())

if not options.show and not options.outfile:
    print("we basically just did a syntax check. set --show or --outfile.")
