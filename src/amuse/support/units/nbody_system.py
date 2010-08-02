from amuse.support.units import units
from amuse.support.units import core
from amuse.support.units import constants
from amuse.support import exceptions

from amuse.support.data.values import new_quantity


import numpy

"""
"""
class nbody_unit(core.base_unit):
    def __init__(self, unit_in_si, system):
        core.base_unit.__init__(self, unit_in_si.quantity, unit_in_si.name, unit_in_si.symbol, system)
        self.unit_in_si = unit_in_si
        
    def __str__(self):
        return 'nbody '+self.unit_in_si.quantity
        
  
nbody_system = core.system('nbody')

length = nbody_unit(units.m, nbody_system)
time = nbody_unit(units.s, nbody_system)
mass = nbody_unit(units.kg, nbody_system)
acceleration = length / (time ** 2)
potential = (length ** 2) / (time ** 2)
energy = mass * potential
specific_energy = potential
speed = length / time
G = 1 | (length**3) / (mass * (time**2))

def is_nbody_unit(unit):
    for factor, x in unit.base:
        if isinstance(x, nbody_unit):
            return True
    return False
    
    
class nbody_to_si(object): 
    DEFAULT_CONVERTER = None
    
    def __init__(self, value1 , value2):
        self.value1 = value1
        self.value2 = value2
        if self.unit1.base == self.unit2.base:
            raise exceptions.AmuseException("Must provide two orthogonal units for example mass and length or time and length")
        unit_was_found = [False, False, False]
        
        self.Gis1 = units.one / constants.G
        
        base = self.Gis1.unit.base
        for i, x in enumerate(base):
            for y in self.unit1.base:
                if y[1] == x[1]:
                    unit_was_found[i] = True
            for y in self.unit2.base:
                if y[1] == x[1]:
                    unit_was_found[i] = True
        if len(filter(None, unit_was_found)) < 2:
            raise exceptions.AmuseException("Must provide more units")
            
        
    @property
    def unit1(self):
        return self.value1.unit 
        
    @property
    def unit2(self):
        return self.value2.unit 
    
    def conversion_factors(self, unit_to_index):
        exponents_of_the_bases =  numpy.zeros((3,3))
        factors_of_the_bases =  numpy.zeros(3)
        for row, value in enumerate((self.Gis1, self.value1, self.value2)):
            for n, unit in value.unit.base:
                exponents_of_the_bases[row, unit_to_index[unit]] = n
            factors_of_the_bases[row] = value.number * value.unit.factor  
            
        log_factors_of_the_bases = numpy.log(factors_of_the_bases)
        numpy.exp(numpy.linalg.solve(exponents_of_the_bases, log_factors_of_the_bases))

        return numpy.exp(numpy.linalg.solve(exponents_of_the_bases, log_factors_of_the_bases))
        
    @property    
    def units(self):
        unit_to_index = {}
        for i, x in enumerate(self.Gis1.unit.base):
            n , unit = x
            unit_to_index[unit] = i
            
        conversion_factors = self.conversion_factors(unit_to_index)
        
        result = []
        nbody_units = mass, length, time
        for n, unit  in self.Gis1.unit.base:
            index = unit_to_index[unit]
            conversion_factor_for_this_base_unit = conversion_factors[index]
            for nbody_unit in nbody_units:
                if nbody_unit.unit_in_si == unit:
                    result.append((nbody_unit, conversion_factor_for_this_base_unit * unit))
                    
        return result
        
    def to_si(self, value):
        factor = value.unit.factor
        number = value.number
        new_unit = 1
        base = value.unit.base
        
        if not base:
            return value
        
        for n, unit in base:
            unit_in_nbody, unit_in_si = self.find_si_unit_for(unit)
            if not unit_in_si is None:
                factor = factor * (unit_in_si.factor ** n)
                new_unit *= (unit_in_si.base[0][1] ** n)
            else:
                new_unit *= (unit ** n)
        return new_quantity(number * factor, new_unit)
        
    
    def unit_to_unit_in_si(self, unit):
        factor = unit.factor
        new_unit = 1
        for n, unit in unit.base:
            unit_in_nbody, unit_in_si = self.find_si_unit_for(unit)
            if not unit_in_si is None:
                factor = factor * (unit_in_si.factor ** n)
                new_unit *= (unit_in_si.base[0][1] ** n)
            else:
                new_unit *= (unit ** n)
        return factor * new_unit
        
        
    def find_si_unit_for(self, unit):
        for unit_nbody, unit_in_si in self.units:
            if unit_nbody == unit:
                return unit_nbody, unit_in_si
        return None, None
        
    def find_nbody_unit_for(self, unit):
        for unit_nbody, unit_in_si in self.units:
            base_in_si = unit_in_si.base[0][1]
            if base_in_si == unit:
                return unit_nbody, unit_in_si
        return None, None
                
    def to_nbody(self, value):
        nbody_units_in_si = self.units
        base = value.unit.base
        factor = value.unit.factor
        number = value.number
        new_unit = 1
        
        if not base:
            return value
            
        for n, unit in base:
            unit_in_nbody, unit_in_si = self.find_nbody_unit_for(unit)
            if not unit_in_si is None:
                factor = factor / (unit_in_si.factor ** n)
                new_unit *= (unit_in_nbody.base[0][1] ** n)
            else:
                new_unit *= (unit ** n)
        return new_quantity(number * factor, new_unit)
        
    
    def unit_to_unit_in_nbody(self, unit):
        nbody_units_in_si = self.units
        base = unit.base
        factor = unit.factor
        new_unit = 1
        for n, unit in base:
            unit_in_nbody, unit_in_si = self.find_nbody_unit_for(unit)
            if not unit_in_si is None:
                factor = factor / (unit_in_si.factor ** n)
                new_unit *= (unit_in_nbody.base[0][1] ** n)
            else:
                new_unit *= (unit ** n)
        return factor * new_unit
        
    def set_as_default(self):
        """Depreacated, no converter can be set as default"""
        import warnings
        warnings.warn("""This call is no longer supported, you cannot set a convert as default to be used by all codes. If you want a converted you need to specify it when instantiating the code.""")
            
    def as_converter_from_si_to_nbody(self):
        class SiToNBodyConverter(object):
            def __init__(self, nbody_to_si):
                self.nbody_to_si = nbody_to_si
            
            def from_source_to_target(self, quantity):
                if hasattr(quantity, 'unit'):
                    return self.nbody_to_si.to_nbody(quantity) 
                else:
                    return quantity
                
            def from_target_to_source(self, quantity):
                if hasattr(quantity, 'unit'):
                    return self.nbody_to_si.to_si(quantity)
                else:
                    return quantity
                    
                
        return SiToNBodyConverter(self)
        
    def as_converter_from_nbody_to_si(self):
        
        class NBodyToSiConverter(object):
            def __init__(self, nbody_to_si):
                self.nbody_to_si = nbody_to_si
            
            def from_source_to_target(self, quantity):
                if hasattr(quantity, 'unit'):
                    return self.nbody_to_si.to_si(quantity) 
                else:
                    return quantity
                
            def from_target_to_source(self, quantity):
                if hasattr(quantity, 'unit'):
                    return self.nbody_to_si.to_nbody(quantity)
                else:
                    return quantity
                    
                
        return NBodyToSiConverter(self)

class noconvert_nbody_to_si(object): 
    
    def __init__(self):
        pass
        
    def to_si(self, value):
        return value
        
    def to_nbody(self, value):
        return value
                
                    
        

       
