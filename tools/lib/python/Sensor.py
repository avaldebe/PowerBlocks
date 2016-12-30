#!/usr/bin/env python
# encoding: utf-8
"""
Sensors:
* NTC thermistor
    * TTC05: TKS TTC05 series
"""
from __future__ import print_function
import numpy
from SI_param import Resistance, Temperature

class Sensor(object):
    """
    Basic sensor object

    TODO
    * add range, accuracy, resolution
    * add vendor information
    """
    pass

class NTC(Sensor):
    """
    Generig NTC
    Based on https://pypi.python.org/pypi/thermistor
    """
    def __init__(self, B, R0, unit='kΩ', T0=298.15, T1=323.15, name=None):
        """Basic NTC parameters"""
        self.B = float(B)       # beta(T0/T1) coefficient in [K]
        self.R0 = Resistance.convert_unit(R0, unit, 'kΩ') # resistence at T0 in [kΩ]
        self.T0 = float(T0)     # 25 [*C] in [*K]
        self.T1 = float(T1)     # 50 [*C] in [*K]
        self.name = name if name else 'NTC%d'%self.B
#       self.R1 = self.resistance(self.T1, 'K')

    def temperature(self, R, r_unit='kΩ', t_unit='C'):
        """resistance R [kΩ] to temperature [unit]"""
        r_kohm = Resistance.convert_unit(R, r_unit, 'kΩ')
        temp_inv = numpy.log(r_kohm/self.R0)/self.B + 1/self.T0
        return Temperature.convert_unit(1/temp_inv, 'K', t_unit)

    def resistance(self, T, t_unit='C', r_unit='kΩ'):
        """temperature [unit] to resistance R [kΩ] """
        temp = Temperature.convert_unit(T, t_unit, 'K')
        temp = 1/temp - 1/self.T0
        r_kohm = numpy.exp(self.B*temp)
        return Resistance.convert_unit(r_kohm, 'kΩ', r_unit)

    def __str__(self):
        t0 = Temperature(self.T0, 'K').unit('C')
        r0 = Resistance(self.R0, 'kΩ')
        return '%s(%s)=%s'%(self.name, t0, r0)


class TTC05(NTC):
    """
    TKS TTC05 series
    http://www.thinking.com.tw/documents/en-TTC05.pdf
    """
    _catalog = { # SMD_code:beta_coff
        '005':2400, '010':2800, '015':2800, '020':2800, '025':2900, '045':3100,
        '050':3100, '060':3100, '085':3200, '090':3200, '101':3200, '121':3300,
        '151':3300, '201':3500, '221':3500, '251':3500, '301':3800, '471':3500,
        '501':3700, '681':3800, '701':3800, '102':3800, '152':3950, '202':4000,
        '222':4000, '252':4000, '302':4000, '332':4000, '402':4000, '472':4050,
        '502':3950, '602':4050, '682':4050, '802':4050, '103':4050, '123':4050,
        '153':4150, '203':4250, '303':4250, '473':4300, '503':4300, '104':4400,
        '154':4500, '204':4600, '224':4600, '474':4750,
    }
    @classmethod
    def catalog(cls, model=None):
        """All NTCs in series"""
        if model is None:
            return cls._catalog.keys()
        elif model in cls._catalog:
            return cls._catalog[model]
        else:
            print('Unknown NTC model %s'%model)
            raise KeyError

    def __init__(self, code):
        self.vendor = 'TKS'
        self.series = 'TTC05'
        self.model = "%03d"%int(code)
        self.name = '%s%s'%(self.series, self.model)
        try:
            beta, code = self.catalog(self.model), self.model
        except KeyError as error:
            print('Unknown NTC %s%s'%self.name)
            raise error
        super(TTC05, self).__init__(beta, code, unit='SMD3', name=self.name)

if __name__ == '__main__':
    import matplotlib.pyplot as plot
    import pandas

    catalog = pandas.DataFrame(
        index=numpy.linspace(25, 75, 100),  # 25 to 75 *C
    )

    for ntc in [102, 103, 104]:
        ntc=TTC05(ntc)
        print("%s"%ntc)
        catalog[ntc.name] = pandas.Series(
            ntc.resistance(catalog.index, 'Ω'),
            index=catalog.index,
        )

    catalog.plot(logy=False, subplots=False)
    plot.xlabel("temperature [*C]")
    plot.ylabel("resistance [Ω]")
    plot.savefig('TTC05.png')
    plot.show()
