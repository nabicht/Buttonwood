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


class OrderEventListener(object):

    def __init__(self, logger):
        self._logger = logger

    # REQUESTS / COMMANDS IN ######################################

    def handle_new_order_command(self, new_order_command, resulting_order_chain):
        """
        The OrderEventListener's call back for being notified of a new order
        command being added to the order chain.

        The resulting_order_chain is the OrderChain object after the
        NewOrderCommand has been applied.

        :param new_order_command: MarketObjects.Events.OrderEvents.NewOrderCommand
        :param resulting_order_chain: MarketObjects.Events.EventChains.OrderEventChain
        """
        # to be optionally implemented by child class
        pass

    def handle_cancel_replace_command(self, cancel_replace_command, resulting_order_chain):
        """
        The OrderEventListener's call back for being notified of a cancel
        replace command being added to the order chain.

        The resulting_order_chain is the OrderChain object after the
        CancelReplaceCommand has been applied.

        :param cancel_replace_command: MarketObjects.Events.OrderEvents.CancelReplaceCommand
        :param resulting_order_chain: MarketObjects.Events.EventChains.OrderEventChain
        """
        # to be optionally implemented by child class
        pass

    def handle_cancel_command(self, cancel_command, resulting_order_chain):
        """
        The OrderEventListener's call back for being notified of a cancel
        command being added to the order chain.

        The resulting_order_chain is the OrderChain object after the
        CancelCommand has been applied.

        :param cancel_command: MarketObjects.Events.OrderEvents.CancelCommand
        :param resulting_order_chain: MarketObjects.Events.EventChains.OrderEventChain
        """
        # to be optionally implemented by child class
        pass

    # RESPONSES / MESSAGES OUT #####################################

    def handle_acknowledgement_report(self, acknowledgement_report, resulting_order_chain):
        """
        The OrderEventListener's call back for being notified of a acknowledgement
        execution report being added to the order chain.

        The resulting_order_chain is the OrderChain object after the
        AcknowledgementReport has been applied.

        :param acknowledgement_report: MarketObjects.Events.OrderEvents.AcknowledgementReport
        :param resulting_order_chain: MarketObjects.Events.EventChains.OrderEventChain
        """
        # to be optionally implemented by child class
        pass

    def handle_partial_fill_report(self, partial_fill_report, resulting_order_chain):
        """
        The OrderEventListener's call back for being notified of a partial fill
        execution report being added to the order chain.

        The resulting_order_chain is the OrderChain object after the
        PartialFillReport has been applied.

        :param partial_fill_report: MarketObjects.Events.OrderEvents.PartialFillReport
        :param resulting_order_chain: MarketObjects.Events.EventChains.OrderEventChain
        """
        # to be optionally implemented by child class
        pass

    def handle_full_fill_report(self, full_fill_report, resulting_order_chain):
        """
        The OrderEventListener's call back for being notified of a full fill
        execution report being added to the order chain.

        The resulting_order_chain is the OrderChain object after the
        FullFillReport has been applied.

        :param full_fill_report: MarketObjects.Events.OrderEvents.FullFillReport
        :param resulting_order_chain: MarketObjects.Events.EventChains.OrderEventChain
        """
        # to be optionally implemented by child class
        pass

    def handle_cancel_report(self, cancel_report, resulting_order_chain):
        """
        The OrderEventListener's call back for being notified of a cancel
        execution report being added to the order chain.

        The resulting_order_chain is the OrderChain object after the
        CancelReport has been applied.

        :param cancel_report: MarketObjects.Events.OrderEvents.CancelReport
        :param resulting_order_chain: MarketObjects.Events.EventChains.OrderEventChain
        """
        # to be optionally implemented by child class
        pass

    def handle_reject_report(self, reject_report, resulting_order_chain):
        """
        The OrderEventListener's call back for being notified of a full fill
        execution report being added to the order chain.

        The resulting_order_chain is the OrderChain object after the
        FullFillReport has been applied.

        :param reject_report: MarketObjects.Events.OrderEvents.RejectReport
        :param resulting_order_chain: MarketObjects.Events.EventChains.OrderEventChain
        """
        # to be optionally implemented by child class
        pass

    # CLOSE OUT THE CHAIN ##########################################

    def handle_chain_close(self, closed_order_chain):
        """
        The OrderEventListener's call back for being notified of a closed order
        chain.

        When the order chain is closed there might be special logic in the
        analytic that needs to run, or at the very least some cleanup that could
        occur.

        :param closed_order_chain: Buttonwood.MarketObjects.Events.EventChains.OrderEventChain
        """
        # to be optionally implemented by child class
        pass

    def clean_up(self, order_chain):
        """
        This is an optional function to be used to clean up memory / data
         structures / etc. when an order_chain is done with.

        The idea is that when a user of the metrics is done with the data for a
         given order_chain, it can call "clean_up" on the listeners and data that
         is no longer needed can be deleted.

        If this function is called before all uses of the OrderEventListener
         are done with the order chain then those uses won't be able to get the
         needed data.

        If a listener tracks data by subchain_id then the cleanup will need to
         go through all subchains in the order chain and do cleanup for each one.

        If an inheritng class of OrderEventListener does not implement this
         function then simply nothing is done to do the clean up.
        
        :param order_chain: Buttonwood.MarketObjects.Events.EventChains.OrderEventChain
        """
        # to be optionally implemented by child class
        pass
