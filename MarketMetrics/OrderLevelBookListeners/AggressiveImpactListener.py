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

from MarketPy.MarketObjects.OrderBookListeners.OrderLevelBookListener import OrderLevelBookListener
from MarketPy.MarketObjects.EventListeners.OrderEventListener import OrderEventListener
from MarketPy.MarketObjects.Side import BID_SIDE
from MarketPy.MarketObjects.Side import ASK_SIDE
from MarketPy.utils.dicts import NDeepDict
from collections import defaultdict


class AggressiveAct:

    def __init__(self, aggressing_event, bid_price_levels, ask_price_levels, event_id, negotiation_id):
        self._aggressing_event = aggressing_event
        self._total_aggressive_qty = 0
        self._is_closed = False
        self._aggressive_side = aggressing_event.side()
        self._open_bid_price_levels = bid_price_levels
        self._open_ask_price_levels = ask_price_levels
        self._close_bid_price_levels = None
        self._close_ask_price_levels = None
        self._event_id = event_id
        self._negotiation_id = negotiation_id

    def __str__(self):
        return "Negotiation ID: %s. Aggressing Event ID: %s\n" % (self._negotiation_id, str(self._aggressing_event.event_id()))

    def event_id(self):
        return self._event_id

    def negotiation_id(self):
        return self._negotiation_id

    def aggressing_time(self):
        return self._aggressing_event.timestamp()

    def aggressing_user_id(self):
        return self._aggressing_event.user_id()

    def aggressive_side(self):
        return self._aggressing_event.side()

    def requested_qty(self):
        return self._aggressing_event.qty()

    def close(self, close_bid_price_levels, close_ask_price_levels):
        self._is_closed = True
        self._close_bid_price_levels = close_bid_price_levels
        self._close_ask_price_levels = close_ask_price_levels

    def is_closed(self):
        return self._is_closed

    def add_aggressive_fill(self, fill_event):
        self._total_aggressive_qty += fill_event.fill_qty()

    def filled_qty(self):
        return self._total_aggressive_qty

    def impact(self):
        impact = 0.0
        if self._aggressing_event.side().is_bid():
            open_price_levels = self._open_ask_price_levels
            close_price_levels = self._close_ask_price_levels
        else:
            open_price_levels = self._open_bid_price_levels
            close_price_levels = self._close_bid_price_levels

        for price_level in open_price_levels:
            # if no price levels in close or top of book close is worse price then add a whole level
            if len(close_price_levels) == 0 or price_level.price().better_than(close_price_levels[0].price(), self.aggressive_side().other_side()):
                impact += 1
            # if the same price then we need to calc the difference in total size and get that % and break the loop
            elif price_level.price() == close_price_levels[0].price():
                size_taken_out = price_level.total_qty() - close_price_levels[0].total_qty()
                if size_taken_out < 0:
                    raise Exception("%d - %d is a negative number!" % (price_level.total_qty(), close_price_levels[0].total_qty()))
                percentage = float(size_taken_out) / price_level.total_qty()
                impact += percentage
                break
        return impact


