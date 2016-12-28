#!/usr/bin/env python
# encoding: utf-8
"""
NTC thermistor class

TODO:
- voltage calculation for R_bias, R_load, R_bridge NTC configurations
- test temperature conversions
"""
from __future__ import print_function
import numpy

class SI_param(object):
    """
    Generic SI object, such as temperature
    """
    _unit_default = None
    _unit_conv = {}
    def __init__(self, value, unit=None):
        assert unit in self._unit_conv, 'Unsuported unit "%s"'%unit
        self._value = float(value)
        self._unit = unit if unit else self._unit_default
    def __float__(self):
        return self._value
    def __unit__(self):
        return self._unit
    def __str__(self):
        return '%g %s'%(self._value, self._unit)
    def __hash__(self):
        return hash(str(self))
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return float(self) == float(other.unit(self))
        else:
            return False
    def __ne__(self, other):
        return not self.__eq__(other)

    @classmethod
    def convert_unit(cls, value, unit_from, unit_to):
        """Convert between unit_from and unit_to """
        def _from_unit(val, unit):
            assert unit in cls._unit_conv, 'Unsuported unit "%s"'%unit
            scale, offset = cls._unit_conv[unit]
            return scale * val + offset
        def _to_unit(val, unit):
            assert unit in cls._unit_conv, 'Unsuported unit "%s"'%unit
            scale, offset = cls._unit_conv[unit]
            return (val - offset) / scale
        if unit_from is unit_to:
            return value
        else:
            return _to_unit(_from_unit(value, unit_from), unit_to)
    def unit(self, unit):
        """Convert object units"""
        if isinstance(unit, type(self)):
            unit = unit.__unit__()
        value = self.convert_unit(self._value, self._unit, unit)
        return self.__class__(value, unit)

class Temperature(SI_param):
    """Temperature in *K"""
    _unit_default = 'K'
    _unit_conv = dict(K=(1, 0), C=(1, 273.15), F=(5/9, -32*5/9+273.15)) #.., unit=(scale, offset)
    def __str__(self):
        return '%g°%s'%(self._value, self._unit)

    @staticmethod
    def test():
        """Check unit conversions"""
        pass

class OHM_param(SI_param):
    """
    Ohm's law objects: resistence, voltage and current
    """
    @staticmethod
    def ohms_law(R=None, I=None, V=None, unit=None):
        """calculate missing R|I|V as function ofthe other 2"""
        assert [R, I, V].count(None) == 1, "Wrong number of arguments"
        assert R is None or isinstance(R, Resistance), "R should be Resistance"
        assert I is None or isinstance(I, Current), "I should be Current"
        assert V is None or isinstance(V, Voltage), "V should be Voltage"
        if R is None:
            param = Resistance(float(V.unit('V'))/float(I.unit('A')), 'Ω')
        if I is None:
            param = Current(float(V.unit('V'))/float(R.unit('Ω')), 'A')
        if V is None:
            param = Voltage(float(R.unit('Ω'))*float(I.unit('A')), 'V')
        if unit:
            param = param.unit(unit)
        return param
    # Ohms law
    def voltage(self, param, unit='mV'):
        if isinstance(self, Resistance):
            return self.ohms_law(R=self, I=param, unit=unit)
        elif isinstance(self, Current):
            return self.ohms_law(I=self, R=param, unit=unit)
        else:
            print("Wrong type %s"%type(self))
            raise TypeError
    def current(self, param, unit='mA'):
        if isinstance(self, Resistance):
            return self.ohms_law(R=self, V=param, unit=unit)
        elif isinstance(self, Voltage):
            return self.ohms_law(V=self, R=param, unit=unit)
        else:
            print("Wrong type %s"%type(self))
            raise TypeError
    def resistance(self, param, unit='kΩ'):
        if isinstance(self, Current):
            return self.ohms_law(I=self, V=param, unit=unit)
        elif isinstance(self, Voltage):
            return self.ohms_law(V=self, I=param, unit=unit)
        else:
            print("Wrong type %s"%type(self))
            raise TypeError
    @staticmethod
    def test():
        """Check unit conversions and Ohm's Law calculations"""
        V, I, R = Voltage(15,'V'), Current(5,'mA'), Resistance(3,'kΩ')
        print('Test %s:\n  V=%s, I=%s, R=%s'%("Ohm's Law",V, I, R))
        test = dict(
            V=[I.voltage(R), R.voltage(I)].count(V),
            I=[V.current(R), R.current(V)].count(I),
            R=[V.resistance(I), I.resistance(V)].count(R),
        )
        for key, val in test.items():
            assert val == 2, "  Failed %s conversion"%key

class Resistance(OHM_param):
    """Resistance in Ω"""
    _unit_default = 'kΩ'
    _unit_conv = {'kΩ':(1e0, 0), 'Ω':(1e-3, 0),'mΩ':(1e-6, 0)} #.., unit=(scale, offset)
    @staticmethod
    def smd(code):
        """
        Decode 3-digit and 4-digit SMD markings
        http://www.hobby-hour.com/electronics/smdcalc.php#smd_resistor_code
        """
        assert type(code) is str and len(code) in [3, 4], 'Unknown SMD code "%s"'%code
        if 'R' in code:
            value = code.replace('R', '.')          # 1R1 is 1.1 Ω
        elif code.isdigit():
            value = "%se%s"%(code[0:-1], code[-1])  # 103 is 10e3 Ω
        try:
            return Resistance(value, 'Ω')
        except ValueError as error:
            print('Wrong SMD code "%s"'%code)
            raise error
    @classmethod
    def convert_unit(cls, value, unit_from, unit_to):
        """Convert units, support SMD codes"""
        if unit_from.lower() in ['smd', 'smd3', 'smd4']:
            return float(cls.smd(value).unit(unit_to))
        else:
            return super(Resistance, cls).convert_unit(value, unit_from, unit_to)

class Voltage(OHM_param):
    """Voltage in mV"""
    _unit_default = 'mV'
    _unit_conv = dict(mV=(1e0, 0), V=(1e3, 0))  #.., unit=(scale, offset)

class Current(OHM_param):
    """Current in mA"""
    _unit_default = 'mA'
    _unit_conv = dict(mA=(1e0, 0), A=(1e3, 0))  #.., unit=(scale, offset)


class NTC(object):
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

    def reststance(self, T, r_unit='kΩ', t_unit='C'):
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

    # assert unit conversions work
    Temperature.test()
    Resistance.test()

    catalog = pandas.DataFrame(
        index=numpy.linspace(25, 75, 100),  # 25 to 75 *C
    )

    for ntc in [102, 103, 104]:
        ntc=TTC05(ntc)
        print("%s"%ntc)
        catalog[ntc.name] = pandas.Series(
            ntc.reststance(catalog.index, 'Ω'),
            index=catalog.index,
        )

    catalog.plot(logy=False, subplots=False)
    plot.xlabel("temperature [*C]")
    plot.ylabel("resistance [Ω]")
    plot.savefig('TTC05.png')
    plot.show()
