"""
This file is part of Buttonwood.

Buttonwood is a python software package created to help quickly create, (re)build, or 
analyze markets, market structures, and market participants. 

MIT License

Copyright (c) 2016-2017 Peter F. Nabicht

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from cdecimal import Decimal


class Product(object):
    def __init__(self, symbol, name, min_price_increment, min_price_increment_value):
        """
        Contains all the information needed about a Product.
  
        A product + an endpoint == a trade-able asset
        :param symbol: str. the common symbol of the product
        :param name: str. the name of the product (more verbose than product. This is also the unique hash of the product
        :param min_price_increment: float or int. the smallest increment of the product, also often called a tick.
        :param min_price_increment_value: float or int. the value of the smallest increment the products trades in.
        """
        assert isinstance(symbol, str)
        assert isinstance(name, str)
        assert isinstance(min_price_increment, Decimal) or isinstance(min_price_increment, str)
        assert isinstance(min_price_increment_value, Decimal) or isinstance(min_price_increment_value, str)
        self._symbol = symbol
        self._name = name
        self._min_price_increment = Decimal(min_price_increment)
        self._min_price_increment_value = Decimal(min_price_increment_value)
        self._identifiers = {}  # used to store different identifiers, like CUSIP, bloomberg universal ID, etc.
        # equality of product ends up getting called pretty frequently so rather than doing a bunch of comparison of a
        #  bunch of getters i'm just going to have one nice tuple and do and do a direct comparison of the tuple
        self._equality_comparitor = (name.lower(), symbol.lower())
        self.__hash = hash(name)

    def set_identifier(self, id_type, id_name):
        """
        Add an identifier as key/value pair,
        :param id_type: str. the key of the identifier, such as "cusip"
        :param id_name: str. the value of the identifer, such as "083803"
        :return:
        """
        assert isinstance(id_type, str)
        assert isinstance(id_name, str)
        # keys default to lower for comparison, but not values since case could end up being important
        self._identifiers[id_type.lower()] = id_name

    def get_identifier(self, id_type):
        """
        Gets the name of the identifer assoicated with the type passed in.
        :param id_type: str. the identifier type, such as cusip
        :return: str. the identifier name. can be None if the type is set.
        """
        return self._identifiers.get(id_type.lower())

    def identifiers(self):
        """
        Gets the dictionary of identifiers of the Product.
        :return: dict {str: str}
        """
        return self._identifiers

    def name(self):
        """
        Gets the name of the product. This is a more verbose title of the product when compared to symbol.
        For example:
         *  symbol is 'MSFT'; name is 'microsoft'
         *  symbol is 'GEU5'; name is 'Eurodollar, September 2005'
        :return: str.
        """
        return self._name

    def symbol(self):
        """
        Gets the symbol (aka. abbreviation) commonly used to describe the product. A symbol is less verbose than a name.
         For example:
          *  symbol is 'MSFT'; name is 'microsoft'
          *  symbol is 'GEU5'; name is 'Eurodollar, September 2005'
        :return: str.
        """
        return self._symbol

    def min_price_increment(self):
        """
        Gets the minimum price increment of a product. This is the smallest increment that the product trades in.
        :return: Decimal
        """
        return self._min_price_increment

    def min_price_increment_value(self):
        """
        Gets the monetary value associated with the minimum price increment of a product.
        :return: Decimal
        """
        return self._min_price_increment_value

    def mpi(self):
        """
        This is the same as `min_price_increment()'. It is just for the convenience of the developer.
  
        :return: Decimal
        """
        return self._min_price_increment

    def mpi_value(self):
        """
        This is the same as `min_price_increment_value()'. It is just for the convenience of the developer.
  
        :return: Decimal
        """
        return self._min_price_increment_value

    def is_valid_price(self, price):
        return (price / self._min_price_increment) % 1 == 0

    def __eq__(self, other):
        identifiers_match = True
        other_identifiers = other.identifiers()
        shared_identifiers = set(self._identifiers).intersection(other_identifiers)
        for shared_identifier in shared_identifiers:
            if self._identifiers[shared_identifier] != other_identifiers[shared_identifier]:
                identifiers_match = False
                break

        return self._equality_comparitor == other._equality_comparitor and identifiers_match

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "%s %s  {mpi: %s mpiValue: %s}" % (self.symbol(), self.name(), str(self.mpi()), str(self.mpi_value()))

    def __hash__(self):
        return self.__hash

    def to_json(self):
        return {"symbol": self.symbol(), "name": self.name(), "mpi": str(self.mpi()), "mpi_value": str(self.mpi_value())}
