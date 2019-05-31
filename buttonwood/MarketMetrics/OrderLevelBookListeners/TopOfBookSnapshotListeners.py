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
from buttonwood.MarketObjects.Side import BID_SIDE
from buttonwood.MarketObjects.Side import ASK_SIDE


class TopOfBookBeforeEventListener(OrderLevelBookListener):
    """
    Tracks top of book before an event for the market the event occurred in. Keeps track in dict of 
      event_id -> (PriceLevel, PriceLevel), where the first PriceLevel is the bid and second is the ask
        
    """

    # TODO UNIT TEST
    def __init__(self, logger):
        OrderLevelBookListener.__init__(self, logger)
        self._event_id_to_tob = {}
        self._market_to_previous_tob = {}

    def notify_book_update(self, order_book, causing_order_chain, tob_updated):
        # set the event to the previous tob
        market = order_book.market()
        tob = self._market_to_previous_tob.get(market)
        event_id = causing_order_chain.most_recent_event().event_id()
        self._event_id_to_tob[event_id] = tob
        # set the previous tob to the new tob (but only do it if TOB changed
        if tob_updated:
            self._market_to_previous_tob[market] = (order_book.best_level(BID_SIDE), order_book.best_level(ASK_SIDE))

    def clean_up_order_chain(self, order_chain):
        for event in order_chain.events():
            del self._event_id_to_tob[event.event_id()]

    def tob_before_event(self, event_id):
        """
        Gets the top of book snapshots as a tuple (bid side PriceLevel, ask side PriceLevel) for the given event_id.
        
        Can be None for either side if the side does not exist in the order book before the event_id.
        
        Can be None instead of a tuple if the event_id is not known.
        
        :param event_id: unique identifier of the event 
        :return: (Buttonwood.MarketObjects.PriceLevel.PriceLevel, Buttonwood.MarketObjects.PriceLevel.PriceLevel)
        """
        return self._event_id_to_tob.get(event_id)


class TopOfBookAfterEventListener(OrderLevelBookListener):
    """
    Tracks top of book after an event for the market the event occurred in. Keeps track in dict of 
      event_id -> (PriceLevel, PriceLevel), where the first PriceLevel is the bid and second is the ask

      if event does not impact the book it doesn't end up getting tracked.
    """

    # TODO UNIT TEST
    def __init__(self, logger):
        OrderLevelBookListener.__init__(self, logger)
        self._event_id_to_tob = {}

    def notify_book_update(self, order_book, causing_order_chain, tob_updated):
        event_id = causing_order_chain.most_recent_event().event_id()
        self._event_id_to_tob[event_id] = (order_book.best_level(BID_SIDE), order_book.best_level(ASK_SIDE))

    def clean_up_order_chain(self, order_chain):
        for event in order_chain.events():
            # not all events cause notify_book_update to be called
            if event.event_id() in self._event_id_to_tob:
                del self._event_id_to_tob[event.event_id()]

    def tob_after_event(self, event_id):
        """
        Gets the top of book snapshots as a tuple (bid side PriceLevel, ask side PriceLevel) for the given event_id.

        Can be None for either side if the side does not exist in the order book after the event_id.

        Can be None instead of a tuple if the event_id is not known.

        :param event_id: unique identifier of the event 
        :return: (Buttonwood.MarketObjects.PriceLevel.PriceLevel, Buttonwood.MarketObjects.PriceLevel.PriceLevel)
        """
        return self._event_id_to_tob.get(event_id)
