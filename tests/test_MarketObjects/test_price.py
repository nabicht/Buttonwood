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

from decimal import Decimal
from math import nan
from buttonwood.MarketObjects.Price import Price
from buttonwood.MarketObjects.Side import BID_SIDE
from buttonwood.MarketObjects.Side import ASK_SIDE


def test_setting_price():
    p = Price("94.58793")
    assert p == Decimal("94.58793")


def test_equality_to_none():
    p = Price("1.242")
    n = None
    assert p != n


def test_equality_to_nan():
    p = Price(nan)
    x = Price("22.3")
    assert p != x


def test_price_decimal_addition():
    p = Price("100.01")
    mpi = Decimal("0.01")
    n = p + mpi
    assert isinstance(p + mpi, Price)
    assert n != p
    assert n == Price("100.02")


def test_price_int_addition():
    p = Price("100.01")
    mpi = 1
    new_price = p + mpi
    assert isinstance(new_price, Price)
    assert new_price != p
    assert new_price == Price("101.01")


def test_price_int_subtraction():
    p = Price("100.01")
    n = p - 1
    assert isinstance(n, Price)
    assert n == Price("99.01")
    assert n != p


def test_price_decimal_subtraction():
    p = Price("100.01")
    n = p - Decimal(1)
    assert isinstance(n, Price)
    assert n == Price("99.01")
    assert n != p


def test_float_addition():
    p = Price('1.1')
    f = 2.2
    res = p + f
    assert isinstance(res, Price)
    assert res == Price('3.3')


def test_int_addition():
    p = Price('1.1')
    i = 5
    res = p + i
    assert isinstance(res, Price)
    assert res == Price('6.1')


def test_int_multiplication():
    p = Price('1.1')
    i = 6
    res = p * i
    assert isinstance(res, Price)
    assert res == Price("6.6")


def test_decimal_multiplication():
    p = Price('1.1')
    d = Decimal(6)
    res = p * d
    assert isinstance(res, Price)
    assert res == Price("6.6")


def test_float_mulitplication():
    p = Price('1.1')
    f = 6.5
    res = p * f
    assert isinstance(res, Price)
    assert res == Price('7.15')


def test_better_than():
    p = Price("91.543")
    p_less = Price("84.456")
    p_more = Price("92.123")
    p_same = Price("91.543")
    assert p_more.better_than(p, BID_SIDE) is True
    assert p_more.better_than(p, ASK_SIDE) is False
    assert p_less.better_than(p, BID_SIDE) is False
    assert p_less.better_than(p, ASK_SIDE) is True
    assert p.better_than(p_same, BID_SIDE) is False
    assert p.better_than(p_same, ASK_SIDE) is False


def test_better_or_same_as():
    p = Price("91.543")
    p_less = Price("84.456")
    p_more = Price("92.123")
    p_same = Price("91.543")
    assert p_more.better_than(p, BID_SIDE) is True
    assert p_more.better_than(p, ASK_SIDE) is False
    assert p_less.better_or_same_as(p, BID_SIDE) is False
    assert p_less.better_or_same_as(p, ASK_SIDE) is True
    assert p.better_or_same_as(p_same, BID_SIDE) is True
    assert p.better_or_same_as(p_same, ASK_SIDE) is True


def test_worse_than():
    p = Price("91.543")
    p_less = Price("84.456")
    p_more = Price("92.123")
    p_same = Price("91.543")
    assert p_less.worse_than(p, BID_SIDE) is True
    assert p_less.worse_than(p, ASK_SIDE) is False
    assert p_more.worse_than(p, BID_SIDE) is False
    assert p_more.worse_than(p, ASK_SIDE) is True
    assert p.worse_than(p_same, BID_SIDE) is False
    assert p.worse_than(p_same, ASK_SIDE) is False


def test_worse_or_same_as():
    p = Price("91.543")
    p_less = Price("84.456")
    p_more = Price("92.123")
    p_same = Price("91.543")
    assert p_less.worse_or_same_as(p, BID_SIDE) is True
    assert p_less.worse_or_same_as(p, ASK_SIDE) is False
    assert p_more.worse_or_same_as(p, BID_SIDE) is False
    assert p_more.worse_or_same_as(p, ASK_SIDE) is True
    assert p.worse_or_same_as(p_same, BID_SIDE) is True
    assert p.worse_or_same_as(p_same, ASK_SIDE) is True


def test_comparison():
    p = Price("91.543")
    p_less = Price('84.456')
    p_more = Price('92.123')
    p_same = Price('91.543')
    assert p_less < p_more
    assert p_less <= p_more
    assert p_less != p_more
    assert (p_less > p_more) is False
    assert (p_less >= p_more) is False
    assert (p_less == p_more) is False
    assert p >= p_same
    assert p <= p_same
    assert p == p_same
    assert (p != p_same) is False
    assert p_same >= p
    assert p_same <= p

    
def test_price_math():
    p1 = Price('1.15')
    p2 = Price('1.35')
    assert p1 + p2 == Price('2.5')
    assert p2 + p1 == Price('2.5')
    assert p2 - p1 == Price('.2')
    assert p1 - p2 == Price('-0.2')
