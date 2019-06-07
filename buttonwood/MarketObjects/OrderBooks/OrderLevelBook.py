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

from collections import OrderedDict
from buttonwood.MarketObjects.EventListeners.OrderEventListener import OrderEventListener
from buttonwood.MarketObjects.Events import OrderEventConstants as TIF
from buttonwood.MarketObjects.Events.OrderEvents import NewOrderCommand
from buttonwood.MarketObjects.Market import Market
from buttonwood.MarketObjects.OrderBooks.BasicOrderBook import BasicOrderBook
from buttonwood.MarketObjects.PriceLevel import PriceLevel
from buttonwood.MarketObjects.Side import BID_SIDE
from buttonwood.MarketObjects.Side import ASK_SIDE
from buttonwood.MarketObjects.OrderBookListeners.OrderLevelBookListener import OrderLevelBookListener


class TimePriorityOrderLevel(object):
    # TODO document
    # TODO unit test
    def __init__(self, logger):
        self._order_chains = OrderedDict()
        self._logger = logger
        self._dirty = False
        self._visible_qty = 0
        self._hidden_qty = 0
        self._num_orders = 0

    def order_chains(self):
        return self._order_chains.values()

    def iter_order_chains(self):
        return self._order_chains.itervalues()

    def first(self):
        if self.is_empty():
            self._logger.warning("%s: first() called on TimePriorityOrderLevel empty level." % self.__class__.__name__)
            return None
        return self.order_chains()[0]

    def is_empty(self):
        return True if len(self.order_chains()) == 0 else False

    def has_order_chain(self, chain_id):
        return chain_id in self._order_chains

    def add_to_level(self, order_chain):
        """
        will not add if already there; rather will log error and return
        """
        if self.has_order_chain(order_chain.chain_id()):
            self._logger.error("%s: Cannot add %s to %s. Already exists at price." %
                               (self.__class__.__name__,
                                str(order_chain.chain_id()),
                                str(order_chain.current_exposure().price())))
        else:
            self._order_chains[order_chain.chain_id()] = order_chain
            # self._dirty = True
            self._visible_qty += order_chain.visible_qty()
            self._hidden_qty += order_chain.hidden_qty()
            self._num_orders += 1
            self._logger.debug("%s: Added %s to %s." %
                               (self.__class__.__name__,
                                str(order_chain.chain_id()),
                                str(order_chain.current_exposure().price())))

    def remove_from_level(self, order_chain):
        if not self.has_order_chain(order_chain.chain_id()):
            self._logger.error("%s: Cannot remove %s from %s. Does not exist at price." %
                               (self.__class__.__name__,
                                str(order_chain.chain_id()),
                                str(order_chain.current_exposure().price())))
        else:
            del self._order_chains[order_chain.chain_id()]
            # removes not as easy as adds because if orderchain is already closed visible and hidden quantities are 0.
            #  so can't just subtract out out the chain's quantities in order to maintain level sizes
            self._dirty = True
            self._logger.debug("%s: Removed %s from %s." %
                               (self.__class__.__name__,
                                str(order_chain.chain_id()),
                                str(order_chain.current_exposure().price())))

    def force_dirty(self):
        # this function needs to exist because if there is a cancel replace down in qty or a partial fill this class
        #  will never know, so whatever calls add_to_level and remove_from_level needs to be responsible for forcing
        #  the dirty flag to true
        self._dirty = True

    def _set_level_quantities(self):
        visible_qty = 0
        hidden_qty = 0
        num_orders = 0
        for order_chain in self._order_chains.itervalues():
            visible_qty += order_chain.visible_qty()
            hidden_qty += order_chain.hidden_qty()
            num_orders += 1
        self._num_orders = num_orders
        self._visible_qty = visible_qty
        self._hidden_qty = hidden_qty
        self._dirty = False

    def visible_qty(self):
        if self._dirty:
            self._set_level_quantities()
        return self._visible_qty

    def hidden_qty(self):
        if self._dirty:
            self._set_level_quantities()
        return self._hidden_qty

    def total_qty(self):
        if self._dirty:
            self._set_level_quantities()
        return self._hidden_qty + self._visible_qty

    def num_orders(self):
        if self._dirty:
            self._set_level_quantities()
        return self._num_orders

    def __len__(self):
        return len(self._order_chains)

    def __str__(self):
        return str(self._order_chains)


