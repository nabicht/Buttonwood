"""
This file is part of MarketPy. 

MarketPy is a python software package created to help quickly create, (re)build, or 
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
from MarketPy.MarketObjects.EventListeners.OrderEventListener import OrderEventListener
from MarketPy.MarketObjects.Events import OrderEventConstants as TIF
from MarketPy.MarketObjects.Events.OrderEvents import NewOrderCommand
from MarketPy.MarketObjects.OrderBooks.BasicOrderBook import BasicOrderBook
from MarketPy.MarketObjects.PriceLevel import PriceLevel
from MarketPy.MarketObjects.Side import BID_SIDE
from MarketPy.MarketObjects.Side import ASK_SIDE
from MarketPy.MarketObjects.OrderBookListeners.OrderLevelBookListener import OrderLevelBookListener


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
            self._dirty = True
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
            self._dirty = True
            self._logger.debug("%s: Removed %s from %s." %
                               (self.__class__.__name__,
                                str(order_chain.chain_id()),
                                str(order_chain.current_exposure().price())))

    def force_dirty(self):
        # this function needs to exist because if there is a cancel replace down in qty this class will never know,
        #  so whatever calls add_to_level and remove_from_level needs to be responsible for forcing the dirty flag to
        #  true
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
            #only have to worry about setting max and min if a new key
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

    def __init__(self, product, logger, name=None):
        BasicOrderBook.__init__(self, product, logger)
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
                          (self.name(), self._product.name(), order_level_book_listener.__class__.__name__))

    def order_level_book_listener(self, listener_id):
        """
        Get the OrderLevelBookListener that is assoicated with the passed in
         listener identifier. If there isn't then None is returned.

        :param listener_id: str
        :return: MarketObjects.OrderBookListeners.OrderLevelBookListener.OrderLevelBookListener. Can be None
        """
        return self._listeners.get(listener_id)

    def _notify_listeners(self, order_chain):
        for listener in self._listeners.itervalues():
            listener.notify_book_update(self, order_chain)

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
        :param price: MarketObjects.Price.Price
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
        return {"order_book_type": self.name(), "product": self.product().to_json(), "order_book": ob_json}

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
        if resulting_order_chain.time_in_force() != TIF.FAR:
            self._logger.error("%s: OrderChain %s Ack %s is a %s, not a FAR. Cannot apply to order book" %
                               (self.name(),
                                str(acknowledgement_report.chain_id()),
                                str(acknowledgement_report.event_id()),
                                TIF.time_in_force_str(resulting_order_chain.time_in_force())))
            return
        price_to_level = self._bid_price_to_level if resulting_order_chain.side().is_bid() else self._ask_price_to_level
        # if a new order then just add it
        if isinstance(acknowledgement_report.acknowledged_command(), NewOrderCommand):
            if acknowledgement_report.price() not in price_to_level:
                price_to_level[acknowledgement_report.price()] = TimePriorityOrderLevel(self._logger)
            price_to_level[acknowledgement_report.price()].add_to_level(resulting_order_chain)
            order_book_updated = True
        else:  # otherwise cancel replace and we need to be more careful
            cr_hist = resulting_order_chain.cancel_replace_information(acknowledgement_report.event_id())
            price = acknowledgement_report.price()
            if cr_hist is None:
                self._logger.error(
                    "%s: OrderChain %s Cannot apply ack of cancel replace %s. No cancel replace history." %
                    (self.name(),
                     str(acknowledgement_report.chain_id()),
                     str(acknowledgement_report.event_id())))
            elif cr_hist.is_price_change():
                # on price changes remove from old price and apply to new price.
                self._logger.debug("%s: OrderChain %s Cancel Replace Ack %s. From %s to %s." %
                                   (self.name(),
                                    str(acknowledgement_report.chain_id()),
                                    str(acknowledgement_report.event_id()),
                                    str(cr_hist.previous_exposure().price()),
                                    str(cr_hist.new_exposure().price())))
                price_to_level[cr_hist.previous_exposure().price()].remove_from_level(resulting_order_chain)
                if len(price_to_level[cr_hist.previous_exposure().price()]) == 0:
                    del price_to_level[cr_hist.previous_exposure().price()]
                if cr_hist.new_exposure().price() not in price_to_level:
                    price_to_level[cr_hist.new_exposure().price()] = TimePriorityOrderLevel(self._logger)
                price_to_level[cr_hist.new_exposure().price()].add_to_level(resulting_order_chain)
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
                    order_book_updated = True
        if order_book_updated:
            self._notify_listeners(resulting_order_chain)
        return order_book_updated

    def handle_partial_fill_report(self, partial_fill_report, resulting_order_chain):
        # only need to updat the orderbook if a passive fill, if its the
        #  aggressive fill then it shouldn't be in the order book so the fill
        #  doesn't impact the order book
        self._last_update_time = partial_fill_report.timestamp()
        price_to_level = self._bid_price_to_level if resulting_order_chain.side().is_bid() else self._ask_price_to_level
        order_book_updated = False
        if not partial_fill_report.is_aggressor():
            if resulting_order_chain.visible_qty() > 0:
                self._logger.debug("%s: OrderChain %s Partial Fill %s. Updated exposure %d (%d) @ %s." %
                                   (self.name(),
                                    str(partial_fill_report.chain_id()),
                                    str(partial_fill_report.event_id()),
                                    resulting_order_chain.visible_qty(),
                                    resulting_order_chain.hidden_qty(),
                                    str(resulting_order_chain.current_price())))
                # a partial fill might not result in any modification of the level, but requires that visible/hidden be
                #  recalculated so force the dirty flag
                price_to_level[resulting_order_chain.current_price()].force_dirty()
                # if the visible qty replenished from hidden reserve then need to move to back of line
                if resulting_order_chain.caused_visible_qty_refresh(partial_fill_report.event_id()):
                    self._logger.debug(
                        "%s: OrderChain %s Partial Fill %s resulted in visible qty refresh. Moving priority to back." %
                        (self.name(),
                         str(partial_fill_report.chain_id()),
                         str(partial_fill_report.event_id())))
                    price_to_level[resulting_order_chain.current_price()].remove_from_level(resulting_order_chain)
                    if resulting_order_chain.current_price() not in price_to_level:
                        price_to_level[resulting_order_chain.current_price()] = TimePriorityOrderLevel(self._logger)
                    price_to_level[resulting_order_chain.current_price()].add_to_level(resulting_order_chain)
                    order_book_updated = True
            else:
                self._logger.error(
                    "%s: OrderChain %s Partial Fill %s. Resulted in no visible qty %d (%d) @ %s. Removing from order book." %
                    (self.name(),
                     str(partial_fill_report.chain_id()),
                     str(partial_fill_report.event_id()),
                     resulting_order_chain.visible_qty(),
                     resulting_order_chain.hidden_qty(),
                     str(partial_fill_report.fill_price())))
                if price_to_level[partial_fill_report.fill_price()].has_order_chain(partial_fill_report.chain_id()):
                    price_to_level[partial_fill_report.fill_price()].remove_from_level(resulting_order_chain)
                else:
                    self._logger.error(
                        "%s: OrderChain %s Partial Fill %s. OrderChain not at price @ %s. Cannot remove from OrderBook." %
                        (self.name(),
                         str(partial_fill_report.chain_id()),
                         str(partial_fill_report.event_id()),
                         str(partial_fill_report.fill_price())))
                if len(price_to_level[partial_fill_report.fill_price()].order_chains()) == 0:
                    del price_to_level[partial_fill_report.fill_price()]
                order_book_updated = True
        if order_book_updated:
            self._notify_listeners(resulting_order_chain)
        return order_book_updated

    def handle_full_fill_report(self, full_fill_report, resulting_order_chain):
        self._last_update_time = full_fill_report.timestamp()
        price_to_level = self._bid_price_to_level if resulting_order_chain.side().is_bid() else self._ask_price_to_level
        order_book_updated = False
        if not full_fill_report.is_aggressor():
            self._logger.debug("%s: OrderChain %s Full Fill %s. Removing order from price %s." %
                               (self.name(),
                                str(full_fill_report.chain_id()),
                                str(full_fill_report.event_id()),
                                str(full_fill_report.fill_price())))
            if price_to_level[full_fill_report.fill_price()].has_order_chain(full_fill_report.chain_id()):
                price_to_level[full_fill_report.fill_price()].remove_from_level(resulting_order_chain)
                order_book_updated = True
                if len(price_to_level[full_fill_report.fill_price()].order_chains()) == 0:
                    del price_to_level[full_fill_report.fill_price()]
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
                price_to_level[last_ack.price()].remove_from_level(resulting_order_chain)
                order_book_updated = True
                if len(price_to_level[last_ack.price()].order_chains()) == 0:
                    del price_to_level[last_ack.price()]

        # if the order book has updated, we need to notify the listeners that a change occurred
        if order_book_updated:
            self._notify_listeners(resulting_order_chain)

        return order_book_updated

    def handle_cancel_report(self, cancel_report, resulting_order_chain):
        self._last_update_time = cancel_report.timestamp()
        price_to_level = self._bid_price_to_level if resulting_order_chain.side().is_bid() else self._ask_price_to_level
        order_book_updated = False
        # remove it from the price at the time of close if it is a FAR and if it has been ack'd
        if resulting_order_chain.is_far() and resulting_order_chain.has_acknowledgement():
            level = price_to_level.get(resulting_order_chain.price_at_close())
            if level.has_order_chain(resulting_order_chain.chain_id()):
                level.remove_from_level(resulting_order_chain)
                self._logger.debug("%s: OrderChain %s Cancel Confirm %s. Removed from %s." %
                                   (self.name(),
                                    str(cancel_report.chain_id()),
                                    str(cancel_report.event_id()),
                                    str(resulting_order_chain.price_at_close())))
                if len(price_to_level[resulting_order_chain.price_at_close()].order_chains()) == 0:
                    del price_to_level[resulting_order_chain.price_at_close()]
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
            self._notify_listeners(resulting_order_chain)
        return order_book_updated

    # TODO add handle_chain_close() and delete order if it is still in order book
    # If it was still in the order book that's a problem.

    def __str__(self):
        s=""
        ask_prices = sorted(self.prices(ASK_SIDE), reverse=True)
        for price in ask_prices:
            if price is None:
                continue
            s += "%s%.12f\t\t" % (" " * 40, price.price())
            order_chains = self._ask_price_to_level[price].order_chains()
            for order_chain in order_chains:
                s += "%s %d (%d/%d) %s, " % (
                str(order_chain.chain_id()), order_chain.most_recent_subchain().subchain_id(), order_chain.visible_qty(), order_chain.hidden_qty(), order_chain.user_id())
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