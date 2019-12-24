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

from nose.tools import *
from buttonwood.MarketObjects.Events.OrderEvents import CancelReplaceCommand
from buttonwood.MarketObjects.Endpoint import Endpoint
from buttonwood.MarketObjects.Market import Market
from buttonwood.MarketObjects.Price import Price
from buttonwood.MarketObjects.Price import PriceFactory
from buttonwood.MarketObjects.Product import Product
from buttonwood.MarketObjects.Side import ASK_SIDE

MARKET = Market(Product("MSFT", "Microsoft"), Endpoint("Nasdaq", "NSDQ"), PriceFactory("0.01"))


def test_creation():
    cr = CancelReplaceCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, ASK_SIDE, Price("23.01"), 234, 2)
    assert cr.event_type_str() == "Cancel Replace Command"
    assert cr.price() == Price("23.01")
    assert cr.market() == MARKET
    assert cr.user_id() == "user_x"
    assert cr.timestamp() == 324893458.324313
    assert cr.event_id() == 12
    assert cr.qty() == 234
    assert cr.iceberg_peak_qty() == 2

@raises(AssertionError)
def test_error_on_negative_qty():
    CancelReplaceCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, ASK_SIDE, Price("23.01"), -8, 2)

@raises(AssertionError)
def test_error_on_negative_iceberg_qty():
    CancelReplaceCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, ASK_SIDE, Price("23.01"), 8, -2)

@raises(AssertionError)
def test_error_on_price_not_matching_product():
    CancelReplaceCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, ASK_SIDE, Price("23.001"), 8, -2)
