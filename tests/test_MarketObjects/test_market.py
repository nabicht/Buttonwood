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

import json
from cdecimal import Decimal
from buttonwood.MarketObjects.Endpoint import Endpoint
from buttonwood.MarketObjects.Product import Product
from buttonwood.MarketObjects.Price import Price
from buttonwood.MarketObjects.Price import PriceFactory
from buttonwood.MarketObjects.Market import Market
from buttonwood.MarketObjects.Price import InvalidPriceException
from nose.tools import *


PRODUCT = Product("AAA", "Some Product named AAA")
ENDPOINT = Endpoint("GenMatch", "Generic matching venue")
PRICE_FACTORY = PriceFactory(Decimal("0.01"))


def test_market_creation():
    mrkt = Market(PRODUCT, ENDPOINT, PRICE_FACTORY)
    assert PRODUCT == mrkt.product()
    assert ENDPOINT == mrkt.endpoint()
    assert mrkt.min_price_increment() == mrkt.mpi() == Decimal("0.01")
    assert len(mrkt.price_factory()._prices) == 0
    # TODO write a lot more tests here of different iterations


def test_basic_equality():
    mrkt1 = Market(PRODUCT, ENDPOINT, PRICE_FACTORY)
    mrkt2 = Market(PRODUCT, ENDPOINT, PRICE_FACTORY)
    assert mrkt1 == mrkt2

    mrkt2 = Market(Product("AAA", "Some Product named AAA"), ENDPOINT, PRICE_FACTORY)
    assert mrkt1 == mrkt2

    mrkt2 = Market(PRODUCT, Endpoint("GenMatch", "Generic matching venue"), PRICE_FACTORY)
    assert mrkt1 == mrkt2

    mrkt2 = Market(Product("BBB", "blah"), ENDPOINT, PRICE_FACTORY)
    assert mrkt1 != mrkt2

    mrkt2 = Market(PRODUCT, Endpoint("xxx", "another endpoint"), PRICE_FACTORY)
    assert mrkt1 != mrkt2

def test_to_json():
    # this is only testing that it isn't broken / bad code
    mrkt = Market(PRODUCT, ENDPOINT, PRICE_FACTORY)
    json.dumps(mrkt.to_json())


def test_to_detailed_json():
    # this is only testing that it isn't broken / bad code
    prod = Product("AAA", "Some Product named AAA")
    prod.set_identifier("CUSIP", "12345")
    prod.set_identifier("internal_id", "8u98792")
    mrkt = Market(prod, ENDPOINT, PRICE_FACTORY)
    json.dumps(mrkt.to_detailed_json())