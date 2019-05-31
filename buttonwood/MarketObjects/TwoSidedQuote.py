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

from buttonwood.MarketObjects.Quote import Quote


class TwoSidedQuote(object):

    def __init__(self, buy_quote, sell_quote, allow_cross=False):
        """
        This is a basic wrapper for a Quote, that has a bid and offer quote.

        :param buy_quote: the quote to buy
        :param sell_quote: the quote to sell
        :param allow_cross: bool. Whether the market can be crossed/locked or not. Optional. Defaults to False (not allowed)
        """
        assert buy_quote is None or isinstance(buy_quote, Quote)
        assert sell_quote is None or isinstance(sell_quote, Quote)
        assert buy_quote is None or buy_quote.side().is_bid(), "If buy quote is not None it's Side must be a bid."
        assert sell_quote is None or sell_quote.side().is_ask(), "If sell quote is not None it's Side must be an ask."
        assert isinstance(allow_cross, bool)

        self._buy_quote = buy_quote
        self._sell_quote = sell_quote
        self._allow_cross = allow_cross
        self._validate_quotes()

    def _validate_quotes(self):
        if self._buy_quote is None or self._sell_quote is None:
            return

        if not self._allow_cross and self._buy_quote.price() >= self._sell_quote.price():
            raise Exception("TwoSidedQuote set to not allow crossed quotes. And bid (%s) >= ask (%s)" %
                            (str(self._buy_quote.price()), str(self._sell_quote.price())))

        if self._sell_quote.market() != self._buy_quote.market():
            raise Exception("In a two sided quote, both quotes must be the same market. Buy %s. Sell %s." %
                            (str(self._buy_quote.market()), str(self._sell_quote.market())))

    def buy_quote(self):
        """
        Gets the buy quote

        :return: Quote. Can be None
        """
        return self._buy_quote

    def sell_quote(self):
        """
        Gets the sell quote

        :return: Quote. Can be None
        """
        return self._sell_quote

    def set_buy_quote(self, buy_quote):
        """
        set the buy quote

        :param buy_quote: Quote
        """
        assert buy_quote is None or isinstance(buy_quote, Quote)
        assert buy_quote is None or buy_quote.side().is_bid(), "If buy quote is not None it's Side must be a bid."
        self._buy_quote = buy_quote
        self._validate_quotes()

    def set_sell_quote(self, sell_quote):
        """
        set the sell quote

        :param sell_quote: Quote
        """
        assert sell_quote is None or isinstance(sell_quote, Quote)
        assert sell_quote is None or sell_quote.side().is_ask(), "If sell quote is not None it's Side must be a ask."
        self._sell_quote = sell_quote
        self._validate_quotes()

    def spread(self):
        """
        get the spread between the buy and sell quotes.

        :return: Decimal. Can be None.
        """
        if self.buy_quote() is None or self.sell_quote() is None:
            return None
        return (self.sell_quote().price().price() - self.buy_quote().price().price()) / self.buy_quote().market().product().mpi()

    def __eq__(self, other):
        return self.buy_quote() == other.buy_quote() and self.sell_quote() == other.sell_quote()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return "Two Sided Quote: Buy %d (%d visible, %d hidden) at %s. Sell %d (%d visible, %d hidden) at %s." % \
               (self.buy_quote().total_qty(),
                self.buy_quote().visible_qty(),
                self.buy_quote().hidden_qty(),
                str(self.buy_quote().price()),
                self.sell_quote().total_qty(),
                self.sell_quote().visible_qty(),
                self.sell_quote().hidden_qty(),
                str(self.sell_quote().price())
                )
