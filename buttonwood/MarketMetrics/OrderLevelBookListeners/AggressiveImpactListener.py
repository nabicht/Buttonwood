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
from buttonwood.MarketObjects.MatchSeries import MatchSeries
from buttonwood.utils.dicts import NDeepDict
from collections import defaultdict


class AggressiveAct(MatchSeries):

    def __init__(self, match_id):
        MatchSeries.__init__(self, match_id)
        self._total_aggressive_qty = 0
        self._impact = None

    def aggressing_user_id(self):
        return self._aggressor.user_id()

    def aggressive_side(self):
        return self._aggressor.side()

    def requested_qty(self):
        return self._aggressor.qty()

    def calculate(self, order_book):
        if self.balanced_match_qty():
            impact = 0.0
            passive_side = self._aggressor.side().other_side()
            passive_tob = order_book.best_level(passive_side)
            # if the opposite tob is worse than the last fill price, then there is no impact on top of book. This can
            #  happen at venues that have stupidly bad self trade prevention.
            for fill_price, fill_qty in self._agg_price_to_qty.iteritems():
                if passive_tob is not None and fill_price == passive_tob.price():
                    total_qty = passive_tob.total_qty() + fill_qty
                    impact += float(fill_qty) / total_qty
                elif passive_tob is None or fill_price.better_than(passive_tob.price(), passive_side):
                    impact += 1
            self._impact = impact

        else:
            raise Exception("Cannot calculated aggressive impact because match qty not balanced.")

    def is_closed(self):
        return self._impact is not None

    def add_fill(self, fill_event):
        MatchSeries.add_fill(self, fill_event)

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
        if market not in self._market_to_orderbook:
            return
        agg_event = self._market_event_id_aggressive_act.get((market, event_id))
        #if aggressor is acked then all fills on both sides shoud be done and we can calculate
        if agg_event:
            agg_event.calculate(self._market_to_orderbook[market])

    def _handle_fill(self, fill, resulting_order_chain):
        match_id = fill.match_id()
        market = fill.market()
        if market not in self._market_to_orderbook:
            return
        event_id = fill.causing_command().event_id()

        agg_act = self._market_event_id_aggressive_act.get((market, event_id))
        # if the event_id of the aggressor does not already exist, we create it
        if not agg_act:
            agg_act = AggressiveAct(match_id)
            self._market_event_id_aggressive_act.set((market, event_id), value=agg_act)
        agg_act.add_fill(fill)

    def handle_partial_fill_report(self, partial_fill_report, resulting_order_chain):
        self._handle_fill(partial_fill_report, resulting_order_chain)

    def handle_full_fill_report(self, full_fill_report, resulting_order_chain):

        market = full_fill_report.market()
        if market not in self._market_to_orderbook:
            return
        self._handle_fill(full_fill_report, resulting_order_chain)
        # on an aggressive full fill we close out the open order chain
        if full_fill_report.is_aggressor():
            event_id = full_fill_report.causing_command().event_id()
            agg_act = self._market_event_id_aggressive_act.get((market, event_id))
            if agg_act is not None:
                # if full fill and qty balanced we should be able to do the impact calculation right now because book up to date
                if agg_act.balanced_match_qty():
                    agg_act.calculate(self._market_to_orderbook[market])
                else: # we need to get the order level books after all the updates are done.
                    self._market_to_agg_acts_to_close[market].add(self._market_event_id_aggressive_act.get((market, event_id)))
            else:
                raise Exception("Got an aggressive full fill but not tracking aggressive acts for event: %s" % str(event_id))

    def handle_cancel_report(self, cancel_report, resulting_order_chain):
        # on a cancel we close out the open order chain because of FAKs
        market = cancel_report.market()
        if market not in self._market_to_orderbook:
            return
        event_id = cancel_report.causing_command().event_id()
        agg_event = self._market_event_id_aggressive_act.get((market, event_id))
        # if aggressor is cancelled then all fills on both sides should be done and we can calculate
        if agg_event:
            agg_event.calculate(self._market_to_orderbook[market])

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
        market = order_chain.market()
        for event in order_chain.events():
            self._market_event_id_aggressive_act.delete([market,event.event_id()])

    def notify_book_update(self, order_book, causing_order_chain, tob_updated):
        market = order_book.market()
        self._market_to_orderbook[market] = order_book
        remove_set = set()
        agg_acts_to_close = self._market_to_agg_acts_to_close[market]
        for agg_act in agg_acts_to_close:
            if agg_act.balanced_match_qty():
                agg_act.calculate(order_book)
        self._market_to_agg_acts_to_close[market] = agg_acts_to_close.difference(remove_set)

    def get_aggressive_impact(self, market, event_id):
        if self._market_event_id_aggressive_act.get((market, event_id)) is not None:
            impact = self._market_event_id_aggressive_act.get((market, event_id)).impact()
            return impact
        return 0.0

    def get_aggressive_qty(self, market, event_id):
        if self._market_event_id_aggressive_act.get((market, event_id)) is not None:
            return self._market_event_id_aggressive_act.get((market, event_id)).match_qty()
        return 0
