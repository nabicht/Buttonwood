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
from buttonwood.MarketObjects.Endpoint import Endpoint
from buttonwood.MarketObjects.Product import Product
from buttonwood.MarketObjects.Price import Price
from buttonwood.MarketObjects.Market import Market


PRODUCT = Product("AAA", "Some Product named AAA")
ENDPOINT = Endpoint("GenMatch", "Generic matching venue")


def test_market_creation():
    mrkt = Market(PRODUCT, ENDPOINT, Decimal("0.01"))
    assert PRODUCT == mrkt.product()
    assert ENDPOINT == mrkt.endpoint()
    assert mrkt.min_price_increment() == mrkt.mpi() == Decimal("0.01")
    assert len(mrkt._prices) == 0
    # TODO write a lot more tests here of different iterations


def test_basic_equality():
    mrkt1 = Market(PRODUCT, ENDPOINT, Decimal("0.01"))
    mrkt2 = Market(PRODUCT, ENDPOINT, Decimal("0.01"))
    assert mrkt1 == mrkt2

    mrkt2 = Market(Product("AAA", "Some Product named AAA"), ENDPOINT, Decimal("0.01"))
    assert mrkt1 == mrkt2

    mrkt2 = Market(PRODUCT, Endpoint("GenMatch", "Generic matching venue"), Decimal("0.01"))
    assert mrkt1 == mrkt2

    mrkt2 = Market(Product("BBB", "blah"), ENDPOINT, Decimal("0.01"))
    assert mrkt1 != mrkt2

    mrkt2 = Market(PRODUCT, Endpoint("xxx", "another endpoint"), Decimal("0.01"))
    assert mrkt1 != mrkt2


def test_price_validation():
    p = Price("23.455")
    mrkt = Market(PRODUCT, ENDPOINT, Decimal("0.01"))
    assert mrkt.is_valid_price(p) is False

    p = Price("23.45")
    mrkt = Market(PRODUCT, ENDPOINT, Decimal("0.005"))
    assert mrkt.is_valid_price(p)

    p = Price("23.455")
    mrkt = Market(PRODUCT, ENDPOINT, Decimal("0.005"))
    assert mrkt.is_valid_price(p)

    p = Price("23.45")
    mrkt = Market(PRODUCT, ENDPOINT, Decimal("1"))
    assert mrkt.is_valid_price(p) is False

    p = Price("23.45")
    mrkt = Market(PRODUCT, ENDPOINT, Decimal("0.45"))
    assert mrkt.is_valid_price(p) is False


def test_price_creation():
    mrkt = Market(PRODUCT, ENDPOINT, Decimal("0.01"), price_range=2)
    assert len(mrkt._prices) == 0
    mrkt.get_price("100.00")
    print mrkt._prices
    assert len(mrkt._prices) == 5
    assert Decimal("99.98") in mrkt._prices
    assert Decimal("99.99") in mrkt._prices
    assert Decimal("100.0") in mrkt._prices
    assert Decimal("100.01") in mrkt._prices
    assert Decimal("100.02") in mrkt._prices

    # should not expand it at all
    mrkt.get_price("100.02")
    assert len(mrkt._prices) == 5
    assert Decimal("99.98") in mrkt._prices
    assert Decimal("99.99") in mrkt._prices
    assert Decimal("100.0") in mrkt._prices
    assert Decimal("100.01") in mrkt._prices
    assert Decimal("100.02") in mrkt._prices

    # now expand to the up
    mrkt.get_price("100.03")  # should add 3 more
    assert len(mrkt._prices) == 8
    assert Decimal("99.98") in mrkt._prices
    assert Decimal("99.99") in mrkt._prices
    assert Decimal("100.0") in mrkt._prices
    assert Decimal("100.01") in mrkt._prices
    assert Decimal("100.02") in mrkt._prices
    assert Decimal("100.03") in mrkt._prices
    assert Decimal("100.04") in mrkt._prices
    assert Decimal("100.05") in mrkt._prices

    # now expand to the down
    mrkt.get_price("99.95")  # should add 5 more
    assert len(mrkt._prices) == 13
    assert Decimal("99.93") in mrkt._prices
    assert Decimal("99.94") in mrkt._prices
    assert Decimal("99.95") in mrkt._prices
    assert Decimal("99.96") in mrkt._prices
    assert Decimal("99.97") in mrkt._prices
    assert Decimal("99.98") in mrkt._prices
    assert Decimal("99.99") in mrkt._prices
    assert Decimal("100.0") in mrkt._prices
    assert Decimal("100.01") in mrkt._prices
    assert Decimal("100.02") in mrkt._prices
    assert Decimal("100.03") in mrkt._prices
    assert Decimal("100.04") in mrkt._prices
    assert Decimal("100.05") in mrkt._prices

    # now expand with a gap
    mrkt.get_price("99.80")  # should add 5 more
    assert len(mrkt._prices) == 18
    assert Decimal("99.78") in mrkt._prices
    assert Decimal("99.79") in mrkt._prices
    assert Decimal("99.80") in mrkt._prices
    assert Decimal("99.81") in mrkt._prices
    assert Decimal("99.82") in mrkt._prices
    assert Decimal("99.94") in mrkt._prices
    assert Decimal("99.95") in mrkt._prices
    assert Decimal("99.96") in mrkt._prices
    assert Decimal("99.97") in mrkt._prices
    assert Decimal("99.98") in mrkt._prices
    assert Decimal("99.99") in mrkt._prices
    assert Decimal("100.0") in mrkt._prices
    assert Decimal("100.01") in mrkt._prices
    assert Decimal("100.02") in mrkt._prices
    assert Decimal("100.03") in mrkt._prices
    assert Decimal("100.04") in mrkt._prices
    assert Decimal("100.05") in mrkt._prices
    assert Decimal("99.90") not in mrkt._prices
