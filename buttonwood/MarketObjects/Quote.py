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

from buttonwood.MarketObjects.PriceLevel import PriceLevel
from buttonwood.MarketObjects.Side import Side
from buttonwood.MarketObjects.Market import Market
from buttonwood.MarketObjects.Price import Price


class Quote(object):
    def __init__(self, market, side, price, visible_qty, hidden_qty=0):
        """
        An individual quote expressing a desire to buy or sell a Product for a Price. Visible qty is required and
         hidden qty is optional, defaulting to 0 because many markets don't support hidden quantity.
  
        :param market: MarketObjects.Market.Market.
        :param side: Side.
        :param price: Price.
        :param visible_qty: int. Must be greater than 0
        :param hidden_qty: int. Must be 0 or more. Optional. Defaults to 0.
        """
        assert isinstance(price, Price) or isinstance(price, str)
        assert isinstance(side, Side)
        assert isinstance(market, Market)
        assert isinstance(visible_qty, int)
        assert isinstance(hidden_qty, int)
        assert visible_qty > 0, "A quote's visible qty must be greater than 0"
        assert hidden_qty >= 0, "A quote's hidden qty must be greater than or equal to 0"
        use_price = price
        if isinstance(price, str):
            use_price = Price(price)
        assert market.product().is_valid_price(use_price), \
            "%s is not a valid price for a product with minimum price increment %s" % \
            (str(use_price), str(market.product().mpi()))
        self._side = side
        self._market = market
        self._price_level = PriceLevel(use_price, visible_qty, hidden_qty, num_orders=1)

    def side(self):
        """
        Get the side of the market the quote is for
  
        :return: Side
        """
        return self._side

    def market(self):
        """
        Get the market the quote is for
  
        :return: MarketObjects.Market.Market
        """
        return self._market

    def price(self):
        """
        Get the price of the quote
  
        :return: Price.
        """
        return self._price_level.price()

    def visible_qty(self):
        """
        Get the visible qty of the quote
  
        :return: int
        """
        return self._price_level.visible_qty()

    def hidden_qty(self):
        """
        Get the hidden qty of the quote
  
        :return: int
        """
        return self._price_level.hidden_qty()

    def total_qty(self):
        """
        Get the total qty of the quote.
  
        :return: int.
        """
        return self._price_level.hidden_qty() + self._price_level.visible_qty()

    def is_buy(self):
        """
        Tells if you the Quote is a buy or not
  
        :return: bool
        """
        return self._side.is_bid()

    def is_sell(self):
        """
        Tells if you the Quote is a sell or not
  
        :return: bool
        """
        return self._side.is_ask()

    def __eq__(self, other):
        if not isinstance(other, Quote):
            return False
        return self._price_level == other._price_level and \
               self.side() == other.side() and \
               self.market() == other.market()

    def __str__(self):
        return "%s Quote: %s %d (%d visible, %d hidden) at %s" % \
               (str(self.market()),
                "Buy" if self.is_buy() else "Sell",
                self.total_qty(),
                self.visible_qty(),
                self.hidden_qty(),
                str(self.price()))
