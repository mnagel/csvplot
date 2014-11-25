#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import code
import csv
import datetime
import matplotlib
import matplotlib.pyplot as plot
import numpy
import re
import sys

parser = argparse.ArgumentParser(prog='csvplot')
parser.add_argument('--x', default=1, type=int)
parser.add_argument('--xtransform', default="float", type=str)
parser.add_argument('--y', default=2, type=int)
parser.add_argument('--ytransform', default="float", type=str)
parser.add_argument('--infile', default=None, type=str)
parser.add_argument('--outfile', default=None, type=str)
parser.add_argument('--show', default=False, action="store_true")
parser.add_argument('--marker', default='.', type=str)
parser.add_argument('--interact', default=False, action="store_true")
parser.add_argument('--sep', default=",", type=str)

options = parser.parse_args()

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
        match = re.match(exp, value)
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

#Direct input 
matplotlib.pyplot.rcParams['text.latex.preamble']=[r"\usepackage{lmodern}"]
#Options
params = {'text.usetex' : True,
          'font.size' : 11,
          'font.family' : 'lmodern',
          'text.latex.unicode': True,
          }
matplotlib.pyplot.rcParams.update(params) 

figure = plot.figure()
subplot = figure.add_subplot(111)

if options.xtransform == "date":
    subplot.plot_date(x,y, c="gray", marker=options.marker, antialiased=True)
else:
    subplot.scatter(x,y, c="gray", marker=options.marker, antialiased=True)

#subplot.set_xlim([1.1 * numpy.amin(x) - 1, 1.1 * numpy.amax(x) + 1])
subplot.set_ylim([1.1 * numpy.amin(y) - 1, 1.1 * numpy.amax(y) + 1])

subplot.set_xlabel(r.fieldnames[options.x])
subplot.set_ylabel(r.fieldnames[options.y])

if options.xtransform == "date":
    subplot.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y-%m-%d\n%H:%M:%S'))
#subplot.yaxis.set_major_locator(MultipleLocator(options.ystep))

box = "tight"
pad = 0.2
if options.outfile is not None:
    print("should save")
    sys.exit(1)
    plot.savefig(filename , figsize=(8, 8), dpi=1000, bbox_inches=box, pad_inches=pad)
    print("saved to %s" % filename)

if options.show:
    plot.show()

if options.interact:
    code.interact(local=locals())

if not options.show and not options.outfile:
    print("we basically just did a syntax check. set --show or --save.")
