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
from buttonwood.MarketObjects.Events.OrderEvents import FillReport


LAST_TRADE_TYPE = 0
BID_TOB_TYPE = 1
ASK_TOB_TYPE = 2
MID_TYPE = 3

def bid_price(order_book, causing_order_chain):
    price = None
    if order_book is not None:
        price = order_book.best_price(BID_SIDE)
    return price


def ask_price(order_book, causing_order_chain):
    price = None
    if order_book is not None:
        price = order_book.best_price(ASK_SIDE)
    return price


def mid_price(order_book, causing_order_chain):
    price = None
    if order_book is not None:
        best_ask_price = order_book.best_price(ASK_SIDE)
        best_bid_price = order_book.best_price(BID_SIDE)
        if best_ask_price is not None and best_bid_price is not None:
            price = (best_bid_price + best_ask_price) / 2.0
        elif best_ask_price is not None:
            # ask price is not None but bid price is, use ask
            price = best_ask_price
        elif best_bid_price is not None:
            # bid price is not None but ask price is, use bid
            price = best_bid_price
        else:
            # both sides are none so no price
            price = None
    return price


def last_trade(order_book, causing_order_chain):
    price = None
    if isinstance(causing_order_chain.most_recent_event(), FillReport):
        price = causing_order_chain.most_recent_event().fill_price()
    return price


class OHLCPriceTracker(object):

    def __init__(self, start_time, start_price):
        self._start_time = start_time
        self._open = start_price
        self._close = start_price
        self._high = start_price
        self._low = start_price

    def update_price(self, price):
        # price cannot be higher than the high and lower than the low so elif works here
        if price > self._high:
            self._high = price
        elif price < self._low:
            self._low = price
        # always update close price as this might be last price of period
        self._close = price

    def start_time(self):
        return self._start_time

    def open(self):
        return self._open

    def close(self):
        return self._close

    def high(self):
        return self._high

    def low(self):
        return self._low


class ConfigurablePeriodBarListener(OrderLevelBookListener):
    """
    Creates Period Bars.

    Takes period, start time and stop time as arguments.

    Period is number of seconds with fractions of seconds being part of the decimal.

    Start time and stop time are both optional number of seconds since the epoch.

    If start time is None then will use first time we see an update, as long
      as that time is one full period less than the stop time.

    If stop time is None it is considered infinite and will go on as long as there is data.
        
    """

    TYPE_TO_FUNCTION = {LAST_TRADE_TYPE: last_trade,
                        BID_TOB_TYPE: bid_price,
                        ASK_TOB_TYPE: ask_price,
                        MID_TYPE: mid_price}

    # TODO UNIT TEST
    def __init__(self, logger, period, start_time=None, stop_time=None, type = LAST_TRADE_TYPE):
        OrderLevelBookListener.__init__(self, logger)
        assert start_time is None or (stop_time is None or start_time <= stop_time - period), "If start time is None and stop time is not None, then start time must be less than or equal to the stop time minus one period."
        self._start_time = start_time
        self._previous_time = start_time
        self._stop_time = stop_time
        self._period = period
        self._market_to_bars = {}
        self._market_to_volume = {}
        self._market_to_current_tracker = {}
        self._type = type
        self._price_func = self.TYPE_TO_FUNCTION[type]
        self._next_stop_time = start_time + period

    def type(self):
        return self._type

    def notify_book_update(self, order_book, causing_order_chain, tob_updated):
        if tob_updated:
            time = order_book.last_update_time()
            if time >= self._start_time:
                market = order_book.market()
                if market not in self._market_to_bars:
                    self._market_to_bars[market] = []

                # if time is < previous time we have an issue.
                if time < self._previous_time:
                    raise Exception("Book update at %0.6f is before the time of the previous update at %0.6f" % (time, self._previous_time))

                # don't do anything if before start time
                if time < self._start_time:
                    return

                if


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
        # print type(causing_order_chain.most_recent_event())
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
