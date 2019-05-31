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

from collections import defaultdict
from buttonwood.MarketObjects.EventListeners.OrderEventListener import OrderEventListener


class VolumeTracker(object):

    def __init__(self):
        self._counterparty_to_passive_volume = defaultdict(lambda: 0)
        self._counterparty_to_aggressive_volume = defaultdict(lambda: 0)

    def add_passive_trade(self, volume, counterparty):
        self._counterparty_to_passive_volume[counterparty] += volume

    def add_aggressive_trade(self, volume, counterparty):
        self._counterparty_to_aggressive_volume[counterparty] += volume

    def total_aggressive_volume_with(self, counterparty):
        return self._counterparty_to_aggressive_volume[counterparty]

    def total_passive_volume_with(self, counterparty):
        return self._counterparty_to_passive_volume[counterparty]

    def total_volume_with(self, counterparty):
        return self.total_passive_volume_with(counterparty) + self.total_aggressive_volume_with(counterparty)

    def total_aggressive_volume(self):
        total_volume = 0
        for volume in self._counterparty_to_aggressive_volume.itervalues():
            total_volume += volume
        return total_volume

    def total_passive_volume(self):
        total_volume = 0
        for volume in self._counterparty_to_passive_volume.itervalues():
            total_volume += volume
        return total_volume

    def total_volume(self):
        return self.total_passive_volume() + self.total_aggressive_volume()


class VolumeTrackingListener(OrderEventListener):

    def __init__(self, logger):
        OrderEventListener.__init__(self, logger)
        self._market_to_participant_to_volume = defaultdict(lambda: defaultdict(VolumeTracker()))  # TODO can I use NDeep dict here?

    def _handle_fill(self, fill_report):
        # only care about passive fill reports because that way we get both counterparties:
        #  1) the user getting filled here and
        #  2) the user on the aggressive command
        if not fill_report.is_aggressor():
            passive_user = fill_report.user()
            aggressive_user = fill_report.aggressing_command().user()
            qty = fill_report.fill_qty()
            market = fill_report.market()
            self._market_to_participant_to_volume[market][passive_user].add_passive_trade(qty, aggressive_user)
            self._market_to_participant_to_volume[market][aggressive_user].add_aggressive_trade(qty, passive_user)

    def handle_partial_fill_report(self, partial_fill_report, resulting_order_chain):
        self._handle_fill(partial_fill_report)

    def handle_full_fill_report(self, full_fill_report, resulting_order_chain):
        self._handle_fill(full_fill_report)