class SideDict(dict):
    # TODO unit test!

    def __init__(self, *args, **kw):
        super(SideDict, self).__init__(*args, **kw)
        self._max_key = None
        self._min_key = None
        self._sort_dirty = False
        self._sorted = []

    def __setitem__(self, key, value):
        if key not in self:
            self._sort_dirty = True
            # only have to worry about setting max and min if a new key
            if self._max_key is None or key > self._max_key:
                self._max_key = key
            if self._min_key is None or key < self._min_key:
                self._min_key = key
        super(SideDict, self).__setitem__(key, value)

    def __delitem__(self, key):
        super(SideDict, self).__delitem__(key)
        # no matter what delete makes dirty because removing a price that is currently in cached list
        self._sort_dirty = True
        if len(self) == 0:
            self._max_key = None
            self._min_key = None
        else:
            if key == self._max_key:
                self._max_key = max(self)
            elif key == self._min_key:
                self._min_key = min(self)

    def max_price(self):
        return self._max_key

    def min_price(self):
        return self._min_key

    def sorted_prices(self, reverse=False):
        if self._sort_dirty:
            self._sorted = sorted(self)
            self._sort_dirty = False
        if reverse:
            return sorted(self._sorted, reverse=True)
        else:
            return self._sorted


class OrderLevelBook(BasicOrderBook, OrderEventListener):
    # TODO document class
    # TODO unit test

    def __init__(self, market, logger, name=None):
        BasicOrderBook.__init__(self, market, logger)
        OrderEventListener.__init__(self, logger)
        self._listeners = OrderedDict()
        self._bid_price_to_level = SideDict()
        self._ask_price_to_level = SideDict()
        self._last_update_time = None
        self._name = "OrderLevelOrderBook" if name is None else name

    def name(self):
        """
        Returns the name of the OrderLevelBook instance.
        
        :return: str 
        """
        return self._name

    def last_update_time(self):
        """
        Gets the last time, as a second timestamp (seconds.milli/microseconds) that the order book last updated.
        
        :return: float 
        """

        return self._last_update_time

    def add_order_level_book_listener(self, listener_id, order_level_book_listener):
        """
        Adds a an OrderLevelOrderBook listener that gets notified each time the order book changes
         A listener is identified by its listener_id so that it can be retrieved later if need be.

        As a warning, a listener can be added more than once if a diferent ID is used so
         this can lead to issues if not careful.


        :param listener_id: str
        :param order_level_book_listener: MarketObjects.OrderBookListeners.OrderLevelBookListener.OrderLevelBookListener
        """
        assert isinstance(listener_id, str)
        assert isinstance(order_level_book_listener, OrderLevelBookListener)

        if listener_id in self._listeners:
            raise Exception("%s is already registered" % listener_id)

        self._listeners[listener_id] = order_level_book_listener
        self._logger.info("%s %s registered listener: %s" %
                          (self.name(), str(self._market), order_level_book_listener.__class__.__name__))

    def order_level_book_listener(self, listener_id):
        """
        Get the OrderLevelBookListener that is assoicated with the passed in
         listener identifier. If there isn't then None is returned.

        :param listener_id: str
        :return: MarketObjects.OrderBookListeners.OrderLevelBookListener.OrderLevelBookListener. Can be None
        """
        return self._listeners.get(listener_id)

    def _notify_listeners(self, order_chain, tob_updated):
        for listener in self._listeners.itervalues():
            listener.notify_book_update(self, order_chain, tob_updated)

    def best_priority_chain(self, side):
        """
        Get the best priority live chain for the given side of the book.

        :return: MarketObjects.Events.EventChains.OrderEventChain
        """
        best_price = self.best_price(side)
        if best_price is not None:
            return (self._bid_price_to_level if side.is_bid() else self._ask_price_to_level)[best_price].first()
        return None

    def prices(self, side):
        """
        All the prices on the given side that are currently live in the order
         book, from best price to worse. For the bids, that is highest to
         lowest; for the asks, that is lowest to highest.

        :param side: MarketObjects.Side.Side
        :return: list of MarketObjects.Price.Price
        """
        if side.is_bid():
            return self._bid_price_to_level.sorted_prices(reverse=True)
        else:
            return self._ask_price_to_level.sorted_prices()

    def best_price(self, side):
        """
        Returns the best price of the of the book (top of book price) for the specified side.
        Will return None if the side is empty

        :return: Price. the top of book price for the passed in side. None if side is empty
        """
        return self._bid_price_to_level.max_price() if side.is_bid() else self._ask_price_to_level.min_price()

    def best_level(self, side):
        """
        Gets the best PriceLevel for the given side. Can be None if side is empty.

        :return: MarketObjects.PriceLevel.PriceLevel
        """
        price = self.best_price(side)
        if price is None:
            return None
        return self.level_at_price(side, price)

    def visible_qty_at_price(self, side, price):
        """
        Gets the visible quantity for the price on the specified side of the
         market. If there are no orders at that price on that side, then will
         return 0.

        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price
        :return: int
        """
        level = (self._bid_price_to_level if side.is_bid() else self._ask_price_to_level).get(price)
        return 0 if level is None else level.visible_qty()

    def hidden_qty_at_price(self, side, price):
        """
        Gets the hidden quantity for the price on the specified side of the
         market. If there are no orders at that price on that side, then will
         return 0.

        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price
        :return: int
        """
        level = (self._bid_price_to_level if side.is_bid() else self._ask_price_to_level).get(price)
        return 0 if level is None else level.hidden_qty()

    def num_orders_at_price(self, side, price):
        """
        Get the number of orders at price for a given side. If price the price is
         empty for that side, return 0.

        If include_hidden_orders is True then it will include orders that are
         hidden size only, otherwise those will not be included. This is an
         optional argument that defaults False.

        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Priceorder_book_output
        :return: int
        """
        level = (self._bid_price_to_level if side.is_bid() else self._ask_price_to_level).get(price)
        return 0 if level is None else level.num_orders()

    def order_chains_at_price(self, side, price):
        """
        Gets the order chains at given price and side, in the order of their current priority, where the first order 
         chain is first in line to be matched by the next aggressive fill and the last would only get a match if all 
         the others' visible qty was fully filled.
         
        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price 
        :return: list of MarketObjects.Events.EventChains.OrderEventChain
        """
        level = (self._bid_price_to_level if side.is_bid() else self._ask_price_to_level).get(price)
        return [] if level is None else level.order_chains()

    def iter_order_chains_at_price(self, side, price):
        """
        Gets the iterable of order chains at given price and side, in the order of their current priority, where the 
         first order chain is first in line to be matched by the next aggressive fill and the last would only get a 
         match if all the others' visible qty was fully filled.
         
        This is similar to order_chains_at_price(self, side, price) but it returns the iterable rather than a list, 
         which is a much more efficient way to work with order event chains if you are just walking across them.
         
        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price 
        :return: list of MarketObjects.Events.EventChains.OrderEventChain
        """
        level = (self._bid_price_to_level if side.is_bid() else self._ask_price_to_level).get(price)
        return [] if level is None else level.iter_order_chains()

    def level_at_price(self, side, price):
        """
        Gets the PriceLevel at a price for a given side. Returns None if the
         price does not exist on that Side.

        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price
        :return: MarketObjects.PriceLevel.PriceLevel. Can be None
        """
        level = (self._bid_price_to_level if side.is_bid() else self._ask_price_to_level).get(price)
        if level is None:
            return None
        return PriceLevel(price,
                          self.visible_qty_at_price(side, price),
                          self.hidden_qty_at_price(side, price),
                          self.num_orders_at_price(side, price))

    def to_json(self):
        ob_json = {}
        for side in [BID_SIDE, ASK_SIDE]:
            side_dict = {}
            for level, price in enumerate(self.prices(side)):
                level = self.level_at_price(side, price)
                chain_ids = []
                for chain in self.order_chains_at_price(side, price):
                    chain_ids.append(chain.chain_id())
                side_dict[level] = {"price": price,
                                    "visible_qty": level.visible_qty(),
                                    "hidden_qty": level.hidden_qty(),
                                    "chains": chain_ids}
            ob_json[str(side)] = side_dict
        return {"order_book_type": self.name(), "market": self.market().to_json(), "order_book": ob_json}

    """
    ORDER BOOK MANIPULATION

    Remember that changes to an order chain aren't live in an order book until
     the  execution report. For example, a new order doesn't show up in the
     order book until the acknowledgement.
    """

    def handle_acknowledgement_report(self, acknowledgement_report, resulting_order_chain):
        # if orderchain is NOT a FAR then don't do anything
        self._last_update_time = acknowledgement_report.timestamp()
        order_book_updated = False
        tob_updated = False
        if resulting_order_chain.time_in_force() != TIF.FAR:
            self._logger.error("%s: OrderChain %s Ack %s is a %s, not a FAR. Cannot apply to order book" %
                               (self.name(),
                                str(acknowledgement_report.chain_id()),
                                str(acknowledgement_report.event_id()),
                                TIF.time_in_force_str(resulting_order_chain.time_in_force())))
            return order_book_updated, tob_updated
        is_bid = resulting_order_chain.side().is_bid()
        price_to_level = self._bid_price_to_level if is_bid else self._ask_price_to_level
        # if a new order then just add it
        if isinstance(acknowledgement_report.acknowledged_command(), NewOrderCommand):
            pre_add_best_price = price_to_level.max_price() if is_bid else price_to_level.min_price()
            if acknowledgement_report.price() not in price_to_level:
                price_to_level[acknowledgement_report.price()] = TimePriorityOrderLevel(self._logger)
            price_to_level[acknowledgement_report.price()].add_to_level(resulting_order_chain)
            if is_bid:
                if pre_add_best_price is None or acknowledgement_report.price() >= pre_add_best_price:
                    tob_updated = True
            else:
                if pre_add_best_price is None or acknowledgement_report.price() <= pre_add_best_price:
                    tob_updated = True
            order_book_updated = True
        else:  # otherwise cancel replace and we need to be more careful
            cr_hist = resulting_order_chain.cancel_replace_information(acknowledgement_report.event_id())
            price = acknowledgement_report.price()
            pre_cr_best_price = price_to_level.max_price() if is_bid else price_to_level.min_price()
            if cr_hist is None:
                self._logger.error(
                    "%s: OrderChain %s Cannot apply ack of cancel replace %s. No cancel replace history." %
                    (self.name(),
                     str(acknowledgement_report.chain_id()),
                     str(acknowledgement_report.event_id())))
            elif cr_hist.is_price_change():
                # on price changes remove from old price and apply to new price.
                prev_exposure_price = cr_hist.previous_exposure().price()
                new_exposure_price = cr_hist.new_exposure().price()
                self._logger.debug("%s: OrderChain %s Cancel Replace Ack %s. From %s to %s." %
                                   (self.name(),
                                    str(acknowledgement_report.chain_id()),
                                    str(acknowledgement_report.event_id()),
                                    str(prev_exposure_price),
                                    str(new_exposure_price)))
                price_to_level[prev_exposure_price].remove_from_level(resulting_order_chain)
                if prev_exposure_price == pre_cr_best_price:
                    tob_updated = True
                if len(price_to_level[prev_exposure_price]) == 0:
                    del price_to_level[prev_exposure_price]
                if new_exposure_price not in price_to_level:
                    price_to_level[new_exposure_price] = TimePriorityOrderLevel(self._logger)
                price_to_level[new_exposure_price].add_to_level(resulting_order_chain)
                if is_bid:
                    if new_exposure_price >= pre_cr_best_price:
                        tob_updated = True
                else:
                    if new_exposure_price <= pre_cr_best_price:
                        tob_updated = True
                order_book_updated = True
            elif cr_hist.is_qty_increase():
                # increased qty means move the back of the line, so remove from the price and then add back to the price
                self._logger.debug("%s: OrderChain %s Cancel Replace Ack %s. Qty increased from %d to %d at %s." %
                                   (self.name(),
                                    str(acknowledgement_report.chain_id()),
                                    str(acknowledgement_report.event_id()),
                                    cr_hist.previous_exposure().qty(),
                                    cr_hist.new_exposure().qty(),
                                    str(price)))
                price_to_level[price].remove_from_level(resulting_order_chain)
                if price not in price_to_level:
                    price_to_level[price] = TimePriorityOrderLevel(self._logger)
                price_to_level[price].add_to_level(resulting_order_chain)
                if price == pre_cr_best_price:
                    tob_updated = True
                order_book_updated = True
            elif cr_hist.is_qty_decrease():
                if acknowledgement_report.qty() == 0:
                    self._logger.debug(
                        "%s: OrderChain %s Cancel Replace Ack %s. Qty decreased from %d to %d at %s. No more qty so removing from level." %
                        (self.name(),
                         str(acknowledgement_report.chain_id()),
                         str(acknowledgement_report.event_id()),
                         cr_hist.previous_exposure().qty(),
                         cr_hist.new_exposure().qty(),
                         str(price)))
                    price_to_level[acknowledgement_report.price()].remove_from_level(resulting_order_chain)
                    # TODO don't I need to delete level if now nothing?
                    if price == pre_cr_best_price:
                        tob_updated = True
                    order_book_updated = True
                else:
                    self._logger.debug(
                        "%s: OrderChain %s Cancel Replace Ack %s. Qty decreased from %d to %d at %s. No priority changes." %
                        (self.name(),
                         str(acknowledgement_report.chain_id()),
                         str(acknowledgement_report.event_id()),
                         cr_hist.previous_exposure().qty(),
                         cr_hist.new_exposure().qty(),
                         str(price)))
                    # need to force the dirty flag at the price level
                    price_to_level[price].force_dirty()
                    if price == pre_cr_best_price:
                        tob_updated = True
                    order_book_updated = True
        if order_book_updated:
            self._notify_listeners(resulting_order_chain, tob_updated)
        return order_book_updated, tob_updated

    def handle_partial_fill_report(self, partial_fill_report, resulting_order_chain):
        # only need to updat the orderbook if a passive fill, if its the
        #  aggressive fill then it shouldn't be in the order book so the fill
        #  doesn't impact the order book
        self._last_update_time = partial_fill_report.timestamp()
        is_bid = resulting_order_chain.side().is_bid()
        price_to_level = self._bid_price_to_level if resulting_order_chain.side().is_bid() else self._ask_price_to_level
        pre_fill_best_price = price_to_level.max_price() if is_bid else price_to_level.min_price()
        order_book_updated = False
        tob_updated = False
        if not partial_fill_report.is_aggressor():
            if resulting_order_chain.visible_qty() > 0:
                price = resulting_order_chain.current_price()
                self._logger.debug("%s: OrderChain %s Partial Fill %s. Updated exposure %d (%d) @ %s." %
                                   (self.name(),
                                    str(partial_fill_report.chain_id()),
                                    str(partial_fill_report.event_id()),
                                    resulting_order_chain.visible_qty(),
                                    resulting_order_chain.hidden_qty(),
                                    str(price)))
                # a partial fill might not result in any modification of the level, but requires that visible/hidden be
                #  recalculated so force the dirty flag
                price_to_level[price].force_dirty()
                # if the visible qty replenished from hidden reserve then need to move to back of line
                if resulting_order_chain.caused_visible_qty_refresh(partial_fill_report.event_id()):
                    self._logger.debug(
                        "%s: OrderChain %s Partial Fill %s resulted in visible qty refresh. Moving priority to back." %
                        (self.name(),
                         str(partial_fill_report.chain_id()),
                         str(partial_fill_report.event_id())))
                    price_to_level[price].remove_from_level(resulting_order_chain)
                    if price not in price_to_level:
                        price_to_level[price] = TimePriorityOrderLevel(self._logger)
                    price_to_level[price].add_to_level(resulting_order_chain)
                    order_book_updated = True
                    if is_bid:
                        if price >= pre_fill_best_price:
                            tob_updated = True
                    else:
                        if price <= pre_fill_best_price:
                            tob_updated = True
            else:
                price = partial_fill_report.fill_price()
                self._logger.error(
                    "%s: OrderChain %s Partial Fill %s. Resulted in no visible qty %d (%d) @ %s. Removing from order book." %
                    (self.name(),
                     str(partial_fill_report.chain_id()),
                     str(partial_fill_report.event_id()),
                     resulting_order_chain.visible_qty(),
                     resulting_order_chain.hidden_qty(),
                     str(price)))
                if price_to_level[price].has_order_chain(partial_fill_report.chain_id()):
                    price_to_level[price].remove_from_level(resulting_order_chain)
                else:
                    self._logger.error(
                        "%s: OrderChain %s Partial Fill %s. OrderChain not at price @ %s. Cannot remove from OrderBook." %
                        (self.name(),
                         str(partial_fill_report.chain_id()),
                         str(partial_fill_report.event_id()),
                         str(price)))
                if len(price_to_level[price].order_chains()) == 0:
                    del price_to_level[price]
                order_book_updated = True
                if price == pre_fill_best_price:
                    tob_updated = True
        if order_book_updated:
            self._notify_listeners(resulting_order_chain, tob_updated)
        return order_book_updated, tob_updated

    def handle_full_fill_report(self, full_fill_report, resulting_order_chain):
        self._last_update_time = full_fill_report.timestamp()
        is_bid = resulting_order_chain.side().is_bid()
        price_to_level = self._bid_price_to_level if is_bid else self._ask_price_to_level
        pre_fill_best_price = price_to_level.max_price() if is_bid else price_to_level.min_price()
        order_book_updated = False
        tob_updated = False
        if not full_fill_report.is_aggressor():
            fill_price = full_fill_report.fill_price()
            self._logger.debug("%s: OrderChain %s Full Fill %s. Removing order from price %s." %
                               (self.name(),
                                str(full_fill_report.chain_id()),
                                str(full_fill_report.event_id()),
                                str(fill_price)))
            if price_to_level[fill_price].has_order_chain(full_fill_report.chain_id()):
                price_to_level[fill_price].remove_from_level(resulting_order_chain)
                order_book_updated = True
                if fill_price == pre_fill_best_price:
                    tob_updated = True
                if len(price_to_level[fill_price].order_chains()) == 0:
                    del price_to_level[fill_price]
            else:
                self._logger.error(
                    "%s: OrderChain %s Full Fill %s. OrderChain not at price @ %s. Cannot remove from OrderBook." %
                    (self.name(),
                     str(full_fill_report.chain_id()),
                     str(full_fill_report.event_id()),
                     str(full_fill_report.fill_price())))
        else:  # if it is the full fill then if there was an ack, we need to remove from that ack, as full fill comes from cancel replace to new price
            last_ack = resulting_order_chain.last_acknowledgement()
            if last_ack is not None:
                price = last_ack.price()
                price_to_level[price].remove_from_level(resulting_order_chain)
                order_book_updated = True
                if price == pre_fill_best_price:
                    tob_updated = True
                if len(price_to_level[price].order_chains()) == 0:
                    del price_to_level[price]

        # if the order book has updated, we need to notify the listeners that a change occurred
        if order_book_updated:
            self._notify_listeners(resulting_order_chain, tob_updated)

        return order_book_updated, tob_updated

    def handle_cancel_report(self, cancel_report, resulting_order_chain):
        self._last_update_time = cancel_report.timestamp()
        is_bid = resulting_order_chain.side().is_bid()
        price_to_level = self._bid_price_to_level if is_bid else self._ask_price_to_level
        pre_cancel_best_price = price_to_level.max_price() if is_bid else price_to_level.min_price()
        order_book_updated = False
        tob_updated = False
        # remove it from the price at the time of close if it is a FAR and if it has been ack'd
        if resulting_order_chain.is_far() and resulting_order_chain.has_acknowledgement():
            price = resulting_order_chain.price_at_close()
            level = price_to_level.get(price)
            if level.has_order_chain(resulting_order_chain.chain_id()):
                level.remove_from_level(resulting_order_chain)
                self._logger.debug("%s: OrderChain %s Cancel Confirm %s. Removed from %s." %
                                   (self.name(),
                                    str(cancel_report.chain_id()),
                                    str(cancel_report.event_id()),
                                    str(price)))
                if len(price_to_level[price].order_chains()) == 0:
                    del price_to_level[price]
                if price == pre_cancel_best_price:
                    tob_updated = True
                order_book_updated = True
            else:
                # go through all other prices on side and see if there, if so then remove it
                self._logger.warning("%s: OrderChain %s Cancel Confirm %s. Not at price at close %s. Searching book." %
                                     (self.name(),
                                      str(cancel_report.chain_id()),
                                      str(cancel_report.event_id()),
                                      str(resulting_order_chain.price_at_close())))
                for price, the_level in price_to_level.iteritems():
                    if the_level.has_order_chain(resulting_order_chain):
                        the_level.remove_from_level(resulting_order_chain)
                        self._logger.warning(
                            "%s: OrderChain %s Cancel Confirm %s. Not at price at close %s. Found and removed from %s." %
                            (self.name(),
                             str(cancel_report.chain_id()),
                             str(cancel_report.event_id()),
                             str(resulting_order_chain.price_at_close()),
                             str(price)))
                        if len(price_to_level[price].order_chains()) == 0:
                            del price_to_level[price]
                        order_book_updated = True
                        if price == pre_cancel_best_price:
                            tob_updated = True
                        break
        if not order_book_updated:
            # no there was never an ack then no need to log, cancelled before ever resting.
            if resulting_order_chain.has_acknowledgement():
                self._logger.error(
                    "%s: OrderChain %s Cancel Confirm %s. Not at price at close %s. Not found in book. Could not remove" %
                    (self.name(),
                     str(cancel_report.chain_id()),
                     str(cancel_report.event_id()),
                     str(resulting_order_chain.price_at_close())))
        else:
            self._notify_listeners(resulting_order_chain, tob_updated)
        return order_book_updated, tob_updated

    # TODO add handle_chain_close() and delete order if it is still in order book
    # If it was still in the order book that's a problem.

    def __str__(self):
        s = ""
        ask_prices = sorted(self.prices(ASK_SIDE), reverse=True)
        for price in ask_prices:
            if price is None:
                continue
            s += "%s%.12f\t\t" % (" " * 40, price.price())
            order_chains = self._ask_price_to_level[price].order_chains()
            for order_chain in order_chains:
                s += "%s %d (%d/%d) %s, " % \
                     (str(order_chain.chain_id()),
                      order_chain.most_recent_subchain().subchain_id(),
                      order_chain.visible_qty(),
                      order_chain.hidden_qty(),
                      order_chain.user_id())
            s += "\n"
        s += "--------------------------------------\n"
        bid_prices = self.prices(BID_SIDE)
        for price in bid_prices:
            if price is None:
                continue
            s += "%.12f\t\t" % price.price()
            order_chains = self._bid_price_to_level[price].order_chains()
            for order_chain in order_chains:
                s += "%s %d (%d/%d) %s, " % (
                    str(order_chain.chain_id()), order_chain.most_recent_subchain().subchain_id(), order_chain.visible_qty(), order_chain.hidden_qty(),
                    order_chain.user_id())
            s += "\n"
        return s


