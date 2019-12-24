
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
from decimal import Decimal
from buttonwood.MarketObjects.Price import Price
from buttonwood.MarketObjects.Price import PriceFactory
from buttonwood.MarketObjects.Price import InvalidPriceException
from buttonwood.MarketObjects.Side import ASK_SIDE
from buttonwood.MarketObjects.Side import BID_SIDE
from nose.tools import *


def test_price_validation():
    p = Price("23.455")
    pf = PriceFactory("0.01")
    assert pf.is_valid_price(p) is False

    p = Price("23.45")
    pf = PriceFactory("0.01")
    assert pf.is_valid_price(p)

    p = Price("23.455")
    pf = PriceFactory("0.001")
    assert pf.is_valid_price(p)

    p = Price("23.45")
    pf = PriceFactory("0.1")
    assert pf.is_valid_price(p) is False

    p = Price("23.45")
    pf = PriceFactory(".5")
    assert pf.is_valid_price(p) is False


def test_get_price():
    pf = PriceFactory("0.01")
    p = pf.get_price(100)
    assert p == Price(100)
    assert p == Decimal("100.00")
    p = pf.get_price("100.01")
    assert p == Price("100.01")
    assert p == Decimal("100.01")
    p = pf.get_price(Decimal("222.22"))
    assert p == Price("222.22")
    assert p == Decimal("222.22")


@raises(InvalidPriceException)
def test_get_price_wrong_mpi_str():
    pf = PriceFactory("0.01")
    pf.get_price("100.001")


@raises(InvalidPriceException)
def test_get_price_wrong_mpi_decimal():
    pf = PriceFactory("0.01")
    pf.get_price(Decimal("100.001"))


@raises(InvalidPriceException)
def test_get_price_wrong_mpi_int():
    pf = PriceFactory(5)
    pf.get_price(7)


def test_min_price():
    pf = PriceFactory("0.01", min_price=Decimal("100.0"))
    # should work for 100.01 and 100.0 but not 99.99
    # also, price 100.01 should and 100.00 should not create 99.00
    pf.get_price("100.01")
    pf.get_price("100.00")

@raises(InvalidPriceException)
def test_min_price_excpetion():
    pf = PriceFactory("0.01", min_price=Decimal("100.0"))
    # should work for 100.01 and 100.0 but not 99.99
    # also, price 100.01 should and 100.00 should not create 99.00
    pf.get_price("99.99")


def test_max_price():
    pf = PriceFactory("0.01", max_price=Decimal("100.0"))
    # should work for 99.99 and 100.0 but not 100.01
    # also, price 99.99 and 100.00 should be created, but should not create 99.00
    pf.get_price("99.99")
    pf.get_price("100.00")


def test_next_price():
    pf = PriceFactory(".5")
    starting_price = pf.get_price(100)
    new_price = pf.next_price(starting_price, BID_SIDE)
    assert new_price == Price("100.5")
    new_price = pf.next_price(new_price, BID_SIDE)
    assert new_price == Price(101)

    new_price = pf.next_price(new_price, ASK_SIDE)
    assert new_price == Price("100.5")
    new_price = pf.next_price(new_price, ASK_SIDE)
    assert new_price == Price(100)


def test_prev_price():
    pf = PriceFactory(".5")
    starting_price = pf.get_price(100)
    new_price = pf.prev_price(starting_price, BID_SIDE)
    assert new_price == Price("99.5")
    new_price = pf.prev_price(new_price, BID_SIDE)
    assert new_price == Price(99)

    new_price = pf.prev_price(new_price, ASK_SIDE)
    assert new_price == Price("99.5")
    new_price = pf.prev_price(new_price, ASK_SIDE)
    assert new_price == Price(100)


@raises(InvalidPriceException)
def test_max_price_excpetion():
    pf = PriceFactory("0.01", max_price=Decimal("100.0"))
    pf.get_price("100.01")


def test_to_json():
    # doesn't really do anything, just makes sure no issues with getting the json
    json.dumps(PriceFactory("0.01", min_price=Decimal("0.0"), max_price=Decimal("100.0")).to_json())


def test_to_str():
    # doesn't really do anything, just makes sure no issues with getting the str
    str(PriceFactory("0.01", min_price=Decimal("0.0"), max_price=Decimal("100.0")))


