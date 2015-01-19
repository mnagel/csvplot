csvplot
=======

csvplot helps you to plot data in plaintext/csv format. 
Plots are customizable using csvplot features
or by dropping back to Python/matplotlib functionality.

Basically, this means that csvplot is partially an application, partially a framework.

Plots can be re-generated when the data changes.

csvplot is written in Python and based on numpy/matplotlib.



Simple Example
=======

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
python csvplot.py --infile doc/data.csv --show
```

Screenshot
----------

![csvplot screenshot](https://raw.githubusercontent.com/mnagel/csvplot/master/doc/data.png "csvplot screenshot")



Real Example
=======

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
python csvplot.py --infile doc/ping.csv --y 9 --sep " " --xtransform date --ytransform ping --title "scatterplot of latency to heise.de" --xlabel "timestamp" --ylabel "latency [ms]" --show
```

Screenshot
----------

![csvplot screenshot](https://raw.githubusercontent.com/mnagel/csvplot/master/doc/ping.png "csvplot screenshot")



Installation
============

* Install the dependecies

```
sudo apt-get install python-matplotlib
```

Save csvplot.py anywhere and run it as described in the examples or the usage section.



Usage
=====

WIP

```
usage: csvplot [-h] [--x X] [--xtransform XTRANSFORM] [--y Y]
               [--ytransform YTRANSFORM] [--infile INFILE] [--outfile OUTFILE]
               [--show] [--interact] [--sep SEP]

optional arguments:
  -h, --help            show this help message and exit
  --x X
  --xtransform XTRANSFORM
  --y Y
  --ytransform YTRANSFORM
  --infile INFILE
  --outfile OUTFILE
  --show
  --interact
  --sep SEP
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
