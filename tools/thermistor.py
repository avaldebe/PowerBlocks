#!/usr/bin/env python
"""
NTC thermistor class

TODO:
- voltage and current SI_param objects
- voltage calculation for R_bias, R_load, R_bridge NTC configurations
"""
from __future__ import print_function
import numpy

class SI_param(object):
    """
    Generic SI object, such as temperature and resistence
    """
    _unit_default = None
    _unit_conv = {}
    def __init__(self, value, unit=None):
        assert unit in self._unit_conv, 'Unsuported unit "%s"'%unit
        self._value = float(value)
        self._unit = unit if unit else self._unit_default
    def __str__(self):
        return '%g %s'%(self._value, self._unit)
    def __float__(self):
        return self._value

    @classmethod
    def convert_unit(cls, value, unit_from, unit_to):
        def _from_unit(val, unit):
            assert unit in cls._unit_conv, 'Unsuported unit "%s"'%unit
            scale, offset = cls._unit_conv[unit]['scale'], cls._unit_conv[unit]['offset']
            return scale * val + offset
        def _to_unit(val, unit):
            assert unit in cls._unit_conv, 'Unsuported unit "%s"'%unit
            scale, offset = cls._unit_conv[unit]['scale'], cls._unit_conv[unit]['offset']
            return (val - offset) / scale
        if unit_from is unit_to:
            return value
        else:
            return _to_unit(_from_unit(value, unit_from), unit_to)

    def unit(self, unit):
        value = self.convert_unit(self._value, self._unit, unit)
        self.__init__(value, unit)
        return self

class Resistance(SI_param):
    """Resistance in ohm"""
    _unit_default = 'kohm'
    _unit_conv = dict(
        Mohm={'scale':1e6, 'offset':0},
        kohm={'scale':1e3, 'offset':0},
        ohm={'scale':1e0, 'offset':0},
        mohm={'scale':1e-3, 'offset':0},
    )
    @staticmethod
    def smd(code):
        """
        Decode 3-digit and 4-digit SMD markings
        http://www.hobby-hour.com/electronics/smdcalc.php#smd_resistor_code
        """
        assert type(code) is str and len(code) in [3, 4], 'Unknown SMD code "%s"'%code
        if 'R' in code:
            value = code.replace('R','.')
        elif code.isdigit():
            value = "%se%s"%(code[0:-1], code[-1])
        try:
            return Resistance(value, 'ohm')
        except ValueError as error:
            print('Wrong SMD code "%s"'%code)
            raise error
    @classmethod
    def convert_unit(cls, value, unit_from, unit_to):
        if unit_from.lower() in ['smd', 'smd3', 'smd4']:
            return float(cls.smd(value).unit(unit_to))
        else:
            return super(Resistance, cls).convert_unit(value, unit_from, unit_to)

class Temperature(SI_param):
    """Temperature in *K"""
    _unit_default = 'K'
    _unit_conv = dict(
        K={'scale':1, 'offset':0},
        C={'scale':1, 'offset':273.15},
        F={'scale':5/9,'offset':459.67*5/9},
    )

class NTC(object):
    """
    Generig NTC
    Based on https://pypi.python.org/pypi/thermistor
    """
    def __init__(self, B, R0, unit='kohm', T0=298.15, T1=323.15, name=None):
        """Basic NTC parameters"""
        self.B = float(B)       # beta(T0/T1) coefficient in [K]
        self.R0 = Resistance.convert_unit(R0, unit, 'kohm') # resistence at T0 in [kOhm]
        self.T0 = float(T0)     # 25 [*C] in [*K]
        self.T1 = float(T1)     # 50 [*C] in [*K]
        self.name = name if name else 'NTC%d'%self.B
#       self.R1 = self.resistance(self.T1, 'K')

    def temperature(self, R, r_unit='kohm', t_unit='C'):
        """resistance R [kohm] to temperature [unit]"""
        r_kohm = Resistance.convert_unit(R, r_unit, 'kohm')
        temp_inv = numpy.log(r_kohm/self.R0)/self.B + 1/self.T0
        return Temperature.convert_unit(1/temp_inv, 'K', t_unit)

    def reststance(self, T, r_unit='kohm', t_unit='C'):
        """temperature [unit] to resistance R [kOhm] """
        temp = Temperature.convert_unit(T, t_unit, 'K')
        temp = 1/temp - 1/self.T0
        r_kohm = numpy.exp(self.B*temp)
        return Resistance.convert_unit(r_kohm, 'kohm', r_unit)

    def __str__(self):
        t0 = Temperature(self.T0, 'K').unit('C')
        r0 = Resistance(self.R0, 'kohm')
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
            beta = self.catalog(self.model)
        except KeyError as error:
            print('Unknown NTC %s%s'%self.name)
            raise error
        super(TTC05, self).__init__(beta, self.model, unit='SMD3', name=self.name)

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
            ntc.reststance(catalog.index, 'ohm'),
            index=catalog.index,
        )

    catalog.plot(logy=False, subplots=False)
    plot.xlabel("temperature [*C]")
    plot.ylabel("resistance [Ohm]")
    plot.savefig('TTC05.png')
    plot.show()
