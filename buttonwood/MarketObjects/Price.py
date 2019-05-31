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

from cdecimal import Decimal
from buttonwood.MarketObjects.Side import Side


class Price(object):
    def __init__(self, price_value):
        """
        Represents a price. Is created with a string, for accuracy, or as a Decimal and is kept as a Decimal
  
        :param price_value: str
        """
        assert isinstance(price_value, str) or isinstance(price_value, Decimal)
        self._price = Decimal(price_value)  # yup, this is do-able. You can instantiate a Decimal with another Decimal
        self._hash = hash(price_value)

    def price(self):
        """
        Gets the underlying price of the Price object as a Decimal
        :return: Decimal
        """
        return self._price

    def better_than(self, other_price, side):
        """
        Determines if this price is better than the passed in price. Returns True if it is and False if it isn't.
        The determination is made using the passed in side:
           *if side is bid then better than means a higher price
           *if side is ask then better than means a lower price
           *if side is other then there is no such thing as a better price so the return is False
        
        :param other_price: Price. the price you are comparing to
        :param side: Side. the side used for the comparison
        :return: boolean
        """
        assert isinstance(other_price, Price), "other_price should be MarketObjects.Price.Price"
        assert isinstance(side, Side), "side should be MarketObjects.Side.Side"
        # if this price is a bid it is better than otherPrice if greater than

        if side.is_bid():
            return self._price > other_price._price
        # otherwise price is an ask and it is better than otherPrice if less than
        else:
            return self._price < other_price._price

    def better_or_same_as(self, other_price, side):
        """
        Determines if this price is better than or same as the passed in price.
        Returns True if it is and False if it isn't.
        The determination is made using the passed in side:
           *if side is bid then better than means a higher price
           *if side is ask then better than means a lower price
           *if side is other then there is no such thing as a better price so the return is False
        
        :param other_price: Price. the price you are comparing to
        :param side: Side. the side used for the comparison
        :return: boolean
        """
        assert isinstance(other_price, Price), "other_price should be MarketObjects.Price.Price"
        assert isinstance(side, Side), "side should be MarketObjects.Side.Side"
        if other_price._price == self._price:
            return True
        return self.better_than(other_price, side)

    def worse_than(self, other_price, side):
        """
        Determines if this price is worse than the passed in price.
        Returns True if it is and False if it isn't.
        The determination is made using the passed in side:
           *if side is bid then worse than means a lower price
           *if side is ask then worse than means a higher price
           *if side is other then there is no such thing as a worse price so the return is False
        
        :param other_price: Price. the price you are comparing to
        :param side: Side. the side used for the comparison
        :return: boolean
        """
        # if this price is a bid it is worse than otherPrice if less than
        assert isinstance(other_price, Price), "other_price should be MarketObjects.Price.Price"
        assert isinstance(side, Side), "side should be MarketObjects.Side.Side"
        if side.is_bid():
            return self._price < other_price._price
        # otherwise price is an ask and it is worse than otherPrice if greater than
        else:
            return self._price > other_price._price

    def worse_or_same_as(self, other_price, side):
        """
        Determines if this price is worse than or same as the passed in price.
        Returns True if it is and False if it isn't.
        The determination is made using the passed in side:
           *if side is bid then worse than means a lower price
           *if side is ask then worse than means a higher price
           *if side is other then there is no such thing as a worse price so the return is False

        :param other_price: Price. the price you are comparing to
        :param side: Side. the side used for the comparison
        :return: boolean
        """
        assert isinstance(other_price, Price), "other_price should be MarketObjects.Price.Price"
        assert isinstance(side, Side), "side should be MarketObjects.Side.Side"
        if other_price._price == self._price:
            return True
        return self.worse_than(other_price, side)

    def ticks_behind(self, other_price, side, product):
        """
        For bids it subtracts its own price from the other price and divides by mpi
  
        For asks it subtracts the other price from its own price and divides by mpi.
  
        The result is if the other price is a better price then we get a positive
         number and if the other price is a worse price, we get a negative number.
  
        If otherprice is none it returns None
        :param other_price: MarketObjects.Price.Price the price you are comparing too
        :param side: MMarketObjects.Side.Side side of the market the comparison is happening on
        :param product: MarketObjects.Product.Product
        :return: float Can be None
        """
        if other_price is None:
            return None

        if side.is_bid():
            return (other_price._price - self._price) / product.mpi()
        else:
            return (self._price - other_price._price) / product.mpi()

    def __lt__(self, other):
        if isinstance(other, Price):
            return self._price < other._price
        if isinstance(other, (float, int, Decimal)):
            return self._price < other
        return None

    def __le__(self, other):
        if isinstance(other, Price):
            return self._price <= other._price
        if isinstance(other, (float, int, Decimal)):
            return self._price <= other
        return None

    def __gt__(self, other):
        if isinstance(other, Price):
            return self._price > other._price
        if isinstance(other, (float, int, Decimal)):
            return self._price > other
        return None

    def __ge__(self, other):
        if isinstance(other, Price):
            return self._price >= other._price
        if isinstance(other, (float, int, Decimal)):
            return self._price >= other
        return None

    def __eq__(self, other):
        if isinstance(other, Price):
            return self._price == other._price
        if isinstance(other, (float, int, Decimal)):
            return self._price == other
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self._hash

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return str(self.price())

    def __rsub__(self, other):
        return other - self._price

    def __sub__(self, other):
        return self._price - other

    def __radd__(self, other):
        return other + self._price

    def __add__(self, other):
        return self._price + other

    def __div__(self, other):
        return self._price / self.__math_val(other)

    def __mul__(self, other):
        return self._price * self.__math_val(other)

    def __math_val(self, obj):
        val = obj
        if isinstance(obj, Price):
            val = obj.price()
        return val
