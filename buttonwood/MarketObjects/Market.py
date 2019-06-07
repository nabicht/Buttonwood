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

from buttonwood.MarketObjects.Endpoint import Endpoint
from buttonwood.MarketObjects.Product import Product

class Market(object):

    def __init__(self, product, endpoint):
        """
        Contains all the information needed about a Market.

        A market is where a trade-able asset is traded. In a central limit order book market this would be one order
        book at one venue for one product. This is why the Market is made up of a Product and an Endpoint.

        :param product: Product. the market's product.
        :param endpoint: Endpoint. the market's endpoint.
        """
        assert isinstance(product, Product)
        assert isinstance(endpoint, Endpoint)
        self._product = product
        self._endpoint = endpoint
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

    def __eq__(self, other):
        return isinstance(other, Market) and other.__hash__() == self.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "%s@%s" % (self.product().name(), self.endpoint().name())

    def to_json(self):
        return {"product": self.product().to_json(), "endpoint": self.endpoint().to_json()}

    def __hash__(self):
        return self._hash
