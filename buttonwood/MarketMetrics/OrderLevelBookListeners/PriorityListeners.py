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
from buttonwood.MarketObjects.Events.OrderEvents import CancelReplaceCommand
from buttonwood.MarketObjects.OrderBooks.OrderLevelOrderBookQueries import modified_qty_at_price
from buttonwood.utils.dicts import NDeepDict


class Priority:
    def __init__(self, ticks_from_tob, ticks_from_opposite_tob, size_ahead_at_price):
        self._ticks_from_tob = ticks_from_tob
        self._ticks_from_opposite_tob = ticks_from_opposite_tob
        self._size_ahead_at_price = size_ahead_at_price

    def ticks_from_tob(self):
        return self._ticks_from_tob

    def ticks_from_opposite_tob(self):
        return self._ticks_from_opposite_tob

    def size_ahead_at_price(self):
        return self._size_ahead_at_price

    def better_priority_than(self, other_priority):
        """
        Returns true if this priority is better than the one passed in.

        Priority is decided by next to get filled so less ticks from TOB or same
         ticks from TOB but less size ahead is better priority.

        :param other_priority: MarketMetrics.OrderLevelBookListeners.PriorityListeners.Priority
        :return: Bool
        """
        assert isinstance(other_priority,
                          Priority), "other_priority must be instance of MarketMetrics.OrderLevelBookListeners.PriorityListeners.Priority"
        return (self.ticks_from_tob() < other_priority.ticks_from_tob()) or \
               (
               self.ticks_from_tob() == other_priority.ticks_from_tob() and self.size_ahead_at_price() < other_priority.size_ahead_at_price())

    def worse_priority_than(self, other_priority):
        """
        Returns true if this priority is worse than the one passed in.

        Priority is decided by next to get filled so more ticks from TOB or same
        ticks from TOB but more size ahead is worse priority.

        :param other_priority: MarketMetrics.OrderLevelBookListeners.PriorityListeners.Priority
        :return: Bool
        """
        assert isinstance(other_priority,
                          Priority), "other_priority must be instance of MarketMetrics.OrderLevelBookListeners.PriorityListeners.Priority"
        return (self.ticks_from_tob() > other_priority.ticks_from_tob()) or \
               (
               self.ticks_from_tob() == other_priority.ticks_from_tob() and self.size_ahead_at_price() > other_priority.size_ahead_at_price())

    def further_from_opposite_tob(self, other_priority):
        """
        Returns true if this priority is further from opposite side tob than
         the one passed in.

        :param other_priority: MarketMetrics.OrderLevelBookListeners.PriorityListeners.Priority
        :return: Bool
        """
        assert isinstance(other_priority,
                          Priority), "other_priority must be instance of MarketMetrics.OrderLevelBookListeners.PriorityListeners.Priority"
        return (self.ticks_from_opposite_tob() > other_priority.ticks_from_opposite_tob()) or \
               (
               self.ticks_from_opposite_tob() == other_priority.ticks_from_opposite_tob() and self.size_ahead_at_price() > other_priority.size_ahead_at_price())

    def closer_to_opposite_tob(self, other_priority):
        """
        Returns true if this priority is further from opposite side tob than
         the one passed in.

        :param other_priority: MarketMetrics.OrderLevelBookListeners.PriorityListeners.Priority
        :return: Bool
        """
        assert isinstance(other_priority,
                          Priority), "other_priority must be instance of MarketMetrics.OrderLevelBookListeners.PriorityListeners.Priority"
        return (self.ticks_from_opposite_tob() < other_priority.ticks_from_opposite_tob()) or \
               (
               self.ticks_from_opposite_tob() == other_priority.ticks_from_opposite_tob() and self.size_ahead_at_price() < other_priority.size_ahead_at_price())


