#! /usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

import argparse
import code
import csv
# noinspection PyUnresolvedReferences
import datetime
import io
import logging
import matplotlib
# import happens later
# import matplotlib.pyplot as plot
import numpy
import re
import sqlite3
import sys


def read_arguments(args):
    def add_common_arguments(p):
        p.add_argument('--title', help="graph title", default="simple plot by csvplot", type=str)
        p.add_argument('--xsize', help="size of graph", default=8, type=int)
        p.add_argument('--xtransform', help="transformation for x values (float/date/ping)", default="float", type=str)
        p.add_argument('--xlog', help="use logarithmic x axis", default=False, action="store_true")
        p.add_argument('--xlabel', help="label for x axis", default="x-values", type=str)
        p.add_argument('--ysize', help="size of graph", default=6, type=int)
        p.add_argument('--ytransform', help="see xtransform", default="float", type=str)
        p.add_argument('--ylog', help="use logarithmic y axis", default=False, action="store_true")
        p.add_argument('--ylabel', help="label for y axis", default="y-values", type=str)
        p.add_argument('--outfile', help="file to save plot to", default=None, type=str)
        p.add_argument('--show', help="if set, opens plot in an interactive window", default=False, action="store_true")
        p.add_argument('--marker', help="matplotlib marker style ala ./x/o", default='.', type=str)
        p.add_argument('--linestyle', help="matplotlib line style ala ''/-/.", default='', type=str)
        p.add_argument('--interact', help="if set, drop to python shell before plotting",
                       default=False, action="store_true")
        p.add_argument('--nolatex', help="if set, no latex is required to run", default=False, action="store_true")
        p.add_argument('--dateformat', help="date format used to parse dates", default='%Y-%m-%d@%H:%M:%S', type=str)
        p.add_argument('--datelocator', help="where to put date markers ala auto/day/minute", default="auto", type=str)
        p.add_argument('-d', '--debug', help="enable debug output",
                       action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING)
        p.add_argument('-v', '--verbose', help="enable verbose output",
                       action="store_const", dest="loglevel", const=logging.INFO)

    parser = argparse.ArgumentParser(prog='csvplot', formatter_class=argparse.ArgumentDefaultsHelpFormatter)

    subparsers = parser.add_subparsers(dest="operationmode")
    # workaround http://stackoverflow.com/a/23354355/2536029
    subparsers.required = True
    sql_parser = subparsers.add_parser('sqlmode', help="plot sql data",
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    sql_parser.add_argument('--dbfile', help="db file to open", required=True, type=str)
    sql_parser.add_argument('--sql', help="sql query that returns (at least) 'x' and 'y' data", required=True, type=str)
    add_common_arguments(sql_parser)

    csv_parser = subparsers.add_parser('csvmode', help="plot csv data",
                                       formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    csv_parser.add_argument('--sep', help="seperator used in csv file ala ','/' '/'\\t'", default=",", type=str)
    csv_parser.add_argument('--xy', help="index of column for x and y data", nargs=2, action='append', type=int)
    group = csv_parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--infile', help="csv file to open", type=str)
    group.add_argument('--stdin', help="read from stdin", default=False, action="store_true")
    add_common_arguments(csv_parser)

    options = parser.parse_args(args)
    return options


def transform(value, transformation, options):
    if transformation == "float":
        return float(value)
    if transformation == "date":
        dt = datetime.datetime.strptime(value, options.dateformat)
        timestamp = matplotlib.dates.date2num(dt)
        return timestamp
    if transformation == "ping":
        exp = "time=([0-9.]+)"
        # noinspection PyBroadException
        try:
            match = re.match(exp, value)
            return transform(match.group(1), "float", options)
        except Exception:
            print("regex did not work on value %s" % value)
            return None
    return value


def get_arrays_to_plot(pool, xind, yind, options):
    print('get_arrays_to_plot')
    x, y = [], []
    cnt = 0

    for res in pool:
        try:
            cnt += 1
            if not cnt % 1000:
                print("got to iteration %d" % cnt)
                print(res)

            xval = res[xind]
            yval = res[yind]
            xt = transform(xval, options.xtransform, options)
            yt = transform(yval, options.ytransform, options)
            if xt is None or yt is None:
                print("could not process line %s" % res)
                continue
            x.append(xt)
            y.append(yt)
        except Exception as e:
            print(type(res))
            print("problem handling line %d: %s" % (cnt, res))
            raise e

    x = numpy.array(x)
    y = numpy.array(y)

    print("x has length %s" % len(x))
    print("y has length %s" % len(y))
    print("x is %s" % x)
    print("y is %s" % y)

    if options.interact:
        code.interact(local=locals())

    return x, y


def do_once_per_graph(subplot, x, y, index, options, label="some data"):

    colors = ["blue", "green", "red", "cyan", "magenta", "yellow", "black", "white"]
    c = colors[index % len(colors)]

    if options.xtransform == "date":
        subplot.plot_date(x, y, c=c, marker=options.marker, linestyle=options.linestyle, antialiased=True, label=label)
    else:
        if options.linestyle != "":
            logging.warn("--linestyle will not work with scatterplot")
        subplot.scatter(x, y, c=c, marker=options.marker, antialiased=True, label=label)

    dx = numpy.amax(x) - numpy.amin(x)
    dy = numpy.amax(y) - numpy.amin(y)
    subplot.set_xlim([numpy.amin(x) - 0.05 * dx, numpy.amax(x) + 0.05 * dx])
    subplot.set_ylim([numpy.amin(y) - 0.05 * dy, numpy.amax(y) + 0.05 * dy])

    if options.xlog:
        subplot.set_xscale('log')
    if options.ylog:
        subplot.set_yscale('log')


def do_once_per_plot(subplot, options):
    subplot.grid(True)
    subplot.set_title(options.title, fontsize=30)
    subplot.set_xlabel(options.xlabel, fontsize=20)
    subplot.set_ylabel(options.ylabel, fontsize=20)

    if options.xtransform == "date":
        matplotlib.pyplot.xticks(rotation=30)
        if options.datelocator == 'day':
            loccer = matplotlib.dates.DayLocator()
        elif options.datelocator == 'minute':
            loccer = matplotlib.dates.MinuteLocator(interval=5)
        else:
            loccer = matplotlib.dates.AutoDateLocator()
        loccer.MAXTICKS = 2000
        subplot.xaxis.set_major_locator(loccer)
        subplot.xaxis.set_major_formatter(matplotlib.dates.DateFormatter(options.dateformat))

    subplot.legend(loc='center left', bbox_to_anchor=(1, 0.5))

    box = "tight"
    pad = 0.2
    if options.outfile is not None:
        matplotlib.pyplot.savefig(options.outfile, dpi=80, bbox_inches=box, pad_inches=pad)
        print("saved to %s" % options.outfile)

    if options.show:
        matplotlib.pyplot.show()

    if options.interact:
        code.interact(local=locals())

    if not options.show and not options.outfile:
        print("we basically just did a syntax check. set --show or --outfile.")


def prepare_matplotlib(options):
    # noinspection PyGlobalUndefined
    global matplotlib
    # need options before matplotlib can be imported
    if not options.show:
        # allow creating pngs without X server
        # noinspection PyUnresolvedReferences
        matplotlib.use('Agg')
    import matplotlib.pyplot

    numpy.set_printoptions(linewidth=200)
    numpy.set_printoptions(suppress=True)
    numpy.set_printoptions(precision=5)

    if not options.nolatex:
        # Direct input
        matplotlib.pyplot.rcParams['text.latex.preamble'] = [r"\usepackage{lmodern}"]
        # Options
        params = {
            'text.usetex': True,
            'font.size': 11,
            'font.family': 'lmodern',
            'text.latex.unicode': True,
        }
        matplotlib.pyplot.rcParams.update(params)

    figure = matplotlib.pyplot.figure(figsize=(options.xsize, options.ysize))
    subplot = figure.add_subplot(111)
    return subplot


def main(options):
    logging.debug("options are %s" % options)

    if options.operationmode == "csvmode":
        main_csvmode(options)
    else:
        main_sqlmode(options)


def main_csvmode(options):
    subplot = prepare_matplotlib(options)

    if not options.xy:
        options.xy = [[1, 2]]

    if options.sep == '\\t':
        options.sep = '\t'

    index = 0

    if options.stdin:
        alltext = sys.stdin.read()
    else:
        alltext = open(options.infile).read()

    if sys.version_info < (3, 0):
        alltext = alltext.decode('utf8')

    for xy in options.xy:
        logging.info("creating graph for %s" % xy)

        # csvplot columns are indexed 1-based
        xind = xy[0] - 1
        yind = xy[1] - 1

        allmylines = csv.DictReader(io.StringIO(alltext), delimiter=options.sep)
        xindname = allmylines.fieldnames[xind]
        yindname = allmylines.fieldnames[yind]
        x, y = get_arrays_to_plot(allmylines, xindname, yindname, options)

        do_once_per_graph(subplot, x, y, index, options, label=allmylines.fieldnames[yind])
        index += 1

    do_once_per_plot(subplot, options)


def main_sqlmode(options):
    logging.debug("options are %s" % options)
    subplot = prepare_matplotlib(options)

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
    r = cur.execute(options.sql)

    allmylines = iter(r.fetchone, None)
    xind = 'x'
    yind = 'y'

    x, y = get_arrays_to_plot(allmylines, xind, yind, options)
    do_once_per_graph(subplot, x, y, 1, options)

    do_once_per_plot(subplot, options)


if __name__ == '__main__':
    myoptions = read_arguments(sys.argv[1:])
    logging.basicConfig(level=myoptions.loglevel)
    main(myoptions)
