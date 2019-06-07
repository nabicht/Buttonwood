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

from buttonwood.MarketObjects.Side import ASK_SIDE
from buttonwood.MarketObjects.Side import BID_SIDE


class BasicOrderBook(object):

    """
    BasicOrderBook includes the base functions for querying an order book,
     no matter the type of order book (price level, order level, or
     otherwise).

    As many of the functions are implemented as can be, and those that aren't
     (as indicate by raising a NotImplemented exception) need to be implemented
     by the inhereting class.

    The inhereting class is also responsible for creating and maintaining the
     underlying data structures as well as the functions (internal and exposed)
     that allow for the manipulation of that structure.

    :param market: MarketObjects.Market.Market
    :param logger: logger
    """

    def __init__(self, market, logger):
        self._logger = logger
        self._market = market

    def market(self):
        """
        Get the market of the order book.

        :return: MarketObjects.Market.Market
        """
        return self._market

    def name(self):
        """
        The name of the order book to be used in logging and other
         identification.

        :return: str
        """
        raise NotImplemented("%s: name() not implemented." % self.__class__.__name__)

    def last_update_time(self):
        """
        Get the last "market time" the order book was updated.

        Order books should be thought of as living breathing things that update
         when new information is applied, so knowing when the last update
         occurred is important.

        "Market Time" vs "clock time".
         Market Time is the time of the market, which is time that comes from
          the market messages.
         Clock time is the time of the server if one called a system call to get
          the current time.
         The last update time is market time and *not* clock time. Using Market
          Time throughout allows for analytics to be done on historical data
          and on live data removes the issue of transport time and queues
          throwing off the deltas between updates.

        The time that gets returned is microseconds since the epoch in seconds
         notation, where to the left of the decimal is an integer and to the
         right of the decimal is the microseconds

        :return: float
        """
        raise NotImplemented("%s: last_update_time() not implemented." % self.__class__.__name__)

    def price_is_bid(self, price):
        """
        Is the price a bid or not. True if the price is worse than or equal to
         the top of book bid price. If no top of book bid price then return
         False.

        :return: boolean
        """
        tob_bid = self.best_bid_price()
        if tob_bid is None:
            return False
        return price.worse_or_same_as(tob_bid, BID_SIDE)

    def price_is_ask(self, price):
        """
        Is the price an ask or not. True if the price is worse than or equal to
         the top of book ask price. If no top of book ask price then return
         False.

        :return: boolean
        """
        tob_ask = self.best_ask_price()
        if tob_ask is None:
            return False
        return price.worse_or_same_as(tob_ask, ASK_SIDE)

    def bid_prices(self):
        """
        All the bid prices currently live in the book in order from best to
         worst (highest to lowest).

        :return: list of MarketObjects.Price.Price
        """
        return self.prices(BID_SIDE)

    def ask_prices(self):
        """
        All the bid prices currently live in the book in order from best to
         worst (lowest to highest).

        :return: list of MarketObjects.Price.Price
        """
        return self.prices(ASK_SIDE)

    def prices(self, side):
        """
        All the prices currently live in the book at the specified side in order
         from best to worst price.

        :param side: MarketObjects.Side.Side
        :return: list of MarketObjects.Price.Price from best to worst
        """
        raise NotImplemented("%s: prices(side) not implemented." % self.__class__.__name__)

    def best_bid_price(self):
        """
        Returns the best price of the bid side of the book.
        Will return None if the side is empty.

        :return: MarketObjects.Price.Price. Can be None.
        """
        return self.best_price(BID_SIDE)

    def best_ask_price(self):
        """
        Returns the best price of the ask side of the book.
        Will return None if the side is empty.

        :return: MarketObjects.Price.Price. Can be None.
        """
        return self.best_price(ASK_SIDE)

    def best_price(self, side):
        """
        Returns the best price of the of the book (top of book price) for the
         specified side. Will return None if the side is empty

        :param: MarketObjects.Side.Side. Side getting TOB for.
        :return: MarketObjects.Price.Price.
        """
        prices = self.prices(side)
        if len(prices) == 0:
            return None
        return prices[0]

    def best_bid_level(self):
        """
        Gets the top of book price level on the bid

        :return: MarketObjects.PriceLevel.PriceLevel
        """
        return self.best_level(BID_SIDE)

    def best_ask_level(self):
        """
        Gets the top of book price level on the bid

        :return: MarketObjects.PriceLevel.PriceLevel
        """
        return self.best_level(ASK_SIDE)

    def best_level(self, side):
        """
        Gets the top of book price level for the given side

        :return: MarketObjects.PriceLevel.PriceLevel
        """
        raise NotImplemented("%s: best_level(side) not implemented." % self.__class__.__name__)

    def total_qty_at_price(self, side, price):
        """
        Gets the total quantity (which is visible + hidden) at a price for the
         given side.

        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price
        :return: int
        """
        return self.visible_qty_at_price(side, price) + self.hidden_qty_at_price(side, price)

    def visible_qty_at_price(self, side, price):
        """
        Gets the visible quantity at the price for the given side.

        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price
        :return: int
        """
        raise NotImplemented("%s visible_qty_at_price(side, price) not implemented" % self.__class__.__name__)

    def hidden_qty_at_price(self, side, price):
        """
        Gets the hidden quantity at the price for the given side.

        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price
        :return: int
        """
        raise NotImplemented("%s hidden_qty_at_price(side, price) not implemented" % self.__class__.__name__)

    def num_orders_at_price(self, side, price):
        """
        Get the number of orders at a price for the given side.

        :param side: MarketObjects.Side.Side.
        :param price: MarketObjects.Price.Price.
        :return: int.
        """
        raise NotImplemented("%s num_orders_at_price(side, price, include_hideen) not implemented" % self.__class__.__name__)
