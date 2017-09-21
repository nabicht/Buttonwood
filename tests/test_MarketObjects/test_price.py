"""
This file is part of MarketPy. 

MarketPy is a python software package created to help quickly create, (re)build, or 
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
from MarketPy.MarketObjects.Price import Price
from MarketPy.MarketObjects.Side import BID_SIDE
from MarketPy.MarketObjects.Side import ASK_SIDE


def test_setting_price():
    p = Price("94.58793")
    assert p.price() == Decimal("94.58793")


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


def test_better_than_int():
    p = Price("91.5")
    assert p.better_than(90, BID_SIDE) is True
    assert p.better_than(92, BID_SIDE) is False
    assert p.better_than(90, ASK_SIDE) is False
    assert p.better_than(92, ASK_SIDE) is True


def test_better_than_float():
    p = Price("91.5")
    assert p.better_than(90.1, BID_SIDE) is True
    assert p.better_than(92.1, BID_SIDE) is False
    assert p.better_than(91.5, BID_SIDE) is False
    assert p.better_than(90.1, ASK_SIDE) is False
    assert p.better_than(92.1, ASK_SIDE) is True
    assert p.better_than(91.5, ASK_SIDE) is False


def test_better_than_decimal():
    p = Price("91.5")
    assert p.better_than(Decimal(90.1), BID_SIDE) is True
    assert p.better_than(Decimal(92.1), BID_SIDE) is False
    assert p.better_than(Decimal(91.5), BID_SIDE) is False
    assert p.better_than(Decimal(90.1), ASK_SIDE) is False
    assert p.better_than(Decimal(92.1), ASK_SIDE) is True
    assert p.better_than(Decimal(91.5), ASK_SIDE) is False


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


def test_better_or_same_as_int():
    p = Price("91.5")
    assert p.better_or_same_as(90, BID_SIDE) is True
    assert p.better_or_same_as(92, BID_SIDE) is False
    assert p.better_or_same_as(90, ASK_SIDE) is False
    assert p.better_or_same_as(92, ASK_SIDE) is True

    p = Price("91")
    assert p.better_or_same_as(91, BID_SIDE) is True
    assert p.better_or_same_as(91, ASK_SIDE) is True


def test_better_or_same_as_float():
    p = Price("91.5")
    assert p.better_or_same_as(90.1, BID_SIDE) is True
    assert p.better_or_same_as(92.1, BID_SIDE) is False
    assert p.better_or_same_as(91.5, BID_SIDE) is True
    assert p.better_or_same_as(90.1, ASK_SIDE) is False
    assert p.better_or_same_as(92.1, ASK_SIDE) is True
    assert p.better_or_same_as(91.5, ASK_SIDE) is True


def test_better_or_same_as_decimal():
    p = Price("91.5")
    assert p.better_or_same_as(Decimal(90.1), BID_SIDE) is True
    assert p.better_or_same_as(Decimal(92.1), BID_SIDE) is False
    assert p.better_or_same_as(Decimal(91.5), BID_SIDE) is True
    assert p.better_or_same_as(Decimal(90.1), ASK_SIDE) is False
    assert p.better_or_same_as(Decimal(92.1), ASK_SIDE) is True
    assert p.better_or_same_as(Decimal(91.5), ASK_SIDE) is True


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


def test_worse_than_int():
    p = Price("91.5")
    assert p.worse_than(90, BID_SIDE) is False
    assert p.worse_than(92, BID_SIDE) is True
    assert p.worse_than(90, ASK_SIDE) is True
    assert p.worse_than(92, ASK_SIDE) is False


def test_worse_than_float():
    p = Price("91.5")
    assert p.worse_than(90.1, BID_SIDE) is False
    assert p.worse_than(92.1, BID_SIDE) is True
    assert p.worse_than(91.5, BID_SIDE) is False
    assert p.worse_than(90.1, ASK_SIDE) is True
    assert p.worse_than(92.1, ASK_SIDE) is False
    assert p.worse_than(91.5, ASK_SIDE) is False


def test_worse_than_decimal():
    p = Price("91.5")
    assert p.worse_than(Decimal(90.1), BID_SIDE) is False
    assert p.worse_than(Decimal(92.1), BID_SIDE) is True
    assert p.worse_than(Decimal(91.5), BID_SIDE) is False
    assert p.worse_than(Decimal(90.1), ASK_SIDE) is True
    assert p.worse_than(Decimal(92.1), ASK_SIDE) is False
    assert p.worse_than(Decimal(91.5), ASK_SIDE) is False


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


def test_worse_or_same_as_int():
    p = Price("91.5")
    assert p.worse_or_same_as(90, BID_SIDE) is False
    assert p.worse_or_same_as(92, BID_SIDE) is True
    assert p.worse_or_same_as(90, ASK_SIDE) is True
    assert p.worse_or_same_as(92, ASK_SIDE) is False

    p = Price("91")
    assert p.worse_or_same_as(91, BID_SIDE) is True
    assert p.worse_or_same_as(91, ASK_SIDE) is True


def test_worse_or_same_as_float():
    p = Price("91.5")
    assert p.worse_or_same_as(90.1, BID_SIDE) is False
    assert p.worse_or_same_as(92.1, BID_SIDE) is True
    assert p.worse_or_same_as(91.5, BID_SIDE) is True
    assert p.worse_or_same_as(90.1, ASK_SIDE) is True
    assert p.worse_or_same_as(92.1, ASK_SIDE) is False
    assert p.worse_or_same_as(91.5, ASK_SIDE) is True


def test_worse_or_same_as_decimal():
    p = Price("91.5")
    assert p.worse_or_same_as(Decimal(90.1), BID_SIDE) is False
    assert p.worse_or_same_as(Decimal(92.1), BID_SIDE) is True
    assert p.worse_or_same_as(Decimal(91.5), BID_SIDE) is True
    assert p.worse_or_same_as(Decimal(90.1), ASK_SIDE) is True
    assert p.worse_or_same_as(Decimal(92.1), ASK_SIDE) is False
    assert p.worse_or_same_as(Decimal(91.5), ASK_SIDE) is True


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
    p3 = Price('0.01')
    assert p1 + p2 == Decimal('2.5')
    assert p2 + p1 == Decimal('2.5')
    assert p2 - p1 == Decimal('.2')
    assert p1 - p2 == Decimal('-0.2')
    assert p1 * p2 == Decimal('1.5525')
    assert p2 * p1 == Decimal('1.5525')
    assert p1 / p3 == Decimal('115')
