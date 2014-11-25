csvplot
=======

csvplot helps you to plot data in plaintext/csv format. 
Plots are customizable using csvplot features
or by dropping back to Python/matplotlib functionality.

Basically, this means that csvplot is partially an application, partially a framework.

Plots can be re-generated when the data changes.

csvplot is written in Python and based on numpy/matplotlib.

Example
=======

```
python csvplot.py --infile data3.csv --show --y 9 --sep " " --xtransform date --ytransform ping
```

Screenshot
----------

![csvplot screenshot](https://raw.githubusercontent.com/mnagel/csvplot/master/doc/ping.png "csvplot screenshot")

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

TBD