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

from buttonwood.MarketObjects.Price import Price


def size_weighted_midpoint(bid_price, bid_qty, ask_price, ask_qty):
    assert(isinstance(bid_price, Price))
    assert(isinstance(ask_price, Price))
    bid_plus_ask_qty = bid_qty + ask_qty
    if bid_plus_ask_qty == 0:
        return None
    return ((bid_qty * ask_price.price()) + (ask_qty * bid_price.price())) / bid_plus_ask_qty


def size_weighted_midpoint_from_price_levels(bid_price_level, ask_price_level, include_hidden=False):
    if bid_price_level is None or ask_price_level is None:
        return None
    bid_qty = bid_price_level.visible_qty()
    ask_qty = ask_price_level.visible_qty()
    if include_hidden:
        bid_qty += bid_qty + bid_price_level.hidden_qty()
        ask_qty += ask_qty + ask_price_level.hidden_qty()
    return size_weighted_midpoint(bid_price_level.price(), bid_qty, ask_price_level.price(), ask_qty)
