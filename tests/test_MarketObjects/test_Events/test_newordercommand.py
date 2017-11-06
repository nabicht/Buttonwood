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

from nose.tools import *

from MarketPy.MarketObjects.Events.OrderEventConstants import *
from MarketPy.MarketObjects.Events.OrderEvents import NewOrderCommand
from MarketPy.MarketObjects.Endpoint import Endpoint
from MarketPy.MarketObjects.Market import Market
from MarketPy.MarketObjects.Price import Price
from MarketPy.MarketObjects.Product import Product
from MarketPy.MarketObjects.Side import BID_SIDE
from MarketPy.MarketObjects.Events.OrderEventConstants import MARKET
from MarketPy.MarketObjects.Events.OrderEventConstants import LIMIT

MARKET = Market(Product("MSFT", "Microsoft", "0.01", "0.01"), Endpoint("Nasdaq", "NSDQ"))

def test_creation():
    new_order = NewOrderCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, BID_SIDE, FAK,
                                Price("23.01"), 234, 2)
    assert new_order.event_type_str() == ("New Order Command")
    assert new_order.price() == Price("23.01")
    assert new_order.product() == MARKET
    assert new_order.user_id() == "user_x"
    assert new_order.timestamp() == 324893458.324313
    assert new_order.event_id() == 12
    assert new_order.side() == BID_SIDE
    assert new_order.qty() == 234
    assert new_order.iceberg_peak_qty() == 2

def test_is_market_order():
    #a market order is a FAK or a FOK, but not a FAR
    new_order = NewOrderCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, BID_SIDE, FAK,
                                Price("23.01"), 234, 2, limit_or_market=MARKET)
    assert new_order.is_market_order()

    new_order = NewOrderCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, BID_SIDE, FOK,
                                Price("23.01"), 234, 2, limit_or_market=LIMIT)
    assert new_order.is_market_order() == False

    new_order = NewOrderCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, BID_SIDE, FAR,
                                Price("23.01"), 234, 2)
    assert new_order.is_market_order() == False

def test_is_limit_order():
    #a market order is a FAR, but not a FAK or a FOK
    new_order = NewOrderCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, BID_SIDE, FAK,
                                Price("23.01"), 234, 2, limit_or_market=MARKET)
    assert new_order.is_limit_order() == False

    new_order = NewOrderCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, BID_SIDE, FOK,
                                Price("23.01"), 234, 2, limit_or_market=LIMIT)
    assert new_order.is_limit_order() == True

    new_order = NewOrderCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, BID_SIDE, FAR,
                                Price("23.01"), 234, 2)
    assert new_order.is_limit_order() == True

def test_neworder_defaults():
    new_order = NewOrderCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, BID_SIDE, FAK,
                                Price("23.01"), 234)
    #iceberg peak qty defaults to qty if not defined as argument
    assert new_order.iceberg_peak_qty() == 234

@raises(AssertionError)
def test_error_on_zero_qty():
    NewOrderCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, BID_SIDE, FAK,
                    Price("23.01"), 0, 2)

@raises(AssertionError)
def test_error_on_negative_qty():
    NewOrderCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, BID_SIDE, FAK,
                    Price("23.01"), -8, 2)

@raises(AssertionError)
def test_error_on_negative_iceberg_qty():
    NewOrderCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, BID_SIDE, FAK,
                    Price("23.01"), 8, -2)

@raises(AssertionError)
def test_error_on_price_not_matching_product():
    NewOrderCommand(12, 324893458.324313, "342adf24441", "user_x", MARKET, BID_SIDE, FAK,
                    Price("23.001"), 8, -2)
