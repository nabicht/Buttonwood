"""
This file is part of Buttonwood.

Buttonwood is a python software package created to help quickly create, (re)build, or 
analyze markets, market structures, and market participants. 

MIT License

Copyright (c) 2016-2020 Peter F. Nabicht

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
from buttonwood.MarketObjects.Events import OrderEventConstants
from buttonwood.MarketObjects.Events.OrderEvents import CancelCommand
from buttonwood.MarketObjects.Events.OrderEvents import CancelReplaceCommand
from buttonwood.MarketObjects.Events.OrderEvents import NewOrderCommand
from buttonwood.utils.dicts import NDeepDict


class OrderEventCountListener(OrderEventListener):

    # TODO unit test
    # TODO document listener

    # COUNT TYPE
    NEW_ORDER = 1
    ACK = 2
    ACK_NEW_ORDERS = 3
    ACK_CANCEL_REPLACE = 4
    CANCEL_REPLACE = 5
    CANCEL_REQUEST = 6
    CANCEL_CONFIRM = 7
    NEW_FAK = 8
    NEW_FAR = 9
    NEW_FOK = 10
    PARTIAL_FILL = 11
    FULL_FILL = 12
    REJECT = 13
    REJECT_NEW = 14
    REJECT_CANCEL_REPLACE = 15
    REJECT_CANCEL = 16
    NEW_LIMIT = 17
    NEW_MARKET = 18
    FAKS_FULLY_FILLED = 19
    FAKS_PARTIALLY_FILLED = 20
    FOKS_FULLY_FILLED = 21
    FARS_FULLY_FILLED_ON_PLACEMENT = 22
    FARS_PARTIALLY_FILLED_ON_PLACEMENT = 23

    def __init__(self, logger):
        OrderEventListener.__init__(self, logger)
        # storing this market -> user -> count type -> count
        self._event_counts = NDeepDict(3, int)

    def get_count(self, market, user_id, count_type):  # get_count(two_year, "user_a", OrderEventCountListener.NEW_FAK)
        return self._event_counts.get([market, user_id, count_type])

    # REQUESTS / COMMANDS IN ######################################

    def handle_new_order_command(self, new_order_command, resulting_order_chain):
        # to be optionally implemented by child class
        self._event_counts[[new_order_command.market(), new_order_command.user_id(), self.NEW_ORDER]] += 1

        # Time In Force Counts
        if new_order_command.time_in_force() == OrderEventConstants.FAR:
            self._event_counts[[new_order_command.market(), new_order_command.user_id(), self.NEW_FAR]] += 1
        elif new_order_command.time_in_force() == OrderEventConstants.FAK:
            self._event_counts[[new_order_command.market(), new_order_command.user_id(), self.NEW_FAK]] += 1
        elif new_order_command.time_in_force() == OrderEventConstants.FOK:
            self._event_counts[[new_order_command.market(), new_order_command.user_id(), self.NEW_FOK]] += 1

        # Market and limit
        if new_order_command.is_market_order():
            self._event_counts[[new_order_command.market(), new_order_command.user_id(), self.NEW_MARKET]] += 1
        elif new_order_command.is_limit_order():
            self._event_counts[[new_order_command.market(), new_order_command.user_id(), self.NEW_LIMIT]] += 1

    def handle_cancel_replace_command(self, cancel_replace_command, resulting_order_chain):
        self._event_counts[[cancel_replace_command.market(), cancel_replace_command.user_id(), self.CANCEL_REPLACE]] += 1

    def handle_cancel_command(self, cancel_command, resulting_order_chain):
        self._event_counts[[cancel_command.market(), cancel_command.user_id(), self.CANCEL_REQUEST]] += 1

    # RESPONSES / MESSAGES OUT #####################################

    def handle_acknowledgement_report(self, acknowledgement_report, resulting_order_chain):
        self._event_counts[[acknowledgement_report.market(), acknowledgement_report.user_id(), self.ACK]] += 1
        if isinstance(acknowledgement_report.acknowledged_command(), NewOrderCommand):
            self._event_counts[[acknowledgement_report.market(), acknowledgement_report.user_id(), self.ACK_NEW_ORDERS]] += 1
            # if ack comes back for a FAR for a new order, and there is a partial fill in teh orderchain then partially filled on placement
            if resulting_order_chain.time_in_force() == OrderEventConstants.FAR and resulting_order_chain.has_partial_fill():
                self._event_counts[[acknowledgement_report.market(), acknowledgement_report.user_id(), self.FARS_PARTIALLY_FILLED_ON_PLACEMENT]] += 1
        elif isinstance(acknowledgement_report.acknowledged_command(), CancelReplaceCommand):
            self._event_counts[[acknowledgement_report.market(), acknowledgement_report.user_id(), self.ACK_CANCEL_REPLACE]] += 1

    def handle_partial_fill_report(self, partial_fill_report, resulting_order_chain):
        self._event_counts[[partial_fill_report.market(), partial_fill_report.user_id(), self.PARTIAL_FILL]] += 1

    def handle_full_fill_report(self, full_fill_report, resulting_order_chain):
        self._event_countS[[full_fill_report.market(), full_fill_report.user_id(), self.FULL_FILL]] += 1

    def handle_cancel_report(self, cancel_report, resulting_order_chain):
        self._event_counts[[cancel_report.market(), cancel_report.user_id(), self.CANCEL_CONFIRM]] += 1

    def handle_reject_report(self, reject_report, resulting_order_chain):
        self._event_counts[[reject_report.market(), reject_report.user_id(), self.REJECT]] += 1
        if isinstance(reject_report.rejected_command(), NewOrderCommand):
            self._event_counts[[reject_report.market(), reject_report.user_id(), self.REJECT_NEW]] += 1
        elif isinstance(reject_report.rejected_command(), CancelReplaceCommand):
            self._event_counts[[reject_report.market(), reject_report.user_id(), self.REJECT_CANCEL_REPLACE]] += 1
        elif isinstance(reject_report.rejected_command(), CancelCommand):
            self._event_counts[[reject_report.market(), reject_report.user_id(), self.REJECT_CANCEL]] += 1

    # CLOSE OUT THE CHAIN ##########################################

    def handle_chain_close(self, closed_order_chain):
        if closed_order_chain.has_full_fill():
            if closed_order_chain.time_in_force() == OrderEventConstants.FAK:
                self._event_counts[[closed_order_chain.market(), closed_order_chain.user_id(), self.FAKS_FULLY_FILLED]] += 1
            elif closed_order_chain.time_in_force() == OrderEventConstants.FOK:
                self._event_counts[[closed_order_chain.market(), closed_order_chain.user_id(), self.FOKS_FULLY_FILLED]] += 1
            elif closed_order_chain.time_in_force() == OrderEventConstants.FAR:
                # if a FAR has no acknowledgement when fully filled, then it was fully filled on placement
                if not closed_order_chain.has_acknowledgement():
                    self._event_counts[[closed_order_chain.market(), closed_order_chain.user_id(), self.FARS_FULLY_FILLED_ON_PLACEMENT]] += 1
        elif closed_order_chain.has_partial_fill():
            if closed_order_chain.time_in_force() == OrderEventConstants.FAK:
                self._event_counts[[closed_order_chain.market(), closed_order_chain.user_id(), self.FAKS_PARTIALLY_FILLED]] += 1
