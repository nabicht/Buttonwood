"""
This file is part of Buttonwood.

Buttonwood is a python software package created to help quickly create, (re)build, or
analyze markets, market structures, and market participants.

MIT License

Copyright (c) 2016-2019 Peter F. Nabicht

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

from buttonwood.MarketObjects.Endpoint import Endpoint
from buttonwood.MarketObjects.Price import PriceFactory
from buttonwood.MarketObjects.Product import Product
import sys

class Market(object):

    def __init__(self, product, endpoint, price_factory, min_qty=1, max_qty=sys.maxsize, qty_increment=1):
        """
        Contains all the information needed about a Market.

        A market is where a trade-able asset is traded. In a central limit order book market this would be one order
        book at one venue for one product. This is why the Market is made up of a Product and an Endpoint.

        :param product: Product. the market's product.
        :param endpoint: Endpoint. the market's endpoint.
        :param price_factory: Price.PriceFactory
        :param min_qty: int. the minimum qty that can be traded in the market. Defaults to 1
        :param qty_increment: int. the increment of qty that is allowed in the market. Defaults to 1
        """
        assert isinstance(product, Product)
        assert isinstance(endpoint, Endpoint)
        assert isinstance(price_factory, PriceFactory)
        self._price_factory = price_factory
        self._product = product
        self._endpoint = endpoint
        self._min_qty = min_qty
        self._max_qty = max_qty
        self._qty_increment = qty_increment
        self._hash = hash((self._product, self._endpoint))

    def product(self):
        """
        Get the Product

        :return: Product.
        """
        return self._product

    def endpoint(self):
        """
        Get the Endpoint

        :return:
        """
        return self._endpoint

    def price_factory(self):
        return self._price_factory

    def get_price(self, price_value):
        return self._price_factory.get_price(price_value)

    def min_price_increment(self):
        """
        Gets the minimum price increment of a product. This is the smallest increment that the product trades in.
        :return: Decimal
        """
        return self._price_factory.mpi()

    def min_price_increment_value(self):
        """
        Gets the monetary value associated with the minimum price increment of a product.
        :return: Decimal
        """
        return self._price_factory.mpi_value()

    def mpi(self):
        """
        This is the same as `min_price_increment()'. It is just for the convenience of the developer.

        :return: Decimal
        """
        return self._price_factory.mpi()

    def mpi_value(self):
        """
        This is the same as `min_price_increment_value()'. It is just for the convenience of the developer.

        :return: Decimal
        """
        return self._price_factory.mpi_value()

    def is_valid_price(self, price):
        return self._price_factory.is_valid_price(price)

    def min_qty(self):
        return self._min_qty

    def max_qty(self):
        return self._max_qty

    def qty_increment(self):
        return self._qty_increment

    def is_valid_qty(self, qty):
        return self._min_qty <= qty <= self._max_qty and (qty - self._min_qty) % self._qty_increment == 0

    def __eq__(self, other):
        return isinstance(other, Market) and other.__hash__() == self.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "%s@%s" % (self.product().name(), self.endpoint().name())

    def to_json(self):
        return {"product": self.product().to_json(), "endpoint": self.endpoint().to_json()}

    def to_detailed_json(self):
        price_info = self._price_factory.to_json()
        return {"product": self.product().to_detailed_json(), "endpoint": self._endpoint.to_json(),
                "price_info": price_info, "min_qty": self._min_qty, "qty_increment": self._qty_increment}

    def __hash__(self):
        return self._hash
