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

from buttonwood.MarketObjects.OrderBookListeners.OrderLevelBookListener import OrderLevelBookListener
from buttonwood.MarketObjects.Events.OrderEvents import AcknowledgementReport
from buttonwood.MarketObjects.Side import BID_SIDE
from buttonwood.MarketObjects.Side import ASK_SIDE
import sys

class CrossedBookListener(OrderLevelBookListener):
    """
    Just looks for crossed books and logs when they happen.
    
    Eventually might want to do something like track how long a crossed book lasts.
    """
    def __init__(self, logger):
        OrderLevelBookListener.__init__(self, logger)

    def notify_book_update(self, order_book, causing_order_chain, tob_updated):
        """
        only time it makes sense to look for crossed books is after an ack, so only doing that.

        we care about more than just TOB updated scenarios because of the possibility of multiple levels crossing and
          this is a rather unsophisticated listener.
        """
        if isinstance(causing_order_chain.most_recent_event(), AcknowledgementReport):
            best_bid_price = order_book.best_bid_price()
            best_ask_price = order_book.best_ask_price()
            if best_bid_price is None or best_ask_price is None:
                return
            if best_bid_price.better_or_same_as(best_ask_price, BID_SIDE):
                firms = set()
                bid_chains = order_book.iter_order_chains_at_price(BID_SIDE, best_bid_price)
                ask_chains = order_book.iter_order_chains_at_price(ASK_SIDE, best_ask_price)
                for chain in bid_chains:
                    firms.add(chain.user_id().split(".")[0])
                for chain in ask_chains:
                    firms.add(chain.user_id().split(".")[0])
                if len(firms) > 1:
                    self._logger.warn("%s is crossed! Bid %s >= Ask %s" %
                                      (str(order_book.market()), str(order_book.best_bid_price()),
                                       str(order_book.best_ask_price())))
