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

from cdecimal import Decimal
from nose.tools import *
from buttonwood.MarketObjects.Quote import Quote
from buttonwood.MarketObjects.Price import Price
from buttonwood.MarketObjects.Price import PriceFactory
from buttonwood.MarketObjects.Side import BID_SIDE
from buttonwood.MarketObjects.Endpoint import Endpoint
from buttonwood.MarketObjects.Market import Market
from buttonwood.MarketObjects.Product import Product

MARKET = Market(Product("MSFT", "Microsoft"), Endpoint("Nasdaq", "NSDQ"), PriceFactory("0.01"))


def test_quote_creation():
    q = Quote(MARKET, BID_SIDE, Price("95.42"), 94)
    assert q.price().price() == Decimal("95.42")
    assert q.visible_qty() == 94
    assert q.hidden_qty() == 0
    assert q._price_level.number_of_orders() == 1
    assert q.market().product().name() == "Microsoft"
    assert q.market().product().symbol() == "MSFT"


@raises(AssertionError)
def test_price_does_not_work_for_product():
    # price has to pass the test of being divisible evenly by the product's minimum price increment
    Quote(MARKET, BID_SIDE, Price("94.342"), 94)


@raises(AssertionError)
def test_visible_qty_not_negative():
    Quote(MARKET, BID_SIDE, Price("94.34"), -3)


@raises(AssertionError)
def test_visible_qty_not_zero():
    Quote(MARKET, BID_SIDE, Price("94.34"), 0)


@raises(AssertionError)
def test_hidden_qty_not_negative():
    Quote(MARKET, BID_SIDE, Price("94.34"), 23, -23)


def test_equality():
    q1 = Quote(MARKET, BID_SIDE, Price("95.42"), 94)
    q2 = Quote(MARKET, BID_SIDE, Price("95.42"), 94)
    assert q1 == q2

    q2 = Quote(Market(Product("APPL", "Apple"), Endpoint("Nasdaq", "NSDQ"), PriceFactory("0.01")),
               BID_SIDE, Price("95.42"), 94)
    assert q1 != q2

    q2 = Quote(MARKET, BID_SIDE, Price("95.43"), 94)
    assert q1 != q2

    q2 = Quote(MARKET, BID_SIDE, Price("95.42"), 91)
    assert q1 != q2

    q2 = Quote(MARKET, BID_SIDE, Price("95.42"), 94, 2)
    assert q1 != q2

    q2 = Quote(MARKET, BID_SIDE, Price("95.42"), 94, 0)
    assert q1 == q2

    q1 = Quote(MARKET, BID_SIDE, Price("95.42"), 94, 3)
    q2 = Quote(MARKET, BID_SIDE, Price("95.42"), 94, 3)
    assert q1 == q2
