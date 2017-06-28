from urllib import request
import json


class Converter(object):
    """
    A class which is used to convert units
    """
    len_units = {'millimeter': 0.001, 'mm': 0.001, 'centimeter': 0.01, 'cm': 0.01, 'meter': 1, 'm': 1,
                 'kilometer': 1000, 'km': 1000, 'inch': 0.0254, 'in': 0.0254, 'foot': 3.28084,
                 'ft': 3.28084, 'yard': 1.09361}

    mass_units = {'milligram': 0.000001, 'mg': 0.000001, 'gram': 0.001, 'g': 0.001, 'kilogram': 1, 'kg': 1,
                  'ton': 1000, 'pound': 0.453592, 'ounce': 0.0283495}

    @staticmethod
    def _get_currency_rates(base='ils') -> dict:
        """
        Gathers the currency rates from the api
        :param base: the base currency
        :returns: dict of currency rates
        """
        with request.urlopen('http://api.fixer.io/latest?base={}'.format(base)) as url:
            data = json.loads(url.read().decode())
            rates = {k.lower(): v**-1 for k, v in data['rates'].items()}
            rates[base] = 1
            return rates

    @staticmethod
    def _convert_const(units, amount: float, unit1, unit2) -> float:
        """
        Calculates the requested conversion of constant units (i.e. mass, length, etc.)
        :param units: a dict of units in the same category as unit1 and unit2
        :param amount: the amount to convert
        :param unit1: the original unit
        :param unit2: the unit of conversion
        :returns: the conversion result
        """
        return units[unit1] / units[unit2] * amount

    @staticmethod
    def find(unit):
        """
        Checks whether a unit is supported by the converter and returns the dict of values for that unit
        :param unit: the unit
        :return: the dict of values for that unit if it's is supported by the converter, None otherwise
        """
        if unit in Converter.len_units:
            return Converter.len_units
        if unit in Converter.mass_units:
            return Converter.mass_units
        try:
            rates = Converter._get_currency_rates()
            if unit in rates:
                return rates
        except:
            return None
        return None

    @staticmethod
    def _get_units(unit1, unit2):
        """
        Checks whether unit1 is convertible to unit2 and returns the dict of values those units
        :param unit1: the original unit
        :param unit2: the conversion unit
        :return: the dict of values for the units if they are convertible, None otherwise
        """
        units = Converter.find(unit1)
        if units and unit2 in units:
            return units
        return None

    @staticmethod
    def convert(amount: float, unit1, unit2) -> float:
        """
        Converts an amount of unit1 into unit2
        :param amount: the amount to convert
        :param unit1: the original unit
        :param unit2: the conversion unit
        :return: float result of the conversion, if the conversion fails, -1 will be returned
        """
        unit1, unit2 = unit1.lower(), unit2.lower()
        units = Converter._get_units(unit1, unit2)
        if not units:
            return -1
        return units[unit1] / units[unit2] * amount
