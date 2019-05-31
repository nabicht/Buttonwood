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

from buttonwood.MarketObjects.Events.OrderEvents import FillReport
from buttonwood.MarketObjects.Events.OrderEvents import FullFillReport
from collections import defaultdict


class MatchSeries:
    """
    A match series is a series of fills on both sides of the book that make up one match from one aggressing order.
    
    For example, a 20 lot buy could cross into the offer and match with 4 other resting orders. This class tracks 
     bundles all the resulting fills into one series of matches.
     
    MatchSeries has no requirement that the all the resulting fills are perfectly symmetric because not all venues 
     return symmetric fills. For the above example, one venue might return:
       * Buy 20
       * Sell 7
       * Sell 3
       * Sell 4
       * Sell 6
       
     While another venue returns:
       * Buy 7
       * Buy 3
       * Buy 4
       * Buy 6
       * Sell 7
       * Sell 3
       * Sell 4
       * Sell 6
     
     The only requirement when sanity checks are run on the MatchSeries is that the total size per price are equal
      on both sides of the match.
      
     Also, it uses internal functions for checking that they all equal get_buys(price) get_sells(price) to do the 
      checks. This let's people overwrite those functions in order to have "fuzzy matches" across asset classes or
      products
    
    Match time (timestamp) is time of first fill.
    
    :param match_series_id: unique identifier of the match series
    """

    def __init__(self, match_series_id):
        self._aggressor = None
        self._agg_price_to_qty = defaultdict(int)
        self._pas_price_to_qty = defaultdict(int)
        self._agg_fills = []
        self._pas_fills = []
        self._series_id = match_series_id
        self._match_time = None
        self._agg_fully_filled = False

    def series_id(self):
        return self._series_id

    def timestamp(self):
        return self._match_time

    def add_fill(self, fill_event):
        """
        Adds the passed in fill_event to the MatchSeries.
        
        :param fill_event: Buttonwood.MarketObject.Events.OrderEvents.FillEvent 
        :return: 
        """
        assert (fill_event is not None)
        assert (isinstance(fill_event, FillReport)), "%s is not a FillReport" % type(fill_event)
        assert (fill_event.aggressing_command() is not None)
        assert (fill_event.match_id() == self.series_id()), "The FillEvent's match id needs to match the series' match id"

        # only check the aggressor if it isn't the first one
        if self._aggressor is None:
            self._aggressor = fill_event.aggressing_command()

        if self._match_time is None:
            self._match_time = fill_event.timestamp()

        if fill_event.is_aggressor():
            assert (fill_event.side() == self._aggressor.side()), "An aggressive fill should have same side as aggressor event."
            self._agg_price_to_qty[fill_event.fill_price()] += fill_event.fill_qty()
            self._agg_fills.append(fill_event)
            if isinstance(fill_event, FullFillReport):
                self._agg_fully_filled = True
        else:
            assert (fill_event.side() != self._aggressor.side()), "A passive fill should have different side than aggressor event."
            self._pas_price_to_qty[fill_event.fill_price()] += fill_event.fill_qty()
            self._pas_fills.append(fill_event)

    def aggressor_side(self):
        return None if self._aggressor is None else self._aggressor.side()

    def _price_qty_sanity_check(self):
        # should have same passive and aggressive prices
        if set(self._agg_price_to_qty.keys()) != set(self._pas_price_to_qty.keys()):
            raise Exception("Match Series {}: does not have same prices. Agg: {}. Pas: {}"
                            .format(str(self.series_id()), str(self._agg_price_to_qty.keys()),
                                    str(self._pas_price_to_qty.keys())))

        # should have same qty at each price
        for price, qty in self._agg_price_to_qty.iteritems():
            if qty != self._pas_price_to_qty[price]:
                raise Exception("Match Series %s: does not have same qty at price %s. Agg: %d. Pas: %d" %
                                (str(self.series_id()), str(price), qty, self._pas_price_to_qty[price]))

    def _fills_sanity_check(self):
        # should only have one full fill on aggressive side
        full_fills = []
        if len(self._agg_fills) == 0:
            raise Exception("Match Series %s: has no aggressive fills." % str(self.series_id()))
        if len(self._pas_fills) == 0:
            raise Exception("Match Series %s: has no passive fills." % str(self.series_id()))
        for fill in self._agg_fills:
            if isinstance(fill, FullFillReport):
                full_fills.append(fill)
        if len(full_fills) > 1:
            raise Exception("Match Series {}: has more than one aggressive full fill. {}"
                            .format(str(self.series_id()), str(full_fills)))

    def qty_at_price(self, price, sanity_check=True):
        if sanity_check:
            self._price_qty_sanity_check()
        return self._agg_price_to_qty[price]

    def price_to_qty(self, sanity_check=True):
        if sanity_check:
            self._price_qty_sanity_check()
        return self._agg_price_to_qty

    def match_qty(self, sanity_check=True):
        if sanity_check:
            self._price_qty_sanity_check()
        return self.aggressive_qty()

    def aggressive_qty(self):
        qty = 0
        for fill in self._agg_fills:
            qty += fill.fill_qty()
        return qty

    def passive_qty(self):
        qty = 0
        for fill in self._pas_fills:
            qty += fill.fill_qty()
        return qty

    def balanced_match_qty(self):
        return self.aggressive_qty() == self.passive_qty()

    def prices(self, sanity_check=True):
        if sanity_check:
            self._price_qty_sanity_check()
        return self._agg_price_to_qty.keys()

    def average_price(self, sanity_check=True):
        if sanity_check:
            self._price_qty_sanity_check()
        total_qty = 0
        price_weighted_qty = 0.0
        for price, qty in self._agg_price_to_qty.iteritems():
            total_qty += qty
            price_weighted_qty += float(price * qty)
        return price_weighted_qty / total_qty

    def price_in_series(self, price, sanity_check=True):
        if sanity_check:
            self._price_qty_sanity_check()
        return price in self._agg_price_to_qty

    def aggressive_fills(self):
        return self._agg_fills

    def aggressor_fully_filled(self):
        return self._agg_fully_filled

    def passive_fills(self):
        return self._pas_fills

    def aggressing_command(self):
        return self._aggressor

    def run_sanity_checks(self):
        self._fills_sanity_check()
        self._price_qty_sanity_check()
