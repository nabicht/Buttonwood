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
from MarketPy.utils.dicts import NDeepDict
from collections import defaultdict


class AggressiveAct:

    def __init__(self, aggressing_event, event_id, negotiation_id):
        self._aggressing_event = aggressing_event
        self._total_aggressive_qty = 0
        self._is_closed = False
        self._aggressive_side = aggressing_event.side()
        self._event_id = event_id
        self._negotiation_id = negotiation_id
        self._price_to_qty = {}
        self._impact = 0.0

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

    def close(self, order_book):
        self._is_closed = True
        impact = 0.0
        opposite_side = self._aggressive_side.other_side()
        opposite_tob = order_book.best_level(opposite_side)
        # if the opposite tob is worse than the last fill price, then there is no impact on top of book. This can
        #  happen at venues that have stupidly bad self trade prevention.
        for fill_price, fill_qty in self._price_to_qty.iteritems():
            if opposite_tob is not None and fill_price == opposite_tob.price():
                total_qty = opposite_tob.total_qty() + fill_qty
                impact += float(fill_qty) / total_qty
            elif opposite_tob is None or fill_price.worse_than(opposite_tob, self._aggressive_side):
                impact += 1
        self._impact = impact

    def is_closed(self):
        return self._is_closed

    def add_aggressive_fill(self, fill_event):
        fill_qty = fill_event.fill_qty()
        self._total_aggressive_qty += fill_qty
        price = fill_event.fill_price()
        if self._price_to_qty.get(price):
            self._price_to_qty[fill_event.fill_price()] += fill_qty
        else:
            self._price_to_qty[fill_event.fill_price()] = fill_qty

    def filled_qty(self):
        return self._total_aggressive_qty

    def impact(self):
        return self._impact


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
        self._market_event_id_aggressive_act = NDeepDict(depth=2, default_value=None)
        self._market_to_orderbook = defaultdict(lambda: None)
        self._market_to_agg_acts_to_close = defaultdict(set)

    def handle_acknowledgement_report(self, acknowledgement_report, resulting_order_chain):
        event_id = acknowledgement_report.causing_command().event_id()
        market = acknowledgement_report.market()
        agg_event = self._market_event_id_aggressive_act.get((market, event_id))
        if agg_event:
            self._market_to_agg_acts_to_close[market].add(self._market_event_id_aggressive_act.get((market, event_id)))

    def _handle_fill(self, fill, resulting_order_chain):
        negotiation_id = fill.match_id()
        market = fill.market()

        # if an aggressor that aggressing event already exists we add the fill
        if fill.is_aggressor():
            event_id = fill.causing_command().event_id()
            # if the subchain already exists then we add a fill to it
            agg_act = self._market_event_id_aggressive_act.get((market, event_id))
            # if the event_id of the aggressor does not already exist, we create it
            if not agg_act:
                agg_act = AggressiveAct(fill.aggressing_command(), event_id, negotiation_id)
                self._market_event_id_aggressive_act.set((market, event_id), value=agg_act)
            else:
                if agg_act.is_closed():
                    raise Exception("Got a fill for closed ChainID %s SubChainID %s)" % (str(resulting_order_chain.chain_id()), str(event_id)))
            agg_act.add_aggressive_fill(fill)

    def handle_partial_fill_report(self, partial_fill_report, resulting_order_chain):
        self._handle_fill(partial_fill_report, resulting_order_chain)

    def handle_full_fill_report(self, full_fill_report, resulting_order_chain):
        self._handle_fill(full_fill_report, resulting_order_chain)
        market = full_fill_report.market()
        # on an aggressive full fill we close out the open order chain
        if full_fill_report.is_aggressor():
            event_id = full_fill_report.causing_command().event_id()
            if self._market_event_id_aggressive_act.get((market, event_id)) is not None:
                # we need to get the order level books after all the updates are done.
                self._market_to_agg_acts_to_close[market].add(self._market_event_id_aggressive_act.get((market, event_id)))
            else:
                raise Exception("Got an aggressive full fill but not tracking aggressive acts for event: %s" % str(event_id))

    def handle_cancel_report(self, cancel_report, resulting_order_chain):
        # on a cancel we close out the open order chain because of FAKs
        market = cancel_report.market()
        event_id = cancel_report.causing_command().event_id()
        agg_event = self._market_event_id_aggressive_act.get((market, event_id))
        if agg_event:
            self._market_to_agg_acts_to_close[market].add(agg_event)

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
        market = order_book.market()

        for agg_act in self._market_to_agg_acts_to_close[market]:
            agg_act.close(order_book)
        del self._market_to_agg_acts_to_close[market]

    def get_aggressive_impact(self, market, event_id):
        if self._market_event_id_aggressive_act.get((market, event_id)) is not None:
            return self._market_event_id_aggressive_act.get((market, event_id)).impact()
        return 0.0

    def get_aggressive_qty(self, market, event_id):
        if self._market_event_id_aggressive_act.get((market, event_id)) is not None:
            return self._market_event_id_aggressive_act.get((market, event_id)).filled_qty()
        return 0
