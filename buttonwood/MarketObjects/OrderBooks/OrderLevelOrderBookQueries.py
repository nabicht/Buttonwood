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
from buttonwood.MarketObjects.Price import Price

def tob_price_level(order_book, side):
    assert isinstance(order_book, OrderLevelBook)
    assert isinstance(side, Side)
    if order_book is None:
        return None
    return order_book.best_level(side)

def modified_qty_at_price(order_book, side, price, ignore_order_ids, ignore_hidden):
    """
    Returns the qty at the given price and side. Will ignore the size for every order that is in ignore_order_ids.
    
    If ignore hidden is True then hidden qty not included. Otherwise it will be.
    
    If the price does not exist at that side of the order book, will return 0
    
    :param order_book: Buttonwood.MarketObjects.OrderBooks.OrderLevelOrderBook.OrderLevelOrderBook
    :param side: Buttonwood.MarketObjects.Side.Side
    :param price: Buttonwood.MarketObjects.Price.Price
    :param ignore_order_ids: set, list or any other collection that allows for "in" query
    :param ignore_hidden: bool
    :return: 
    """
    # TODO unit test
    assert isinstance(order_book, OrderLevelBook)
    assert isinstance(side, Side)
    assert isinstance(price, Price)
    assert isinstance(ignore_hidden, bool)
    if ignore_order_ids is not None:
        use_ignore_order_ids = ignore_order_ids

        chains = order_book.iter_order_chains_at_price(side, price)
        qty = 0
        for chain in chains:
            if chain.chain_id() not in use_ignore_order_ids:
                qty += chain.visible_qty()
                if not ignore_hidden:
                    qty += chain.hidden_qty()

    else:  # do this else to take advantage of any precalculation that might be done
        qty = order_book.level_at_price(side, price).total_qty()
    return qty



