#!/usr/bin/env python
# encoding: utf-8
"""
NTC thermistor calculations

TODO:
- voltage calculation for R_load, R_bridge NTC configurations
"""
from __future__ import print_function
import sys
import numpy
import matplotlib.pyplot as plot
import pandas
sys.path.insert(1, "./lib/python")
from Sensor import TTC05

catalog = pandas.DataFrame(
    index=numpy.linspace(25, 75, 100),  # 25 to 75 *C
)

for ntc in [102, 103, 104]:
    ntc=TTC05(ntc)
    print("%s"%ntc)
    catalog[ntc.name] = pandas.Series(
        ntc.resistance(catalog.index, 'C', 'Ω'),
        index=catalog.index,
    )

catalog.plot(logy=False, subplots=False)
plot.xlabel("temperature [°C]")
plot.ylabel("resistance [Ω]")
plot.savefig('TTC05.png')
plot.show()
