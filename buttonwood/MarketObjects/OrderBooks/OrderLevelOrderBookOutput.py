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

from buttonwood.MarketObjects.OrderBooks.OrderLevelBook import OrderLevelBook
from buttonwood.MarketObjects.Side import Side
from buttonwood.MarketObjects.Side import ASK_SIDE
from buttonwood.MarketObjects.Side import BID_SIDE
import json


def _level_json(order_book_level, side, price):
    level_list = []
    for order_chain in order_book_level.iter_order_chains_at_price(side, price):
        chain_dict = dict()
        chain_dict["chain_id"] = order_chain.chain_id()
        chain_dict["subchain_id"] = order_chain.most_recent_subchain().subchain_id()
        chain_dict["total_qty"] = order_chain.total_qty()
        chain_dict["iceberg_peak"] = order_chain.self.iceberg_peak_qty()
        chain_dict["visible_qty"] = order_chain.visible_qty()
        chain_dict["hidden_qty"] = order_chain.hidden_qty()
        chain_dict["priority_time"] = order_chain.most_recent_subchain().open_event().timestamp()
        level_list.append(chain_dict)
    return level_list

def _side_json(order_book, side):
    assert isinstance(side, Side)
    side_list = []
    prices = order_book.prices(side)
    for price in prices:
        price_dict = dict()
        price_dict["price"] = float(price)
        price_dict["visible_qty"] = order_book.visible_qty_at_price(side, price)
        price_dict["hidden_qty"] = order_book.hidden_qty_at_price(side, price)
        price_dict["order_chains"] = _level_json(order_book, side, price)
        side_list.append(price_dict)
    side_dict = dict()
    side_dict["levels"] = side_list
    return side_dict

def json_snapshot(order_book):
    assert isinstance(order_book, OrderLevelBook)
    order_book_dict = dict()
    order_book_dict["Market"] = order_book.market().to_json()
    order_book_dict["last_update_time"] = order_book.last_update_time()
    order_book_dict[str(BID_SIDE)] = _side_json(order_book, BID_SIDE)
    order_book_dict[str(ASK_SIDE)] = _side_json(order_book, ASK_SIDE)
    return json.dumps(order_book_dict)

