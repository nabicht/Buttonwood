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

from buttonwood.MarketObjects.EventListeners.OrderEventListener import OrderEventListener
from buttonwood.MarketObjects.MatchSeries import MatchSeries


class MatchSeriesTracker(OrderEventListener):

    def __init__(self, logger):
        OrderEventListener.__init__(self, logger)
        self._aggressor_event_id_to_series = {}
        self._id_to_series = {}
        self._fill_event_id_to_series = {}

    def _handle_fill(self, fill):
        series = self._id_to_series.get(fill.match_id())
        if series is None:
            series = MatchSeries(fill.match_id())
            series.add_fill(fill)
            self._id_to_series[fill.match_id()] = series
            self._aggressor_event_id_to_series[fill.aggressing_command().event_id()] = series
            self._fill_event_id_to_series[fill.event_id()] = series
        else:
            series.add_fill(fill)
            self._fill_event_id_to_series[fill.event_id()] = series

    def match_ids(self):
        return self._id_to_series.keys()

    def handle_partial_fill_report(self, partial_fill_report, resulting_order_chain):
        self._handle_fill(partial_fill_report)

    def handle_full_fill_report(self, full_fill_report, resulting_order_chain):
        self._handle_fill(full_fill_report)

    def match_series(self, match_id):
        """
        Get the MatchSeries for the given match_id. Can be None if unknown match_id.
        
        :param match_id: unique identifier of MatchSeries 
        :return: Buttonwood.MarketObjects.MatchSeries.MatchSeries
        """
        return self._id_to_series.get(match_id)

    def match_series_for_side(self, side):
        """
        Returns a list of all MatchSeries that had an aggressive side that matches the passed in side
        
        :param side: Buttonwood.MarketObjects.Side.Side
        :return: list() of Buttonwood.MarketObjects.MatchSeries.MatchSeries
        """
        l = []
        for series in self._id_to_series.itervalues():
            if series.aggressor_side() == side:
                l.append(series)
        return l

    def aggressor_match_series(self, aggressor_event_id):
        """
        Return the match series for a given aggressor event id. It will return None if aggressor_event_id is not known.
        
        :param aggressor_event_id: unique identifier of the aggressor event 
        :return: Buttonwood.MarketObjects.MatchSeries.MatchSeries
        """
        return self._aggressor_event_id_to_series.get(aggressor_event_id)

    def fill_event_id_match_series(self, fill_event_id):
        """
        Return the match series for a given fill event id. It will be return None if the fill event id is not known.
        
        :param fill_event_id: unique identifier of the fille vent 
        :return: Buttonwood.MarketObjects.MatchSeries.MatchSeries
        """
        return self._fill_event_id_to_series.get(fill_event_id)
