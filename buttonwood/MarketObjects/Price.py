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

import json
import decimal
from decimal import Decimal
from buttonwood.MarketObjects.Side import Side
from buttonwood.MarketObjects.Side import BID_SIDE


class InvalidPriceException(Exception):
    pass


class Price:

    def __init__(self, price_value, precision=Decimal(".111111111111111")):  # precision defaults to 15
        if isinstance(price_value, Decimal):
            self.__value = price_value
        elif isinstance(price_value, float):
            self.__value = Decimal(price_value).quantize(precision, rounding=decimal.ROUND_HALF_UP)
        else:
            self.__value = Decimal(price_value)
        self.__hash = self.__value.__hash__()
        self.__float_value = float(self.__value)
        self.__precision = precision

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
        assert isinstance(side, Side), "side should be MarketObjects.Side.Side"
        # if this price is a bid it is better than otherPrice if greater than

        if side.is_bid():
            return self > other_price
        # otherwise price is an ask and it is better than otherPrice if less than
        else:
            return self < other_price

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
        return True if other_price == self else self.better_than(other_price, side)

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
        assert isinstance(other_price, Price), "other_price should be MarketObjects.Price.Price"
        assert isinstance(side, Side), "side should be MarketObjects.Side.Side"
        # if this price is a bid it is worse than otherPrice if less than
        if side.is_bid():
            return self < other_price
        # otherwise price is an ask and it is worse than otherPrice if greater than
        else:
            return self > other_price

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
        return True if other_price == self else self.worse_than(other_price, side)

    def ticks_behind(self, other_price, side, market):
        """
        For bids it subtracts its own price from the other price and divides by mpi
  
        For asks it subtracts the other price from its own price and divides by mpi.
  
        The result is if the other price is a better price then we get a positive
         number and if the other price is a worse price, we get a negative number.
  
        If otherprice is none it returns None
        :param other_price: MarketObjects.Price.Price the price you are comparing too
        :param side: MMarketObjects.Side.Side side of the market the comparison is happening on
        :param market: MarketObjects.Market.Market
        :return: float Can be None
        """
        if other_price is None:
            return None

        if side.is_bid():
            return (other_price - self) / market.mpi()
        else:
            return (self - other_price) / market.mpi()

    def __hash__(self):
        return self.__hash

    def __repr__(self):
        return self.__value.__repr__()

    def __str__(self):
        return self.__value.__str__()

    def __lt__(self, other):
        if not isinstance(other, Price):
            raise TypeError(other, '< requires another Price object')
        else:
            return self.__value < other.__value

    def __le__(self, other):
        if not isinstance(other, Price):
            raise TypeError(other, '<= requires another Price object')
        else:
            return self.__value <= other.__value

    def __eq__(self, other):
        if isinstance(other, Price):
            return self.__value == other.__value
        else:
            return self.__value == Price(other).__value

    def __ne__(self, other):
        return not self == other

    def __gt__(self, other):
        if not isinstance(other, Price):
            raise TypeError(other, '> requires another Price object')
        else:
            return self.__value > other.__value

    def __ge__(self, other):
        if not isinstance(other, Price):
            raise TypeError(other, '>= requires another Price object')
        else:
            return self.__value >= other.__value

    def __bool__(self):
        return bool(self.__value)

    def __add__(self, other):
        if isinstance(other, float):
            value = self.__float_value + other
        else:
            if isinstance(other, Price):
                other = other.__value
            value = self.__value + other
        return self.__class__(value, precision=self.__precision)

    def __radd__(self, other):
        return self.__add__(other)

    def __sub__(self, other):
        if isinstance(other, float):
            value = self.__float_value - other
        else:
            if isinstance(other, Price):
                other = other.__value
            value = self.__value - other
        return self.__class__(value, precision=self.__precision)

    def __rsub__(self, other):
        return (-self).__add__(other)

    def __mul__(self, other):
        if isinstance(other, float):
            value = self.__float_value * other
        else:
            if isinstance(other, Price):
                raise TypeError("Two prices cannot be multiplied")  # just doesn't make sense. Why would someone do this?
            value = self.__value * other
        return self.__class__(value, precision=self.__precision)

    def __rmul__(self, other):
        return self.__mul__(other)

    def __div__(self, other):
        return self.__truediv__(other)

    def __truediv__(self, other):
        if isinstance(other, Price):
            # not really sure why someone would want to divide a price by another price
            raise TypeError("Two prices cannot be divided")
        else:
            if other == 0:
                raise ZeroDivisionError()
            if isinstance(other, float):
                value = self.__float_value / other
            else:
                value = self.__value / other
        return self.__class__(value, precision=self.__precision)

    def __floordiv__(self, other):
        if isinstance(other, Price):
            # not really sure why someone would want to divide a price by another price
            raise TypeError("Two prices cannot be divided")
        else:
            if other == 0:
                raise ZeroDivisionError()
            if isinstance(other, float):
                value = self.__float_value // other
            else:
                value = self.__value // other
        return self.__class__(value, precision=self.__precision)

    def __mod__(self, other):
        if isinstance(other, Price):
            # not really sure why someone would want to modulo a price by another price
            raise TypeError("modulo of two prices is not supported")
        if other == 0:
            raise ZeroDivisionError()
        if isinstance(other, float):
            value = self.__float_value % other
        else:
            value = self.__value % other
        return self.__class__(value, precision=self.__precision)

    def __divmod__(self, other):
        raise TypeError("divmod of a price is not supported")

    def __pow__(self, other):
        raise TypeError("pow of a price is not supported")

    def __neg__(self):
        return self.__class__(-self.__value)

    def __pos__(self):
        return self.__class__(+self.__value)

    def __abs__(self):
        return self.__class__(abs(self.__value))

    def __int__(self):
        return int(self.__value)

    def __float__(self):
        return self.__float_value