class EventPriorityListener(OrderLevelBookListener, OrderEventListener):
    """

    priority from event on commands can be considered intended priority

    priority from event on execution reports can be considered achieved priority

    priority at command is what the priority was before the event .

    Designed to work with the order books of multiple markets.
    """

    # TODO UNIT TEST!
    def __init__(self, logger, handle_market_orders=False):
        OrderLevelBookListener.__init__(self, logger)
        OrderEventListener.__init__(self, logger)
        self._market_to_order_book = {}
        self._market_to_event_to_priority = NDeepDict(depth=2)
        self._market_to_event_to_priority_before = NDeepDict(depth=2, default_value=None)
        self._handle_market_orders = handle_market_orders

    def _calculate_priority_not_in_book(self, price, side, market, ignore_order_ids=set()):
        """
        Calculate the priority when not reflected in the book yet.

        :param price: MarketObjects.Price.Price
        :param side: MarketObjects.Side.Side
        :param market: MarketObjects.Market.Market
        :return: PriorityListeners.Priority
        """
        # if the order book is None then the orderbook hasn't been established
        #  and we can assume that ack is best priority for its side and there is
        #  other side.
        order_book = self._market_to_order_book.get(market)
        if order_book is None:
            return Priority(0, None, 0)
        else:  # if order book is not None then we need to figure out what priority would be
            # calculate distance from opposite side since needed in both
            opposite_best_price = order_book.best_price(side.other_side())
            ticks_from_opposite_tob = None
            if opposite_best_price is not None:  # if it is None then ticks from opposite is None
                ticks_from_opposite_tob = price.ticks_behind(opposite_best_price, side, market.product())

            #best_price = order_book.best_price(side)
            best_price = self._best_price(order_book, side, ignore_order_ids)
            # if the best price is None then it is best priority and only need distance from opposite side of book
            if best_price is None:
                return Priority(0, ticks_from_opposite_tob, 0)
            else:  # if best price is not None then we need to calculate
                ticks_from_tob = price.ticks_behind(best_price, side, market.product())
                # assuming visible qty gets priority over hidden so only want visible qty for qty ahead
                if len(ignore_order_ids) == 0:
                    qty_ahead = order_book.visible_qty_at_price(side, price)
                else:
                    qty_ahead = modified_qty_at_price(order_book, side, price, ignore_order_ids=ignore_order_ids,
                                                  ignore_hidden=True)
                return Priority(ticks_from_tob, ticks_from_opposite_tob, qty_ahead)

    def _best_price(self, order_book, side, order_chain_ids):
        prices = order_book.prices(side)
        best_price = None
        for price in prices:
            for order_chain in order_book.iter_order_chains_at_price(side, price):
                if order_chain.chain_id() not in order_chain_ids:
                    best_price = price
                    break
            if best_price is not None:
                break
        return best_price

    def _calculate_priority_in_book(self, order_chain):
        """
        Calculate the priority when is in the book already.

        :param order_chain: MarketObjects.Events.EventChains.OrderEventChain
        :return: PriorityListeners.Priority
        """
        market = order_chain.market()
        side = order_chain.side()
        price = order_chain.current_price() if order_chain.is_open() else order_chain.price_at_close()
        order_book = self._market_to_order_book.get(market)
        if order_book is None:
            return Priority(0, None, 0)
        else:  # if order book is not None then we need to figure out what priority would be
            # calculate distance from opposite side since needed in both
            opposite_best_price = order_book.best_price(side.other_side())
            ticks_from_opposite_tob = None
            if opposite_best_price is not None:  # if it is None then ticks from opposite is None
                ticks_from_opposite_tob = price.ticks_behind(opposite_best_price, side, market.product())

            # in getting best price, ignore the same order chain so it doesn't factor in with cancel-replace back off of top of book.
            best_price = order_book.best_price(side)
            # if the best price is None then it is best priority and only need distance from opposite side of book
            if best_price is None:
                return Priority(0, ticks_from_opposite_tob, 0)
            else:  # if best price is not None then we need to calculate
                ticks_from_tob = price.ticks_behind(best_price, side, market.product())
                # assuming visible qty gets priority over hidden so only want visible qty for qty ahead
                qty_ahead = 0
                for chain in order_book.iter_order_chains_at_price(side, price):
                    if chain.chain_id() == order_chain.chain_id():
                        break
                    qty_ahead += chain.visible_qty()
                return Priority(ticks_from_tob, ticks_from_opposite_tob, qty_ahead)

    def handle_new_order_command(self, new_order_command, resulting_order_chain):
        if new_order_command.is_market_order() and not self._handle_market_orders:
            self._logger.debug("%s set to ignore market orders. New Order %s is a market order. Ignoring" %
                               (self.__class__.__name__, str(new_order_command.event_id())))
            return
        event_id = new_order_command.event_id()
        price = new_order_command.price()
        side = resulting_order_chain.side()
        market = new_order_command.market()
        if market not in self._market_to_order_book:
            return
        # new orders are not in the book so calculate what priority *would be*
        priority = self._calculate_priority_not_in_book(price, side, market)
        self._market_to_event_to_priority.set((market, event_id), value=priority)
        # No need to set priority before event on new orders

    def handle_cancel_replace_command(self, cancel_replace_command, resulting_order_chain):
        event_id = cancel_replace_command.event_id()
        price = cancel_replace_command.price()
        side = resulting_order_chain.side()
        market = resulting_order_chain.market()
        if market not in self._market_to_order_book:
            return
        # need the most recently requested exposure, if none, get the ack'd exposure
        exposure = resulting_order_chain.most_recent_requested_exposure()
        if exposure is None:
            exposure = resulting_order_chain.current_exposure()

        before_event_priority = self._calculate_priority_in_book(resulting_order_chain)
        self._market_to_event_to_priority_before.set((market, event_id), value=before_event_priority)

        # cancel_replace_same_priority is True if cancel replace down and same price
        cancel_replace_same_priority = (price == exposure.price() and exposure.qty() > cancel_replace_command.qty())

        # cancel replaces have priority at time of event, because order already in book
        if cancel_replace_same_priority:
            priority = before_event_priority
        else:  # otherwise, have to calculate what priority *would be*
            # ignore itself so that we do include it as in front of itself on cancel replace up in size
            priority = self._calculate_priority_not_in_book(price, side, market,
                                                            ignore_order_ids={cancel_replace_command.chain_id()})
        self._market_to_event_to_priority.set((market, event_id), value=priority)

    def handle_cancel_command(self, cancel_command, resulting_order_chain):
        """
        at time fo a cancel, the order should be in the book so just go ahead and calculate priority in book.
        """
        event_id = cancel_command.event_id()
        market = resulting_order_chain.market()
        if market not in self._market_to_order_book:
            return
        priority = self._calculate_priority_in_book(resulting_order_chain)
        self._market_to_event_to_priority.set((market, event_id), value=priority)
        # priority before the event is the same calculated aftet event for cancel command
        self._market_to_event_to_priority_before.set((market, event_id), value=priority)

    def handle_acknowledgement_report(self, acknowledgement_report, resulting_order_chain):
        event_id = acknowledgement_report.event_id()
        market = resulting_order_chain.market()
        # don't do anything! orderbook not known
        if market not in self._market_to_order_book:
            return
        # acks are in the book already and no need to do anything fancy with ignoring orders
        priority = self._calculate_priority_in_book(resulting_order_chain)
        self._market_to_event_to_priority.set((market, event_id), value=priority)

        # if acking a new order no priority before, so use default of None.
        #  Calculate for cancel replace with current priority since hasn't been applied to book yet
        if isinstance(acknowledgement_report.causing_command(), CancelReplaceCommand):
            self._market_to_event_to_priority_before.set((market, event_id), value=priority)


    def _priority_at_fill(self, fill_event, resulting_order_chain):
        """
        A fill we can assume priority at fill was best.

        Still need to calculate the ticks from opposite side though.
        """
        market = fill_event.market()
        event_id = fill_event.event_id()
        order_book = self._market_to_order_book.get(market)
        # don't do anything! orderbook not known
        if order_book is None:
            return
        # do closes
        opposite_best_price = order_book.best_price(resulting_order_chain.side().other_side())
        ticks_from_opposite_tob = None
        if opposite_best_price is not None:  # if it is None then ticks from opposite is None
            ticks_from_opposite_tob = abs((opposite_best_price - fill_event.fill_price()) / market.product().mpi())
        priority = Priority(0, ticks_from_opposite_tob, 0)
        self._market_to_event_to_priority.set((market, event_id), value=priority)

        #for a fill, priority before fill is always 0
        self._market_to_event_to_priority_before.set((market, event_id), value=priority)

    def handle_partial_fill_report(self, partial_fill_report, resulting_order_chain):
        self._priority_at_fill(partial_fill_report, resulting_order_chain)

    def handle_full_fill_report(self, full_fill_report, resulting_order_chain):
        self._priority_at_fill(full_fill_report, resulting_order_chain)

    def handle_cancel_report(self, cancel_report, resulting_order_chain):
        """
        When an order is cancelled we want to calculate what its priority was at
         time of cancel. Since the cancel hasn't impacted the order book yet,
         can find the order chain in the order book and calculate the priority.
        """
        # we really only care if a limit and FAR order because otherwise, it wouldn't have any priority since never in book.
        #  and if it has no ack then it was cancelled for self trade purposes (or some such thing) so no impact on book
        if not (resulting_order_chain.is_far() and resulting_order_chain.is_limit_order() and resulting_order_chain.has_acknowledgement()):
            return
        market = resulting_order_chain.market()
        if market not in self._market_to_order_book:
            return
        event_id = cancel_report.event_id()
        priority = self._calculate_priority_in_book(resulting_order_chain)
        self._market_to_event_to_priority.set((market, event_id), value=priority)
        self._market_to_event_to_priority_before.set((market, event_id), value=priority)

    def notify_book_update(self, order_book, causing_order_chain, tob_updated):
        """
        All that needs to be done here is save off the most order_book to be used
         when an event listener call back needs it.
        """
        self._market_to_order_book[order_book.market()] = order_book

    def event_priority(self, market, event_id):
        """
        Get's the priority of the event. If the event was not tracked (/doesn't exist) then will return None.
        
        :param market: MarketObjects.Market.Market
        :param event_id: unique identifier of event
        :return: MarketMetrics.OrderLevelBookListeners.PriorityListeners.Priority
        """
        return self._market_to_event_to_priority.get((market, event_id))

    def priority_before_event(self, market, event_id):
        """
        Gets the priority of the event's order chain right before the event occurred. If the event was not 
         tracked (/doesn't exist) then will return None.
        
        :param market: MarketObjects.Market.Market
        :param event_id: unique identifier of event
        :return: MarketMetrics.OrderLevelBookListeners.PriorityListeners.Priority
        """
        return self._market_to_event_to_priority_before.get((market, event_id))

    def clean_up(self, order_chain):
        """
        If clean_up is called with an order_chain than this will go through the
         order chain's events and remove them from tracking

        WARNING: once this is called, the event_priority no longer return the values that are
         meaningful; rather, you'll get None.

        :param order_chain: MarketObjects.Events.EventChains.OrderEventChain
        """
        market = order_chain.market()
        events = order_chain.events()
        for event in events:
            self._market_to_event_to_priority.delete((market, event.event_id()))
            if event.event_id() in self._market_to_event_to_priority_before.get([market]):
                self._market_to_event_to_priority_before.delete((market, event.event_id()))
