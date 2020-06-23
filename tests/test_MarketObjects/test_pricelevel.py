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

import pytest
from buttonwood.MarketObjects.PriceLevel import PriceLevel
from buttonwood.MarketObjects.Price import Price
from buttonwood.MarketObjects.Side import BID_SIDE, ASK_SIDE


def test_pricelevel_creation():
    pl = PriceLevel(Price("84.5"), 12)
    assert pl.price() == Price("84.5")
    assert pl.number_of_orders() is None
    assert pl.visible_qty() == 12
    assert pl.hidden_qty() == 0

    pl = PriceLevel(Price("32.134"), 14, 23)
    assert pl.price() == Price("32.134")
    assert pl.number_of_orders() is None
    assert pl.visible_qty() == 14
    assert pl.hidden_qty() == 23


def test_negative_visible_qty_fails():
    with pytest.raises(AssertionError):
        PriceLevel(Price("23.33"), -2)


def test_zero_visible_qty_fails():
    with pytest.raises(AssertionError):
        PriceLevel(Price("23.33"), 0)


def test_zero_hidden_qty_works():
    pl = PriceLevel(Price("23.33"), 3, 0)
    assert pl.hidden_qty() == 0


def test_negative_hidden_qty_failes():
    with pytest.raises(AssertionError):
        PriceLevel(Price("23.33"), 3, -3)


def test_pricelevel_must_have_price():
    with pytest.raises(AssertionError):
        PriceLevel(None, -2)


def test_visible_qty_must_be_int():
    with pytest.raises(AssertionError):
        PriceLevel(Price("1.1"), 3.0)


def test_hidden_qty_must_be_int():
    with pytest.raises(AssertionError):
        PriceLevel(Price("1.1"), 3, 4.0)


def test_negative_num_orders_fails():
    with pytest.raises(AssertionError):
        PriceLevel(Price("1.1"), 3, 4, -2)


def test_zero_num_orders_fails():
    with pytest.raises(AssertionError):
        PriceLevel(Price("1.1"), 3, 4, 0)


def test_cannot_have_more_orders_than_qty():
    with pytest.raises(AssertionError):
        PriceLevel(Price("1.1"), 3, 2, 8)


def test_better_than():
    pl1 = PriceLevel(Price("1.4"), 2, 3, 2)
    pl2 = PriceLevel(Price("1.1"), 2, 3, 2)
    assert pl1.better_than(pl2, BID_SIDE)
    assert pl2.better_than(pl1, BID_SIDE) is False
    assert pl1.better_than(pl2, ASK_SIDE) is False
    assert pl2.better_than(pl1, ASK_SIDE)


def test_better_or_same_as():
    pl1 = PriceLevel(Price("1.4"), 2, 3, 2)
    pl2 = PriceLevel(Price("1.1"), 2, 3, 2)
    pl3 = PriceLevel(Price("1.4"), 24, 4, 22)
    assert pl1.better_or_same_as(pl2, BID_SIDE)
    assert pl2.better_or_same_as(pl1, BID_SIDE) is False
    assert pl1.better_or_same_as(pl2, ASK_SIDE) is False
    assert pl2.better_or_same_as(pl1, ASK_SIDE)
    assert pl1.better_or_same_as(pl3, BID_SIDE)
    assert pl1.better_or_same_as(pl3, ASK_SIDE)


def test_worse_than():
    pl1 = PriceLevel(Price("1.6"), 2, 3, 2)
    pl2 = PriceLevel(Price("2.1"), 2, 3, 2)
    assert pl1.worse_than(pl2, BID_SIDE)
    assert pl2.worse_than(pl1, BID_SIDE) is False
    assert pl1.worse_than(pl2, ASK_SIDE) is False
    assert pl2.worse_than(pl1, ASK_SIDE)


def test_worse_or_same_as():
    pl1 = PriceLevel(Price("1.6"), 2, 3, 2)
    pl2 = PriceLevel(Price("2.1"), 2, 3, 2)
    pl3 = PriceLevel(Price("1.6"), 24, 4, 22)
    assert pl1.worse_or_same_as(pl2, BID_SIDE)
    assert pl2.worse_or_same_as(pl1, BID_SIDE) is False
    assert pl1.worse_or_same_as(pl2, ASK_SIDE) is False
    assert pl2.worse_or_same_as(pl1, ASK_SIDE)
    assert pl1.worse_or_same_as(pl3, BID_SIDE)
    assert pl1.worse_or_same_as(pl3, ASK_SIDE)


def test_equality():
    pl1 = PriceLevel(Price("1.1"), 2, 3, 2)
    pl2 = PriceLevel(Price("1.1"), 2, 3, 2)
    pl_price_different = PriceLevel(Price("1.2"), 2, 3, 2)
    pl_visible_qty_different = PriceLevel(Price("1.1"), 3, 3, 2)
    pl_hidden_qty_different = PriceLevel(Price("1.1"), 2, 332, 2)
    pl_num_orders_different = PriceLevel(Price("1.1"), 2, 3, 3)
    pl_num_orders_none = PriceLevel(Price("1.1"), 2, 3, None)
    assert pl1 == pl2
    assert pl1 != pl_price_different
    assert pl1 != pl_visible_qty_different
    assert pl1 != pl_hidden_qty_different
    assert pl1 != pl_num_orders_different
    assert pl1 != pl_num_orders_none

    pl1_num_orders_none = PriceLevel(Price("1.1"), 2, 3)
    pl2_num_orders_none = PriceLevel(Price("1.1"), 2, 3)
    assert pl1_num_orders_none == pl2_num_orders_none
    assert pl1 != pl2_num_orders_none
    assert pl2 != pl1_num_orders_none