class PriceFactory:

    def __init__(self, min_price_increment, min_price_increment_value=1, min_price=Price(-999999),
                 max_price=Price(999999), precision=Decimal(".111111111111111")):
        assert isinstance(min_price_increment, (Decimal, str, int))
        assert isinstance(min_price_increment_value, (Decimal, str, int))
        assert isinstance(precision, Decimal)
        self._precision = precision
        self._mpi = Decimal(min_price_increment)
        # if mpi has a decimal then precision needs be more precise than min_price_increment's decimal
        mpi_decimal_len = 0
        precision_len = 0
        if str(self._mpi).find(".") > -1:
            mpi_decimal_len = len(str(self._mpi).split(".")[1])
        if str(self._precision).find(".") > -1:
            precision_len = len(str(self._precision).split(".")[1])
        assert precision_len >= mpi_decimal_len, "precision needs to be more precise than min_price_increment"
        self._mpi_value = Decimal(min_price_increment_value)
        self._min_price = min_price if isinstance(min_price, Price) else Price(min_price)
        self._max_price = max_price if isinstance(max_price, Price) else Price(max_price)
        assert self._min_price <= self._max_price, "Max price (%s) must be greater than or equal to min price (%s)." % \
                                                   (str(max_price), str(min_price))

    def next_price(self, price, side):
        return self.get_price(price + (self._mpi * (1 if side is BID_SIDE else -1)))

    def prev_price(self, price, side):
        return self.get_price(price + (self._mpi * (-1 if side is BID_SIDE else 1)))

    def get_price(self, price_value):
        price = price_value if isinstance(price_value, Price) else Price(price_value)
        if not self.is_valid_price(price):
            raise InvalidPriceException("%s is not valid price with min %s max %s and mpi %s" %
                                        (str(price_value), str(self._min_price), str(self._max_price), str(self._mpi)))
        return price

    def min_price_increment(self):
        """
        Gets the minimum price increment of a product. This is the smallest increment that the product trades in.
        :return: Decimal
        """
        return self._mpi

    def min_price_increment_value(self):
        """
        Gets the monetary value associated with the minimum price increment of a product.
        :return: Decimal
        """
        return self._mpi_value

    def mpi(self):
        """
        This is the same as `min_price_increment()'. It is just for the convenience of the developer.

        :return: Decimal
        """
        return self._mpi

    def mpi_value(self):
        """
        This is the same as `min_price_increment_value()'. It is just for the convenience of the developer.

        :return: Decimal
        """
        return self._mpi_value

    def is_valid_price(self, price):
        if not isinstance(price, Price):
            price = Price(price)
        return (self._min_price <= price <= self._max_price) and (price % self._mpi) == 0

    def to_json(self):
        return {"mpi": str(self._mpi), "mpv": str(self._mpi_value), "min": str(self._min_price),
                "max": str(self._max_price)}

    def __str__(self):
        return json.dumps(self.to_json())