class AggregateOrderLevelBook(OrderLevelBook, OrderLevelBookListener):

    def __init__(self, market, logger, component_books=None, name=None):
        assert component_books is None or isinstance(component_books, (list, tuple, set))
        OrderLevelBook.__init__(self, market, logger, name)
        OrderLevelBookListener.__init__(self, logger)
        self._component_books = set()
        self._market_to_component_book = {}
        if component_books is not None:
            for component_book in component_books:
                self.add_component_book(component_book)
        self._name = "AggregateOrderLevelOrderBook %s@%s" % (market.product().name(), market.endpoint().name()) if name is None else name

    def _validate_component_order_book(self, order_book):
        # an implementing inheritor of AggregateOrderBook can put logic here to test if the orderbook should even be
        #  added to the AggregateOrderBook. For example, some aggregate order books might want to check that all
        #  component order books are the same product or the have the same tick size or are denominated the same way.
        # If this function returns false, it won't get added as a component order book
        assert isinstance(order_book, OrderLevelBook)

    def _pre_notify_listeners(self, causing_order_chain, agg_tob_updated):
        """
        This is a function where an implementing instance of AggregateOrderBook can do some work before listeners are
        notified of a change.
        :return:
        """
        pass

    def add_component_book(self, order_book):
        """
        returns True if added, False if not added
        """
        assert isinstance(order_book, OrderLevelBook)
        should_add = self._validate_component_order_book(order_book)
        self._logger.info("%s is adding order book for %s" % (self.name(), str(order_book.market())))
        added = False
        if should_add:
            self._component_books.add(order_book)
            self._market_to_component_book[order_book.market()] = order_book
            order_book.add_order_level_book_listener(self.name(), self)
            added = True
        return added

    def component_books(self):
        return self._component_books

    def has_component_book(self, order_book):
        assert isinstance(order_book, OrderLevelBook)
        return order_book in self._component_books

    def has_component_market(self, market):
        assert isinstance(market, Market)
        return market in self._market_to_component_book

    def component_pool_with_price(self, side, price):
        pools = set()
        for ob in self._component_books:
            if ob.visible_qty_at_price(side, price) > 0:
                pools.add(ob.market())
        return pools

    def order_books_at_price(self, side, price):
        obs = set()
        for ob in self._component_books:
            if ob.visible_qty_at_price(side, price) > 0:
                obs.add(ob)
        return obs

    def _tob_updated(self, component_order_book, causing_order_chain, tob_updated):
        """
        This gets called before the dirty flags are set (as those should be set in _pre_notify_listeners) and will
          determine if the tob_updated flag in the update should be true or false
        :param component_order_book:
        :param causing_order_chain:
        :param tob_updated:
        :return:
        """
        agg_tob_updated = False
        if tob_updated:
            # only need to check the side of the causing order chain
            tob = component_order_book.best_price(causing_order_chain.side())
            agg_tob = self.best_price(causing_order_chain.side())
            # if they are both None or if they are both same price, then we need assume tob updated for agg book
            if tob is None and agg_tob is None:
                agg_tob_updated = True
            if tob is not None and agg_tob is not None:
                if tob == agg_tob:
                    agg_tob_updated = True
        return agg_tob_updated

    def notify_book_update(self, component_order_book, causing_order_chain, tob_updated):
        agg_tob_updated = self._tob_updated(component_order_book, causing_order_chain, tob_updated)
        self._pre_notify_listeners(causing_order_chain, agg_tob_updated)
        self._notify_listeners(causing_order_chain, agg_tob_updated)

    def clean_up_order_chain(self, order_chain):
        """
        Function let's the order book listener clean up data it might be storing for the order chain.

        Should only be called if the data being kept by the listener for the order chain (or events in the order chain
         is no longer needed)

        :param order_chain: Buttonwood.MarketObjects.Events.EventChains.OrderEventChain
        :return:
        """
        pass  # not tracking of order chains that needs to be cleaned up

    def name(self):
        """
        Returns the name of the OrderLevelBook instance.

        :return: str
        """
        return self._name

    def last_update_time(self):
        """
        Gets the last time, as a second timestamp (seconds.milli/microseconds) that the order book last updated.

        :return: float
        """
        return max(ob.last_update_time() for ob in self._component_books)

    def best_priority_chain(self, side):
        """
        Get the best priority live chain for the given side of the book.

        :return: MarketObjects.Events.EventChains.OrderEventChain
        """
        raise Exception("best_priority_chain: To be implemented by implementation of AggregateOrderLevelBook")

    def prices(self, side):
        """
        All the prices on the given side that are currently live in the order
         book, from best price to worse. For the bids, that is highest to
         lowest; for the asks, that is lowest to highest.

        :param side: MarketObjects.Side.Side
        :return: list of MarketObjects.Price.Price
        """
        raise Exception("prices: To be implemented by implementation of AggregateOrderLevelBook")

    def best_price(self, side):
        """
        Returns the best price of the of the book (top of book price) for the specified side.
        Will return None if the side is empty

        :return: Price. the top of book price for the passed in side. None if side is empty
        """
        raise Exception("best_price: To be implemented by implementation of AggregateOrderLevelBook")

    def best_level(self, side):
        """
        Gets the best PriceLevel for the given side. Can be None if side is empty.

        :return: MarketObjects.PriceLevel.PriceLevel
        """
        raise Exception("best level: To be implemented by implementation of AggregateOrderLevelBook")

    def visible_qty_at_price(self, side, price):
        """
        Gets the visible quantity for the price on the specified side of the
         market. If there are no orders at that price on that side, then will
         return 0.

        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price
        :return: int
        """
        raise Exception("visible_qty_at_price: To be implemented by implementation of AggregateOrderLevelBook")

    def hidden_qty_at_price(self, side, price):
        """
        Gets the hidden quantity for the price on the specified side of the
         market. If there are no orders at that price on that side, then will
         return 0.

        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price
        :return: int
        """
        raise Exception("hidden_qty_at_price: To be implemented by implementation of AggregateOrderLevelBook")

    def num_orders_at_price(self, side, price):
        """
        Get the number of orders at price for a given side. If price the price is
         empty for that side, return 0.

        If include_hidden_orders is True then it will include orders that are
         hidden size only, otherwise those will not be included. This is an
         optional argument that defaults False.

        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Priceorder_book_output
        :return: int
        """
        raise Exception("num_orders_at_price: To be implemented by implementation of AggregateOrderLevelBook")

    def order_chains_at_price(self, side, price):
        """
        Gets the order chains at given price and side, in the order of their current priority, where the first order
         chain is first in line to be matched by the next aggressive fill and the last would only get a match if all
         the others' visible qty was fully filled.

        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price
        :return: list of MarketObjects.Events.EventChains.OrderEventChain
        """
        raise Exception("order_chains_at_price: To be implemented by implementation of AggregateOrderLevelBook")

    def iter_order_chains_at_price(self, side, price):
        """
        Gets the iterable of order chains at given price and side, in the order of their current priority, where the
         first order chain is first in line to be matched by the next aggressive fill and the last would only get a
         match if all the others' visible qty was fully filled.

        This is similar to order_chains_at_price(self, side, price) but it returns the iterable rather than a list,
         which is a much more efficient way to work with order event chains if you are just walking across them.

        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price
        :return: list of MarketObjects.Events.EventChains.OrderEventChain
        """
        raise Exception("iter_order_chains_at_price: To be implemented by implementation of AggregateOrderLevelBook")

    def level_at_price(self, side, price):
        """
        Gets the PriceLevel at a price for a given side. Returns None if the
         price does not exist on that Side.

        :param side: MarketObjects.Side.Side
        :param price: MarketObjects.Price.Price
        :return: MarketObjects.PriceLevel.PriceLevel. Can be None
        """
        raise Exception("level_at_price: order_chains_at_price: To be implemented by implementation of AggregateOrderLevelBook")

    def to_json(self):
        ob_json = {}
        for side in [BID_SIDE, ASK_SIDE]:
            side_dict = {}
            for level, price in enumerate(self.prices(side)):
                level = self.level_at_price(side, price)
                chain_ids = []
                for chain in self.order_chains_at_price(side, price):
                    chain_ids.append(chain.chain_id())
                side_dict[level] = {"price": price,
                                    "visible_qty": level.visible_qty(),
                                    "hidden_qty": level.hidden_qty(),
                                    "chains": chain_ids}
            ob_json[str(side)] = side_dict
        return {"order_book_type": self.name(), "market": self.market().to_json(), "order_book": ob_json}

    def __str__(self):
        s = "%s\n" % self.name()
        ask_prices = sorted(self.prices(ASK_SIDE), reverse=True)
        for price in ask_prices:
            if price is not None:
                order_books = self.order_books_at_price(ASK_SIDE, price)
                s += "%s%.12f %d (%d) [%s]\n" % (" " * 40, price.price(), self.visible_qty_at_price(ASK_SIDE, price), self.hidden_qty_at_price(ASK_SIDE, price), ",".join(order_book.market().endpoint().name() for order_book in order_books))
        s += "--------------------------------------\n"
        bid_prices = self.prices(BID_SIDE)
        for price in bid_prices:
            if price is not None:
                order_books = self.order_books_at_price(BID_SIDE, price)
                s += "%.12f %d (%d) [%s]\n" % (price.price(), self.visible_qty_at_price(BID_SIDE, price), self.hidden_qty_at_price(BID_SIDE, price), ",".join(order_book.market().endpoint().name() for order_book in order_books))
        return s

    """
    NO ORDER BOOK MANIPULATION

    By design, aggregate books are intended for lazy evaluation of values that are aggregates of the component books. 
     This means that there is no direct manipulation of an aggregate order book and it is not a listener of events.
    """
