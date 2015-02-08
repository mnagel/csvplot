csvplot
=======

csvplot helps you to plot data in plaintext/csv format.
Plots are customizable using csvplot features
or by dropping back to Python/matplotlib functionality.

Basically, this means that csvplot is partially an application, partially a framework.

Plots can be re-generated when the data changes.

csvplot is written in Python and based on numpy/matplotlib.



Simple Example
==============

Input is structured like this:
```
x,y
1,1
2,2
3,3
4,2
5,1
6,2
7,3
```

```
python csvplot.py csvmode --infile doc/data.csv --show
```

Screenshot
----------

![csvplot screenshot](https://raw.githubusercontent.com/mnagel/csvplot/master/doc/data.png "csvplot screenshot")



Real Example
============

Input is structured like this:
```
timestamp, num, bytes, from, host, ip, seq, ttl, ping, ms
2014-11-25@19:56:13 64 bytes from redirector.heise.de (193.99.144.80): icmp_seq=3395 ttl=245 time=120 ms
2014-11-25@19:56:14 64 bytes from redirector.heise.de (193.99.144.80): icmp_seq=3396 ttl=245 time=106 ms
2014-11-25@19:56:15 64 bytes from redirector.heise.de (193.99.144.80): icmp_seq=3397 ttl=245 time=17.9 ms
```

To obtain data like this yourself, run:
```
ping heise.de | while read pong; do echo "$(date '+%Y-%m-%d@%H:%M:%S') $pong"; done >> doc/ping.csv
```
You need to manually add the first header line and remove trailing statistics output added by `ping` (last few lines).

```
python csvplot.py csvmode --infile doc/ping.csv --y 9 --sep " " --xtransform date --ytransform ping --title "scatterplot of latency to heise.de" --xlabel "timestamp" --ylabel "latency [ms]" --show
```

Screenshot
----------

![csvplot screenshot](https://raw.githubusercontent.com/mnagel/csvplot/master/doc/ping.png "csvplot screenshot")



SQL Mode
========

`regex2db.py` allows to parse textfiles by regular expressions and write the data to a sqlite database.
`csvplot.py` supports a special `sqlmode` that allows reading data from a sqlite database.

The following example is basic as the power of SQL is not really used, but the principle should be clear.

The above ping example can be solved using the sqlite way as follows:

```
# create a database with suitable schema.
# any schema can be used

sqlite3 ping.sqlite <<EOF
CREATE TABLE data1 (timestamp TEXT, host TEXT, ip TEXT, ping REAL);
.exit
EOF


# fill the database from a log file.

python regex2db.py --dbfile ping.sqlite --tablename data1 --truncate \
  --capture 1 date timestamp \
  --capture 2 string host \
  --capture 3 string ip \
  --capture 4 float ping \
  --regex '(\S{19}) 64 bytes from (\S+) \(([0-9.]+)\): icmp_seq=\d+ ttl=\d+ time=([0-9.]+) ms' \
  doc/ping.csv


# run the csvplot in sqlmode.

python csvplot.py sqlmode --dbfile ping.sqlite --sql 'select timestamp as x, ping as y from data1;' --xtransform date --title "scatterplot of latency to heise.de" --xlabel "timestamp" --ylabel "latency [ms]" --show
```

The SQL statement can have any complexity, but must select rows with (at least) the columns `x` and `y` containing the data to plot.



Installation
============

* Install the dependecies

```
sudo apt-get install python-matplotlib
```

Save csvplot.py anywhere and run it as described in the examples or the usage section.



Usage
=====

```
$ python csvplot.py csvmode -h
usage: csvplot csvmode [-h] [--sep SEP] [--x X] [--y Y] [--infile INFILE]
[--title TITLE] [--xsize XSIZE]
[--xtransform XTRANSFORM] [--xlog] [--xlabel XLABEL]
[--ysize YSIZE] [--ytransform YTRANSFORM] [--ylog]
[--ylabel YLABEL] [--outfile OUTFILE] [--show]
[--marker MARKER] [--linestyle LINESTYLE] [--interact]
[--nolatex] [--dateformat DATEFORMAT]
[--datelocator DATELOCATOR]

optional arguments:
-h, --help            show this help message and exit
--sep SEP
--x X
--y Y
--infile INFILE
--title TITLE
--xsize XSIZE
--xtransform XTRANSFORM
--xlog
--xlabel XLABEL
--ysize YSIZE
--ytransform YTRANSFORM
--ylog
--ylabel YLABEL
--outfile OUTFILE
--show
--marker MARKER
--linestyle LINESTYLE
--interact
--nolatex
--dateformat DATEFORMAT
--datelocator DATELOCATOR


$ python csvplot.py sqlmode -h
usage: csvplot sqlmode [-h] --dbfile DBFILE --sql SQL [--title TITLE]
[--xsize XSIZE] [--xtransform XTRANSFORM] [--xlog]
[--xlabel XLABEL] [--ysize YSIZE]
[--ytransform YTRANSFORM] [--ylog] [--ylabel YLABEL]
[--outfile OUTFILE] [--show] [--marker MARKER]
[--linestyle LINESTYLE] [--interact] [--nolatex]
[--dateformat DATEFORMAT] [--datelocator DATELOCATOR]

optional arguments:
-h, --help            show this help message and exit
--dbfile DBFILE
--sql SQL
--title TITLE
--xsize XSIZE
--xtransform XTRANSFORM
--xlog
--xlabel XLABEL
--ysize YSIZE
--ytransform YTRANSFORM
--ylog
--ylabel YLABEL
--outfile OUTFILE
--show
--marker MARKER
--linestyle LINESTYLE
--interact
--nolatex
--dateformat DATEFORMAT
--datelocator DATELOCATOR
```



LICENCE
=======

The MIT License (MIT)

Copyright (c) 2014-2015 Michael Nagel and csvplot contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
