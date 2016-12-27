#!/usr/bin/env python
"""
NTC thermistor class

Based on https://pypi.python.org/pypi/thermistor
"""
from __future__ import print_function
import numpy


class NTC(object):
    """Generig NTC"""
    def __init__(self, R0=10, B=3977, T0=298.15, T1=323.15):
        """Basic NTC parameters"""
        self.R0 = float(R0)  # resistence at T0 in [kOhm]
        self.B = float(B)    # 1/beta(T0/T1) coefficient in [K]
        self.T0 = float(T0)  # 25 [*C] in [*K]
        self.T1 = float(T1)  # 50 [*C] in [*K]

    def temperature(self, R, unit='C'):
        """resistance R [kOhm] to temperature [unit]"""
        temp_inv = numpy.log(R/self.R0)/self.B + 1/self.T0
        if unit is 'K':
            return 1/temp_inv
        elif unit is 'C':
            return 1/temp_inv - 273.15
        else:
            print('Unsuported temperature unit "%s"'%unit)
            raise KeyError

    def reststance(self, T, unit='C'):
        """temperature [unit] to resistance R [kOhm] """
        if unit is 'K':
            temp = T
        elif unit is 'C':
            temp = T + 273.15
        else:
            print('Unsuported temperature unit "%s"'%unit)
            raise KeyError
        temp = 1/temp - 1/self.T0
        return numpy.exp(self.B*temp)


    def __str__(self):
        return '%7.3f kOhm at %.1f *C'%(self.R0,self.T0)


class TTC05(NTC):
    """
    TKS TTC05 series
    http://www.thinking.com.tw/documents/en-TTC05.pdf
    """
    @staticmethod
    def catalog(model=None):
        """All NTCs in series"""
        catalog = {
            '005':NTC(.005, 2400), '010':NTC(.010, 2800), '015':NTC(.015, 2800),
            '020':NTC(.020, 2800), '025':NTC(.025, 2900), '045':NTC(.045, 3100),
            '050':NTC(.050, 3100), '060':NTC(.060, 3100), '085':NTC(.085, 3200),
            '090':NTC(.090, 3200), '101':NTC(.100, 3200), '121':NTC(.120, 3300),
            '151':NTC(.150, 3300), '201':NTC(.200, 3500), '221':NTC(.220, 3500),
            '251':NTC(.250, 3500), '301':NTC(.300, 3800), '471':NTC(.470, 3500),
            '501':NTC(.500, 3700), '681':NTC(.680, 3800), '701':NTC(.700, 3800),
            '102':NTC(1.00, 3800), '152':NTC(1.50, 3950), '202':NTC(2.00, 4000),
            '222':NTC(2.20, 4000), '252':NTC(2.50, 4000), '302':NTC(3.00, 4000),
            '332':NTC(3.30, 4000), '402':NTC(4.00, 4000), '472':NTC(4.70, 4050),
            '502':NTC(5.00, 3950), '602':NTC(6.00, 4050), '682':NTC(6.80, 4050),
            '802':NTC(8.00, 4050), '103':NTC(10.0, 4050), '123':NTC(12.0, 4050),
            '153':NTC(15.0, 4150), '203':NTC(20.0, 4250), '303':NTC(30.0, 4250),
            '473':NTC(47.0, 4300), '503':NTC(50.0, 4300), '104':NTC(100., 4400),
            '154':NTC(150., 4500), '204':NTC(200., 4600), '224':NTC(220., 4600),
            '474':NTC(470., 4750),
        }
        if model is None:
            return catalog.keys()
        else:
            return catalog[model]

    def __init__(self, model):
        self.vendor = 'TKS'
        self.series = 'TTC05'
        self.model = "%03d"%int(model)
        self.name = '%s%s'%(self.series, self.model)
        try:
            ntc = self.catalog(self.model)
        except KeyError as error:
            print('Unknown NTC %s%s'%self.name)
            raise error
        super(TTC05, self).__init__(ntc.R0, ntc.B)

    def __str__(self):
        return '%s: %s'%(self.name, super(TTC05, self).__str__())

if __name__ == '__main__':
    import matplotlib.pyplot as plot
    import pandas

    catalog = pandas.DataFrame(
        index=numpy.linspace(25, 75, 100),
    )

    for model in [102, 103, 104]:
        ntc=TTC05(model)
        catalog[ntc.name]=pandas.Series(
            ntc.reststance(catalog.index)*1e3,
            index=catalog.index)

    catalog.plot(logy=False, subplots=False)
    plot.xlabel("temperature [*C]")
    plot.ylabel("resistance [Ohm]")
    plot.savefig('TTC05.png')
    plot.show()
