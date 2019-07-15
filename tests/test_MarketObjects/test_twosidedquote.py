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
from buttonwood.MarketObjects.Quote import Quote
from buttonwood.MarketObjects.Side import ASK_SIDE
from buttonwood.MarketObjects.Side import BID_SIDE
from buttonwood.MarketObjects.Endpoint import Endpoint
from buttonwood.MarketObjects.Market import Market
from buttonwood.MarketObjects.Product import Product
from buttonwood.MarketObjects.Price import PriceFactory
from buttonwood.MarketObjects.TwoSidedQuote import TwoSidedQuote
from cdecimal import Decimal

MARKET = Market(Product("MSFT", "Microsoft"), Endpoint("Nasdaq", "NSDQ"), PriceFactory("0.01"))


def test_successful_instantiation_no_cross():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    assert tsq.buy_quote() == bid_quote
    assert tsq.sell_quote() == ask_quote
    TwoSidedQuote(bid_quote, ask_quote, False)
    TwoSidedQuote(bid_quote, None)
    TwoSidedQuote(None, ask_quote)
    TwoSidedQuote(None, None)


@raises(AssertionError)
def test_failed_instantiation_bid_quote_not_a_bid():
    bid_quote = Quote(MARKET, ASK_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    TwoSidedQuote(bid_quote, ask_quote)


@raises(AssertionError)
def test_failed_instantiation_sell_quote_not_an_ask():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, BID_SIDE, "26.20", 233)
    TwoSidedQuote(bid_quote, ask_quote)


@raises(Exception)
def test_failed_instantiation_products_not_the_same():
    market1 = Market(Product("MSFT", "Microsoft"), Endpoint("Nasdaq", "NSDQ"), PriceFactory(".01"))
    market2 = Market(Product("APPL", "Apple"), Endpoint("Nasdaq", "NSDQ"), PriceFactory(".01"))
    bid_quote = Quote(market1, BID_SIDE, "25.23", 18)
    ask_quote = Quote(market2, ASK_SIDE, "26.20", 233)
    TwoSidedQuote(bid_quote, ask_quote)


@raises(Exception)
def test_failed_instantiation_locked_market():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "25.23", 233)
    TwoSidedQuote(bid_quote, ask_quote)


@raises(Exception)
def test_failed_instantiation_crossed_market():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "25.20", 233)
    TwoSidedQuote(bid_quote, ask_quote)


def test_successful_instantiation_locked_market_allowed():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "25.23", 233)
    TwoSidedQuote(bid_quote, ask_quote, True)


def test_successful_instantiation_crossed_market_allowed():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "18.42", 233)
    TwoSidedQuote(bid_quote, ask_quote, True)


def test_successful_set_buy_quote():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    bid_quote2 = Quote(MARKET, BID_SIDE, "25.25", 43)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    assert tsq.buy_quote() == bid_quote
    assert tsq.sell_quote() == ask_quote
    tsq.set_buy_quote(bid_quote2)
    assert tsq.buy_quote() == bid_quote2
    assert tsq.sell_quote() == ask_quote


def test_successful_set_sell_quote():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(MARKET, ASK_SIDE, "25.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    assert tsq.buy_quote() == bid_quote
    assert tsq.sell_quote() == ask_quote
    tsq.set_sell_quote(ask_quote2)
    assert tsq.buy_quote() == bid_quote
    assert tsq.sell_quote() == ask_quote2


@raises(Exception)
def test_failed_set_sell_quote_wrong_product():
    market1 = Market(Product("MSFT", "Microsoft"), Endpoint("Nasdaq", "NSDQ"), PriceFactory("0.01"))
    market2 = Market(Product("APPL", "Apple"), Endpoint("Nasdaq", "NSDQ"), PriceFactory("0.01"))
    bid_quote = Quote(market1, BID_SIDE, "25.23", 18)
    ask_quote = Quote(market1, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(market2, ASK_SIDE, "25.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_sell_quote(ask_quote2)


@raises(AssertionError)
def test_failed_set_sell_quote_wrong_side():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(MARKET, BID_SIDE, "25.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_sell_quote(ask_quote2)


@raises(AssertionError)
def test_failed_set_buy_quote_wrong_side():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    buy_quote2 = Quote(MARKET, ASK_SIDE, "25.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_buy_quote(buy_quote2)


@raises(Exception)
def test_failed_set_buy_quote_crossed_market():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    buy_quote2 = Quote(MARKET, BID_SIDE, "26.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_buy_quote(buy_quote2)


@raises(Exception)
def test_failed_set_buy_quote_locked_market():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    buy_quote2 = Quote(MARKET, BID_SIDE, "26.20", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_buy_quote(buy_quote2)


@raises(Exception)
def test_failed_set_buy_quote_wrong_product():
    market1 = Market(Product("MSFT", "Microsoft"), Endpoint("Nasdaq", "NSDQ"), PriceFactory("0.01"))
    market2 = Market(Product("APPL", "Apple",), Endpoint("Nasdaq", "NSDQ"), PriceFactory("0.01"))
    bid_quote = Quote(market1, BID_SIDE, "25.23", 18)
    ask_quote = Quote(market1, ASK_SIDE, "26.20", 233)
    buy_quote2 = Quote(market2, BID_SIDE, "25.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_buy_quote(buy_quote2)


@raises(Exception)
def test_failed_set_sell_quote_crossed_market():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(MARKET, ASK_SIDE, "24.98", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_sell_quote(ask_quote2)


@raises(Exception)
def test_failed_set_sell_quote_locked_market():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(MARKET, BID_SIDE, "25.23", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote)
    tsq.set_sell_quote(ask_quote2)


def test_successful_set_buy_quote_locked_market():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    buy_quote2 = Quote(MARKET, BID_SIDE, "26.20", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote, True)
    tsq.set_buy_quote(buy_quote2)


def test_successful_set_buy_quote_crossed_market():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    buy_quote2 = Quote(MARKET, BID_SIDE, "28.20", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote, True)
    tsq.set_buy_quote(buy_quote2)


def test_successful_set_sell_quote_crossed_market():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(MARKET, ASK_SIDE, "24.20", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote, True)
    tsq.set_sell_quote(ask_quote2)


def test_successful_set_sell_quote_locked_market():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    ask_quote2 = Quote(MARKET, ASK_SIDE, "25.23", 3)
    tsq = TwoSidedQuote(bid_quote, ask_quote, True)
    tsq.set_sell_quote(ask_quote2)


def test_spread():
    bid_quote = Quote(MARKET, BID_SIDE, "25.23", 18)
    ask_quote = Quote(MARKET, ASK_SIDE, "26.20", 233)
    tsq = TwoSidedQuote(bid_quote, ask_quote, True)
    assert tsq.spread() == 97
    # now lock the market
    ask_quote2 = Quote(MARKET, ASK_SIDE, "25.23", 2334)
    tsq.set_sell_quote(ask_quote2)
    assert tsq.spread() == 0
    # now cross the market
    ask_quote3 = Quote(MARKET, ASK_SIDE, "24.23", 2334)
    tsq.set_sell_quote(ask_quote3)
    assert tsq.spread() == -100
    # now test ask None
    tsq.set_sell_quote(None)
    assert tsq.spread() is None
    # now test both None
    tsq.set_buy_quote(None)
    assert tsq.spread() is None
    # now only buy is none
