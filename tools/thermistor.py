#!/usr/bin/env python
"""
NTC thermistor class

Based on https://pypi.python.org/pypi/thermistor
"""
from __future__ import print_function
import numpy

class SI_param(object):
    """Generic SI object, such as temperature and resistence"""
    _unit_conv = {}
    def __init__(self, value, unit=None):
        assert unit in self._unit_conv, 'Unsuported unit "%s"'%unit
        self._value = value
        self._unit = unit

    def unit(self, unit=None):
        assert unit in self._unit_conv, 'Unsuported unit "%s"'%unit
        value = self._value
        if unit != self._unit:
            value *= self._unit_conv[self._unit]['scale']
            value += self._unit_conv[self._unit]['offset']
            value -= self._unit_conv[unit]['offset']
            value /= self._unit_conv[unit]['scale']
        return value

    def __str__(self):
        return '%.3f %s'%(self._value,self._unit)

class Resistance(SI_param):
    """Resistance in ohm"""
    _unit_conv = dict(
        Mohm={'scale':1e6, 'offset':0},
        kohm={'scale':1e3, 'offset':0},
        ohm={'scale':1e0, 'offset':0},
        mohm={'scale':1e-3, 'offset':0},
    )
    def __init__(self, value, unit='kohm'):
        super(Resistance, self).__init__(value, unit)

class Temperature(SI_param):
    """Temperature in *K"""
    _unit_conv = dict(
        K={'scale':1, 'offset':0},
        C={'scale':1, 'offset':273.15},
        F={'scale':5/9,'offset':459.67*5/9},
    )
    def __init__(self, value, unit='K'):
        super(Temperature, self).__init__(value, unit)

class NTC(object):
    """Generig NTC"""
    def __init__(self, R0=10, B=3977, T0=298.15, T1=323.15):
        """Basic NTC parameters"""
        self.R0 = float(R0)   # resistence at T0 in [kOhm]
        self.B = float(B)     # beta(T0/T1) coefficient in [K]
        self.T0 = float(T0)   # 25 [*C] in [*K]
        self.T1 = float(T1)   # 50 [*C] in [*K]

    def temperature(self, R, r_unit='kohm', t_unit='C'):
        """resistance R [kohm] to temperature [unit]"""
        r_kohm = Resistance(R,r_unit).unit('kohm')
        temp_inv = numpy.log(r_kohm/self.R0)/self.B + 1/self.T0
        return Temperature(1/temp_inv, 'K').unit(t_unit)

    def reststance(self, T, unit='C'):
        """temperature [unit] to resistance R [kOhm] """
        temp = Temperature(T, unit).unit('K')
        temp = 1/temp - 1/self.T0
        return numpy.exp(self.B*temp)


class TTC05(NTC):
    """
    TKS TTC05 series
    http://www.thinking.com.tw/documents/en-TTC05.pdf
    """
    __catalog = {
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

    def catalog(self, model=None):
        """All NTCs in series"""
        if model is None:
            return self.__catalog.keys()
        else:
            return self.__catalog[model]

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
        index=numpy.linspace(25, 75, 100),  # 25 to 75 *C
    )

    for model in [102, 103, 104]:
        ntc=TTC05(model)
        catalog[ntc.name] = pandas.Series(
            ntc.reststance(catalog.index)*1e3,  # kOhm to Ohm
            index=catalog.index,
        )

    catalog.plot(logy=False, subplots=False)
    plot.xlabel("temperature [*C]")
    plot.ylabel("resistance [Ohm]")
    plot.savefig('TTC05.png')
    plot.show()
