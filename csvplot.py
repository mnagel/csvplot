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

parser = argparse.ArgumentParser(prog='csvplot')
parser.add_argument('--title', default="simple plot by csvplot", type=str)
parser.add_argument('--x', default=1, type=int)
parser.add_argument('--xtransform', default="float", type=str)
parser.add_argument('--xlog', default=False, action="store_true")
parser.add_argument('--xlabel', default="x-values", type=str)
parser.add_argument('--y', default=2, type=int)
parser.add_argument('--ytransform', default="float", type=str)
parser.add_argument('--ylog', default=False, action="store_true")
parser.add_argument('--ylabel', default="y-values", type=str)
parser.add_argument('--infile', default=None, type=str)
parser.add_argument('--outfile', default=None, type=str)
parser.add_argument('--show', default=False, action="store_true")
parser.add_argument('--marker', default='.', type=str)
parser.add_argument('--interact', default=False, action="store_true")
parser.add_argument('--sep', default=",", type=str)
parser.add_argument('--nolatex', default=False, action="store_true")

options = parser.parse_args()

# need options before matplotlib can be imported
if not options.show:
    matplotlib.use('Agg') # allow creating pngs without X server
import matplotlib.pyplot as plot

# csvplot columns are indexed 1-based
options.x = options.x - 1
options.y = options.y - 1

numpy.set_printoptions(linewidth=200)
numpy.set_printoptions(suppress=True)
numpy.set_printoptions(precision=5)

if options.infile is None:
    exit("--infile argument is mandatory")

r = csv.DictReader(open(options.infile), delimiter=options.sep)
# index to name
i2n = r.fieldnames

# TODO move the supported transformers elsewhere
def transform(value, transformation):
    if transformation == "float":
        return float(value)
    if transformation == "date":
        dt = datetime.datetime.strptime(value, '%Y-%m-%d@%H:%M:%S')
        timestamp = matplotlib.dates.date2num(dt)
        return timestamp
    if transformation == "ping":
        exp = "time=([0-9.]+)"
        try:
            match = re.match(exp, value)
        except:
            print("regex did not work on value %s" % (value))
            return None
        #print("line is %s and regex is %s" % (value, exp))
        #print(match.group(1))
        return transform(match.group(1), "float")
    return value

x,y = [],[]
for line in r:
    xval = line[i2n[options.x]]
    yval = line[i2n[options.y]]
    xt = transform(xval, options.xtransform)
    yt = transform(yval, options.ytransform)
    if xt is None or yt is None:
        print("could not process line %s" % line)
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

subplot = figure.add_subplot(111)

if options.xtransform == "date":
    subplot.plot_date(x,y, c="blue", marker=options.marker, antialiased=True)
else:
    subplot.scatter(x,y, c="blue", marker=options.marker, antialiased=True)

dx = numpy.amax(x) - numpy.amin(x)
dy = numpy.amax(y) - numpy.amin(y)
subplot.set_xlim([numpy.amin(x) - 0.05*dx, numpy.amax(x) + 0.05*dx])
subplot.set_ylim([numpy.amin(y) - 0.05*dy, numpy.amax(y) + 0.05*dy])

subplot.set_xlabel(r.fieldnames[options.x])
subplot.set_ylabel(r.fieldnames[options.y])

if options.xlog:
    subplot.set_xscale('log')
if options.ylog:
    subplot.set_yscale('log')

subplot.grid(True)
subplot.set_title(options.title, fontsize=30)
subplot.set_xlabel(options.xlabel, fontsize=20)
subplot.set_ylabel(options.ylabel, fontsize=20)

if options.xtransform == "date":
    subplot.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d\n%H:%M:%S'))
#subplot.yaxis.set_major_locator(MultipleLocator(options.ystep))

box = "tight"
pad = 0.2
if options.outfile is not None:
    plot.savefig(options.outfile , figsize=(8, 8), dpi=1000, bbox_inches=box, pad_inches=pad)
    print("saved to %s" % options.outfile)

if options.show:
    plot.show()

if options.interact:
    code.interact(local=locals())

if not options.show and not options.outfile:
    print("we basically just did a syntax check. set --show or --outfile.")
