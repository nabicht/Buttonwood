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
from buttonwood.MarketObjects.EventListeners.OrderEventListener import OrderEventListener
from buttonwood.MarketObjects.Events.OrderEvents import NewOrderCommand, CancelReplaceCommand
from buttonwood.MarketObjects.Events.EventChains import OrderEventChain
from buttonwood.MarketObjects.Side import ASK_SIDE
from buttonwood.MarketObjects.Side import BID_SIDE
from buttonwood.utils.dicts import NDeepDict
import operator


class LastTimeTOBListener(OrderLevelBookListener, OrderEventListener):
    """
    Tracks when prices were top of book so that at any given time we can query
     with a price and side and determine when the last time that price was top
     of book.

    If you use the same price but the other side, you get when the last time the
     price would have crossed the book.

    This is designed so it can work with multiple order books at once.
    """
    # TODO UNIT TEST
    def __init__(self, logger):
        OrderLevelBookListener.__init__(self, logger)
        OrderEventListener.__init__(self, logger)
        self._market_to_side_prev_price = NDeepDict(depth=2, default_value=None)
        self._market_side_price_time = NDeepDict(depth=3, default_value=None)  # market to side to price to last time it was top of book
        self._market_side_best_price = NDeepDict(depth=2, default_value=None)
        self._event_id_to_last_time_crossed = dict()
        self._event_id_to_last_time_tob = dict()

    def _update_based_on_new_event(self, market, time):
        for side in [BID_SIDE, ASK_SIDE]:
            # TODO could also loop over every market if we needed to do so here but that impacts performance for what I think is minimal gain
            prev_best_price = self._market_to_side_prev_price.get((market, side))
            if prev_best_price is not None:
                self._market_side_price_time.set((market, side, prev_best_price), value=time)

    def handle_new_order_command(self, new_order_command, resulting_order_chain):
        assert isinstance(new_order_command, NewOrderCommand)
        event_id = new_order_command.event_id()
        market = new_order_command.market()
        time = new_order_command.timestamp()
        self._update_based_on_new_event(market, time)
        price = new_order_command.price()
        side = new_order_command.side()
        if event_id not in self._event_id_to_last_time_crossed:
            self._event_id_to_last_time_crossed[event_id] = self._last_time_crossed(market, side, price)
        if event_id not in self._event_id_to_last_time_tob:
            self._event_id_to_last_time_tob[event_id] = self._last_time_was_tob(market, side, price)

    def handle_cancel_replace_command(self, cancel_replace_command, resulting_order_chain):
        assert isinstance(cancel_replace_command, CancelReplaceCommand)
        event_id = cancel_replace_command.event_id()
        market = cancel_replace_command.market()
        time = cancel_replace_command.timestamp()
        self._update_based_on_new_event(market, time)
        price = cancel_replace_command.price()
        side = cancel_replace_command.side()
        if event_id not in self._event_id_to_last_time_crossed:
            self._event_id_to_last_time_crossed[event_id] = self._last_time_crossed(market, side, price)
        if event_id not in self._event_id_to_last_time_tob:
            self._event_id_to_last_time_tob[event_id] = self._last_time_was_tob(market, side, price)

    def last_time_was_tob(self, event_id):
        last_time_tob = self._event_id_to_last_time_tob[event_id]
        return last_time_tob

    def last_time_crossed(self, event_id):
        last_time_crossed = self._event_id_to_last_time_crossed[event_id]
        if last_time_crossed is not None:
            del self._event_id_to_last_time_crossed[event_id]
        return last_time_crossed

    def notify_book_update(self, order_book, causing_order_chain, tob_updated):
        """
        Every time an orderbook comes in, look at the top of book price.

        If TOB didn't change at all then just

        If the same as the previous top of book price then we just update that
         price's last TOB time.

        If a new top of book, we need to:
         1) update the previous price to the new time (since it was TOB up to and including this new time)
         2) update the new price to the new time
        """
        time = order_book.last_update_time()
        market = order_book.market()
        # only need to do the side that was updated by the causing order chain as that is only side that changed
        side = causing_order_chain.side()

        best_price = order_book.best_price(side)
        # if current book best price is not none then need to set its time
        if best_price is not None:
            self._market_side_price_time.set((market, side, best_price), value=time)
            prev_best_price = self._market_side_best_price.get((market, side))
            if prev_best_price is None or best_price.better_than(prev_best_price, side):
                self._market_side_best_price.set((market, side), value=best_price)
        # if previous best price is not none and is different than new best price then need to set its time to
        #  update it to include previous price period since it was best price until the change
        prev_best_price = self._market_to_side_prev_price.get((market, side))
        if prev_best_price is not None and prev_best_price != best_price:
            self._market_side_price_time.set((market, side, prev_best_price), value=time)
        # set previous best price to be the current best price
        self._market_to_side_prev_price.set((market, side), value=best_price)

    def _last_time_was_tob(self, market, side, price):
        """
        Returns the last time the price was the top of book
        Will return None if the passed in price has never been top of book for
         market and side during the scope of this listener

        :param market: MarketObjects.Market.Market
        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price
        :return: float. (Could be None)
        """
        return self._market_side_price_time.get((market, side, price))

    def _last_time_crossed(self, market, side, price):
        """
        Returns the last time the price for the given side would have crossed the book.
        
        None if it never would have crossed the book or if there was never a book to cross.
        
        :param market: MarketObjects.Market.Market
        :param side: MarketObjects.Side.Side (side of the order we are checking)
        :param price: MarketObjects.Price.Price (price of the order we are checking)
        :return: float. (Could be None)
        """

        resting_side = side.other_side()
        # if book hasn't been established yet, so return None

        # there are a lot of messages that come in that never would have crossed. so just tracking a "best bid and best
        # offer seen all day" would keep us from doing the below sorting and iterating for these and save a ton of time
        best_resting_price = self._market_side_best_price.get((market, resting_side))
        if best_resting_price is None or price.worse_than(best_resting_price, side):
            return None
        else:

            resting_prices_to_time = self._market_side_price_time.get((market, resting_side))

            # sort list based on time, where most recent time (highest number) is first
            sorted_x = sorted(resting_prices_to_time.items(), key=operator.itemgetter(1), reverse=True)
            for x in sorted_x:
                if price.better_or_same_as(x[0], side):
                    return x[1]
        self._logger.error("last_time_crossed has a price that would have crossed today but still has no cross time value. Something is broken!")
        # failsafe return?
        return None

    def clean_up(self, order_chain):
        # if order chain events in map, clean up
        assert isinstance(order_chain, OrderEventChain)
        events = order_chain.events()
        for event in events:
            try:
                del self._event_id_to_last_time_crossed[event.event_id()]
            except:
                pass  # silent fail is okay here. All I'm doing is deleting if it exists in dict. If it doesn't exist no need to delete so failure state is acceptable and faster than checking for existence first.
            try:
                del self._event_id_to_last_time_tob[event.event_id()]
            except:
                pass  # silent fail is okay here. All I'm doing is deleting if it exists in dict. If it doesn't exist no need to delete so failure state is acceptable and faster than checking for existence first.