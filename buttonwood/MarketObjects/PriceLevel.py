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
from buttonwood.MarketObjects.Side import Side


class PriceLevel(object):
    def __init__(self, price, visible_qty, hidden_qty=0, num_orders=None):
        """
        A price level is one price of one side of a book. It summarizes all the basic data found at that price, including
         the price itself, the visible qty, the hidden qty, and the number of orders. Hidden Qty is optional as many
         markets don't have it as an option. And number of orders is optional because based on the market that's data is
         being processed you might not have knowledge of number of orders.
  
         Visible Qty must be greater than 0 because can't have negative qty and if 0 then shouldn't be a price level.
  
         Hidden Qty must be >=0 because can't have a negative qty at a price level.
  
         Number of orders must be >= visible qty + hidden_qty because smallest size per order is 1 so can't have more
          orders than qty.
  
         If number of orders is defined then it has to be > 0 as can't be negative and 0 would mean no price level.
  
        :param price: MarketObjects.Price. The level's price
        :param visible_qty: int. quantity that is at the price and visible
        :param hidden_qty: int. quantity that is at the price and hidden. Optional. Defaults to 0.
        :param num_orders: int. the number of orders that makes up the price level. Optional. Defaults to None.
        """
        assert isinstance(price, Price)
        assert isinstance(visible_qty, int)
        assert isinstance(hidden_qty, int)
        assert visible_qty > 0
        assert hidden_qty >= 0
        assert num_orders is None or isinstance(num_orders, int)
        assert num_orders is None or num_orders <= visible_qty + hidden_qty
        assert num_orders is None or num_orders > 0
        self._price = price
        self._visible_qty = visible_qty
        self._hidden_qty = hidden_qty
        self._num_orders = num_orders

    def price(self):
        """
        The price of the price level
  
        :return: Price
        """
        return self._price

    def total_qty(self):
        """
        The total qty on the price level, which is visible + hidden
  
        :return: int.
        """
        return self._visible_qty + self._hidden_qty

    def visible_qty(self):
        """
        The visible qty at the price level
  
        :return: int
        """
        return self._visible_qty

    def hidden_qty(self):
        """
        The hidden qty at the price level
  
        :return: int
        """
        return self._hidden_qty

    def number_of_orders(self):
        """
        The number of orders that make up the price level.
  
        :return: int. Can be None.
        """
        return self._num_orders

    def better_than(self, other_level, side):
        """
        returns if this price level is better than another price level for a given side of the market
        :param side: Side
        :param other_level: PriceLevel
        :return: bool
        """
        assert isinstance(other_level, PriceLevel)
        assert isinstance(side, Side)
        return self.price().better_than(other_level.price(), side)

    def better_or_same_as(self, other_level, side):
        """
        returns if this price level is better than or same as another price level for a given side of the market
        :param side: Side
        :param other_level: PriceLevel
        :return: bool
        """
        assert isinstance(other_level, PriceLevel)
        assert isinstance(side, Side)
        return self.price().better_or_same_as(other_level.price(), side)

    def worse_than(self, other_level, side):
        """
        returns if this price level is worse than another price level for a given side of the market
        :param side: Side
        :param other_level: PriceLevel
        :return: bool
        """
        assert isinstance(other_level, PriceLevel)
        assert isinstance(side, Side)
        return self.price().worse_than(other_level.price(), side)

    def worse_or_same_as(self, other_level, side):
        """
        returns if this price level is worse than or same as another price level for a given side of the market
        :param side: Side
        :param other_level: PriceLevel
        :return: bool
        """
        assert isinstance(other_level, PriceLevel)
        assert isinstance(side, Side)
        return self.price().worse_or_same_as(other_level.price(), side)

    def __eq__(self, other):
        assert isinstance(other, PriceLevel)
        if other is None:
            return False
        if self.price() != other.price():
            return False
        if self.visible_qty() != other.visible_qty():
            return False
        if self.hidden_qty() != other.hidden_qty():
            return False
        if self.number_of_orders() is not None and other.number_of_orders() is not None:
            if self.number_of_orders() != other.number_of_orders():
                return False
        else:
            if self.number_of_orders() is None and other.number_of_orders() is not None:
                return False
            if self.number_of_orders() is not None and other.number_of_orders() is None:
                return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        s = "%s : %d | %d" % (str(self._price), self.visible_qty(), self.hidden_qty())
        if self._num_orders is not None:
            s = s + " (%d)" % self._num_orders
        return s
