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
from nose.tools import *
from MarketPy.MarketObjects.Quote import Quote
from MarketPy.MarketObjects.Side import BID_SIDE, ASK_SIDE
from MarketPy.MarketObjects.Product import Product
from MarketPy.MarketObjects.TwoSidedQuote import TwoSidedQuote

def test_successful_instantiation_no_cross():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    assert tsq.buy_quote() == bid_quote
    assert tsq.sell_quote() == ask_quote
    TwoSidedQuote(bid_quote, ask_quote, False)
    TwoSidedQuote(bid_quote, None)
    TwoSidedQuote(None, ask_quote)
    TwoSidedQuote(None, None)

@raises(AssertionError)
def test_failed_instantiation_bid_quote_not_a_bid():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, ASK_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    TwoSidedQuote(bid_quote, ask_quote)

@raises(AssertionError)
def test_failed_instantiation_sell_quote_not_an_ask():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, BID_SIDE, "26.20", 233)
    TwoSidedQuote(bid_quote, ask_quote)

@raises(Exception)
def test_failed_instantiation_products_not_the_same():
    product1 = Product("MSFT", "microsoft", "0.01", "0.01")
    product2 = Product("APPL", "Apple", "0.01", "0.01")
    bid_quote = Quote(product1, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product2, ASK_SIDE, "26.20", 233)
    TwoSidedQuote(bid_quote, ask_quote)

@raises(Exception)
def test_failed_instantiation_locked_market():
    product1 = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product1, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product1, ASK_SIDE, "25.23", 233)
    TwoSidedQuote(bid_quote, ask_quote)

@raises(Exception)
def test_failed_instantiation_crossed_market():
    product1 = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product1, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product1, ASK_SIDE, "25.20", 233)
    TwoSidedQuote(bid_quote, ask_quote)

def test_successful_instantiation_locked_market_allowed():
    product1 = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product1, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product1, ASK_SIDE, "25.23", 233)
    TwoSidedQuote(bid_quote, ask_quote, True)

def test_successful_instantiation_crossed_market_allowed():
    product1 = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product1, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product1, ASK_SIDE, "18.42", 233)
    TwoSidedQuote(bid_quote, ask_quote, True)

def test_successful_set_buy_quote():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    bid_quote2 = Quote(product, BID_SIDE, "25.25", 43)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    assert tsq.buy_quote() == bid_quote
    assert tsq.sell_quote() == ask_quote
    tsq.set_buy_quote(bid_quote2)
    assert tsq.buy_quote() == bid_quote2
    assert tsq.sell_quote() == ask_quote

def test_successful_set_sell_quote():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(product, ASK_SIDE, "25.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    assert tsq.buy_quote() == bid_quote
    assert tsq.sell_quote() == ask_quote
    tsq.set_sell_quote(ask_quote2)
    assert tsq.buy_quote() == bid_quote
    assert tsq.sell_quote() == ask_quote2

@raises(Exception)
def test_failed_set_sell_quote_wrong_product():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    product2 = Product("APPL", "Apple", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(product2, ASK_SIDE, "25.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_sell_quote(ask_quote2)

@raises(AssertionError)
def test_failed_set_sell_quote_wrong_side():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(product, BID_SIDE, "25.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_sell_quote(ask_quote2)

@raises(AssertionError)
def test_failed_set_buy_quote_wrong_side():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    buy_quote2 = Quote(product, ASK_SIDE, "25.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_buy_quote(buy_quote2)


@raises(Exception)
def test_failed_set_buy_quote_crossed_market():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    buy_quote2 = Quote(product, BID_SIDE, "26.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_buy_quote(buy_quote2)

@raises(Exception)
def test_failed_set_buy_quote_locked_market():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    buy_quote2 = Quote(product, BID_SIDE, "26.20", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_buy_quote(buy_quote2)

@raises(Exception)
def test_failed_set_buy_quote_wrong_product():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    product2 = Product("APPL", "Apple", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    buy_quote2 = Quote(product2, BID_SIDE, "25.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_buy_quote(buy_quote2)

@raises(Exception)
def test_failed_set_sell_quote_crossed_market():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(product, ASK_SIDE, "24.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_sell_quote(ask_quote2)

@raises(Exception)
def test_failed_set_sell_quote_locked_market():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(product, BID_SIDE, "25.23", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_sell_quote(ask_quote2)

def test_successful_set_buy_quote_locked_market():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    buy_quote2 = Quote(product, BID_SIDE, "26.20", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote, True)
    tsq.set_buy_quote(buy_quote2)

def test_successful_set_buy_quote_crossed_market():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    buy_quote2 = Quote(product, BID_SIDE, "28.20", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote, True)
    tsq.set_buy_quote(buy_quote2)

def test_successful_set_sell_quote_crossed_market():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(product, ASK_SIDE, "24.20", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote, True)
    tsq.set_sell_quote(ask_quote2)

def test_successful_set_sell_quote_locked_market():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(product, ASK_SIDE, "25.23", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote, True)
    tsq.set_sell_quote(ask_quote2)

def test_spread():
    product = Product("MSFT", "microsoft", "0.01", "0.01")
    bid_quote = Quote(product, BID_SIDE, "25.23", 18)
    ask_quote = Quote(product, ASK_SIDE, "26.20", 233)
    tsq = TwoSidedQuote(bid_quote, ask_quote, True)
    assert tsq.spread() == 97
    #now lock the market
    ask_quote2 = Quote(product, ASK_SIDE, "25.23", 2334)
    tsq.set_sell_quote(ask_quote2)
    assert tsq.spread() == 0
    #now cross the market
    ask_quote3 = Quote(product, ASK_SIDE, "24.23", 2334)
    tsq.set_sell_quote(ask_quote3)
    assert tsq.spread() == -100
    #now test ask None
    tsq.set_sell_quote(None)
    assert tsq.spread() is None
    #now test both None
    tsq.set_buy_quote(None)
    assert tsq.spread() is None
    #now only buy is none
    tsq.set_sell_quote(ask_quote3)