class AggressiveImpactListener(OrderLevelBookListener, OrderEventListener):
    """
    Tracks the Aggressive Impact of each subchain.

    The aggressive impact of a subchain is how many levels of the order book
     that the subchain took out upon open. The left of the decimal is how many
     entire price levels the subchain took out and the right of the decimal is
     the percentage of the next level.

    Aggressive impact value examples:
      * 2 and a half levels --> 2.5
      * 80% of top of book only --> 0.8
      * 4 levels exactly --> 4.0
      * doesn't aggress --> 0.0
    """

    # TODO UNIT TEST
    def __init__(self, logger):
        OrderLevelBookListener.__init__(self, logger)
        OrderEventListener.__init__(self, logger)
        self._product_event_id_aggressive_act = NDeepDict(depth=2, default_value=None)
        self._product_to_orderbook = defaultdict(lambda: None)
        self._negotiation_id_to_bid_levels = defaultdict(lambda: None)
        self._negotiation_id_to_ask_levels = defaultdict(lambda: None)
        self._product_to_agg_acts_to_close = defaultdict(list)

    def _price_levels(self, product, side):
        price_levels = []
        if self._product_to_orderbook[product] is not None:
            order_book = self._product_to_orderbook[product]
            prices = order_book.prices(side)
            for price in prices:
                price_levels.append(order_book.level_at_price(side, price))
        return price_levels

    def handle_acknowledgement_report(self, acknowledgement_report, resulting_order_chain):
        event_id = acknowledgement_report.causing_command().event_id()
        product = acknowledgement_report.product()
        if self._product_event_id_aggressive_act.get((product, event_id)) is not None:
            bid_levels = self._price_levels(product, BID_SIDE)
            ask_levels = self._price_levels(product, ASK_SIDE)
            self._product_event_id_aggressive_act.get((product, event_id)).close(bid_levels, ask_levels)

    def _handle_fill(self, fill, resulting_order_chain):
        negotiation_id = fill.match_id()
        product = fill.product()
        if self._negotiation_id_to_ask_levels[negotiation_id] is None:
            self._negotiation_id_to_ask_levels[negotiation_id] = self._price_levels(product, ASK_SIDE)
        if self._negotiation_id_to_bid_levels[negotiation_id] is None:
            self._negotiation_id_to_bid_levels[negotiation_id] = self._price_levels(product, BID_SIDE)

        # if an aggressor that aggressing event already exists we add the fill
        if fill.is_aggressor():
            event_id = fill.causing_command().event_id()
            # if the subchain already exists then we add a fill to it
            agg_act = self._product_event_id_aggressive_act.get((product, event_id))
            if agg_act is not None:
                if agg_act.is_closed():
                    raise Exception("Got a fill for closed ChainID %s SubChainID %s)" % (str(resulting_order_chain.chain_id()), str(event_id)))
                agg_act.add_aggressive_fill(fill)

            # if the event_id of the aggressor does not already exist, we create it
            else:
                bid_price_levels = self._negotiation_id_to_bid_levels[negotiation_id]
                ask_price_levels = self._negotiation_id_to_ask_levels[negotiation_id]
                agg_act = AggressiveAct(fill.aggressing_command(), bid_price_levels, ask_price_levels, event_id, negotiation_id)
                agg_act.add_aggressive_fill(fill)
                self._product_event_id_aggressive_act.set((product, event_id), value=agg_act)

    def handle_partial_fill_report(self, partial_fill_report, resulting_order_chain):
        self._handle_fill(partial_fill_report, resulting_order_chain)

    def handle_full_fill_report(self, full_fill_report, resulting_order_chain):
        self._handle_fill(full_fill_report, resulting_order_chain)
        product = full_fill_report.product()
        # on an aggressive full fill we close out the open order chain
        if full_fill_report.is_aggressor():
            event_id = full_fill_report.causing_command().event_id()
            if self._product_event_id_aggressive_act.get((product, event_id)) is not None:
                # we need to get the order level books after all the updates are done.
                #self._product_to_agg_acts_to_close[product].add(event_id)
                self._product_event_id_aggressive_act.get((product, event_id)).close(self._price_levels(product, BID_SIDE),
                                                                                     self._price_levels(product, ASK_SIDE))

    def handle_cancel_report(self, cancel_report, resulting_order_chain):
        # on a cancel we close out the open order chain because of FAKs
        product = cancel_report.product()
        event_id = cancel_report.causing_command().event_id()
        if self._product_event_id_aggressive_act.get((product, event_id)) is not None:
            self._product_event_id_aggressive_act.get((product, event_id)).close(self._price_levels(product, BID_SIDE),
                                                                                    self._price_levels(product, ASK_SIDE))

    def clean_up(self, order_chain):
        """
        If clean_up is called with an order_chain than this will go through the
         order chain's subchain IDs and delete each one from the maps that store
         the aggressive acts for a subchain.

        WARNING: once this is called, the get_aggressive_impact and
         get_aggressive_qty will no longer return the values that are
         meaningful; rather, you'll get the 0 values

        :param order_chain: MarketObjects.Events.EventChains.OrderEventChain
        """
        # TODO
        pass

    def notify_book_update(self, order_book, causing_order_chain):
        product = order_book.product()
        self._product_to_orderbook[product] = order_book
        for agg_act in self._product_to_agg_acts_to_close[product]:
            agg_act.close(self._price_levels(product, BID_SIDE), self._price_levels(product, ASK_SIDE))
        del self._product_to_agg_acts_to_close[product]

    def get_aggressive_impact(self, product, event_id):
        if self._product_event_id_aggressive_act.get((product, event_id)) is not None:
            return self._product_event_id_aggressive_act.get((product, event_id)).impact()
        return 0.0

    def get_aggressive_qty(self, product, event_id):
        if self._product_event_id_aggressive_act.get((product, event_id)) is not None:
            return self._product_event_id_aggressive_act.get((product, event_id)).filled_qty()
        return 0
