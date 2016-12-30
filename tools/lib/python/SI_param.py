#!/usr/bin/env python
# encoding: utf-8
"""
Parameter with attached SI units:
* ATmospheric parameters
    * Temperature in [K, C, F] units
* Electrical parameters
    * Resistance in [kΩ, Ω, mΩ] units
    * Voltage in [mV, V] units
    * Current in [mA, A] units

TODO:
* add relative humidity, atmospheric pressure
* add power
"""
from __future__ import print_function

class _SI_unit(object):
    """
    From `NIST`__
    .. __: https://www.nist.gov/pml/nist-guide-si-chapter-4-two-classes-si-units-and-si-prefixes

    ========================= ======= =========
    Base quantity             SI base unit
    ------------------------- -----------------
    ..                        Symbol  Name
    ========================= ======= =========
    length                    m       meter
    mass                      kg      kilogram
    time                      s       second
    electric current          A       ampere
    thermodynamic temperature K       kelvin
    amount of substance       mol     mole
    ========================= ======= =========

    ========================= ========= ======
    Derived quantity          SI derived unit
    ------------------------- ----------------
    ..                        Symbol    Name
    ========================= ========= ======
    area                      m2        square meter
    volume                    m3        cubic meter
    speed, velocity           m/s       meter per second
    acceleration              m/s2      meter per second squared
    wavenumber                m-1       reciprocal meter
    density, mass density     kg/m3     kilogram per cubic meter
    specific volume           m3/kg     cubic meter per kilogram
    current density           A/m2      ampere per square meter
    magnetic field strength   A/m       ampere per meter
    substance concentration   mol/m3	mole per cubic meter
    ========================= ========= ======

    ========================= ========= ======== ======
    Derived quantity          SI coherent derived unit
    ------------------------- -------------------------
    ..                        Symbol    Formula  Name
    ========================= ========= ======== ======
    frequency	              Hz        s-1      hertz
    force                     N         m*kg/s2  newton
    pressure, stress          Pa        N/m2     pascal
    energy, work              J         N*m      joule
    power                     W         J/s      watt
    electric charge           C         s*A      coulomb
    electric pot.difference   V         W/A      volt
    capacitance               F         C/V      farad
    electric resistance       Ω         V/A      ohm
     Celsius temperature      °C        K-273.15 degree Celsius
    ========================= ========= ======== ======
    """
    pass

class _SI_param(object):
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
        return hash(self.convert_unit(self._value, self._unit, self._unit_default))
    def __eq__(self, other):
        if isinstance(other, type(self)):
            return round(float(self) - float(other.unit(self)),6) == 0
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

class Temperature(_SI_param):
    """Temperature in *K"""
    _unit_default = 'K'
    _unit_conv = dict(K=(1, 0), C=(1, 273.15), F=(5/9, -32*5/9+273.15)) #.., unit=(scale, offset)
    def __str__(self):
        return '%g°%s'%(self._value, self._unit)

    @staticmethod
    def test(debug=False):
        """Check unit conversions"""
        test = "Temp. conversion"
        K, C, F = Temperature(323.15,'K'), Temperature(50,'C'), Temperature(122,'F')
        if debug:
            print('Test %s:\n  K=%s, C=%s, F=%s'%(test, K, C, F))
        else:
            print('Test %s:'%test, end='')
        test = dict(
            K=[C, F].count(K),
            C=[K, F].count(C),
            F=[K, C].count(F),
        )
        for key, val in test.items():
            assert val == 2, "  Failed %s conversion"%key
        print('  Pass')

class _OHM_param(_SI_param):
    """
    Ohm's law objects: resistence, voltage and current
    """
    @staticmethod
    def _ohms_law(R=None, I=None, V=None, unit=None):
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
            return self._ohms_law(R=self, I=param, unit=unit)
        elif isinstance(self, Current):
            return self._ohms_law(I=self, R=param, unit=unit)
        else:
            print("Wrong type %s"%type(self))
            raise TypeError
    def current(self, param, unit='mA'):
        if isinstance(self, Resistance):
            return self._ohms_law(R=self, V=param, unit=unit)
        elif isinstance(self, Voltage):
            return self._ohms_law(V=self, R=param, unit=unit)
        else:
            print("Wrong type %s"%type(self))
            raise TypeError
    def resistance(self, param, unit='kΩ'):
        if isinstance(self, Current):
            return self._ohms_law(I=self, V=param, unit=unit)
        elif isinstance(self, Voltage):
            return self._ohms_law(V=self, I=param, unit=unit)
        else:
            print("Wrong type %s"%type(self))
            raise TypeError
    @staticmethod
    def test(debug=False):
        """Check unit conversions and Ohm's Law calculations"""
        test = "Ohm's Law"
        V, I, R = Voltage(15,'V'), Current(5,'mA'), Resistance(3,'kΩ')
        if debug:
            print('Test %s:\n  V=%s, I=%s, R=%s'%(test, V, I, R))
        else:
            print('Test %s:'%test, end='')
        test = dict(
            V=[I.voltage(R), R.voltage(I)].count(V),
            I=[V.current(R), R.current(V)].count(I),
            R=[V.resistance(I), I.resistance(V)].count(R),
        )
        for key, val in test.items():
            assert val == 2, "  Failed %s conversion"%key
        print('  Pass')

class Resistance(_OHM_param):
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

class Voltage(_OHM_param):
    """Voltage in mV"""
    _unit_default = 'mV'
    _unit_conv = dict(mV=(1e0, 0), V=(1e3, 0))  #.., unit=(scale, offset)

class Current(_OHM_param):
    """Current in mA"""
    _unit_default = 'mA'
    _unit_conv = dict(mA=(1e0, 0), A=(1e3, 0))  #.., unit=(scale, offset)

if __name__ == '__main__':

    # assert unit conversions work
    Temperature.test()
    Resistance.test()
