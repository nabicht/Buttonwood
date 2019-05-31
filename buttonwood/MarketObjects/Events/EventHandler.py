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
from buttonwood.MarketObjects.Events.OrderEvents import OrderCommand
from buttonwood.MarketObjects.Events.OrderEvents import ExecutionReport
from buttonwood.MarketObjects.Events.OrderEvents import NewOrderCommand
from buttonwood.MarketObjects.Events.OrderEvents import CancelReplaceCommand
from buttonwood.MarketObjects.Events.OrderEvents import CancelCommand
from buttonwood.MarketObjects.Events.OrderEvents import AcknowledgementReport
from buttonwood.MarketObjects.Events.OrderEvents import RejectReport
from buttonwood.MarketObjects.Events.OrderEvents import PartialFillReport
from buttonwood.MarketObjects.Events.OrderEvents import FullFillReport
from buttonwood.MarketObjects.Events.OrderEvents import CancelReport
from buttonwood.MarketObjects.Events.EventChains import OrderEventChain
from buttonwood.MarketObjects.OrderBooks.BasicOrderBook import BasicOrderBook
from buttonwood.MarketObjects.OrderBooks.OrderLevelBook import AggregateOrderLevelBook
from buttonwood.MarketObjects.Market import Market
from buttonwood.utils.IDGenerators import MonotonicIntID
from collections import OrderedDict
from collections import defaultdict
import logging


class OrderEventHandler:
    def __init__(self, logger):
        self._event_listeners = OrderedDict()
        self._chain_id_to_chain = {}
        self._market_book_id_to_book = {}
        self._market_to_registered_books = defaultdict(set)
        self._logger = logger
        self._sub_chain_id_generator = MonotonicIntID()

    def register_orderbook(self, market, order_book_id, order_book):
        """
        Allows you to register an order book for a market with a given order book identifier. The identifier allows you
        to name the order book so it is easily retrievable later.

        If the orderbook id already exists for the market an error will be thrown with message "<order book id> is
        already registered for <market name>".  This will prevent overriding an order book that has already been
        registered and populated.

        :param market: MarketObjects.Market.Market
        :param order_book_id: str. The human readable, unique identifier for the orderbook
        :param order_book: MarketObjects.OrderBooks.BasicOrderBook
        """
        assert isinstance(order_book, BasicOrderBook)
        assert isinstance(market, Market)
        assert isinstance(order_book_id, str)

        if isinstance(order_book, AggregateOrderLevelBook):
            for component_order_book in order_book.component_books():
                comp_book_id = "%s Component Book (%s)" % (order_book_id, str(component_order_book.market()))
                self.register_orderbook(component_order_book.market(), comp_book_id, component_order_book)

        if market not in self._market_book_id_to_book:
            self._market_book_id_to_book[market] = {}
        if order_book_id not in self._market_book_id_to_book[market]:
            self._market_book_id_to_book[market][order_book_id] = order_book
        else:
            raise Exception("%s is already registered for %s" % (order_book_id, str(market)))
        self._market_to_registered_books[market].add(order_book)

    def order_book(self, market, order_book_id):
        if market in self._market_book_id_to_book:
            return self._market_book_id_to_book[market].get(order_book_id)
        return None

    def register_event_listener(self, event_listener_id, event_listener):
        """
        Registers and event listener with the given event listener identifier. The event listener identifier allos you
        to name the event listener so it is easily retrievable later.

        If the event listener identifier already exists then an error will be thrown with the message "<event listener
        id> is already registered". This will prevent overriding a listener that has already been
        registered and used.

        The order the event listeners are registered is also the order that they are updated in.

        :param event_listener_id: String. The human readable, unique identifier for the event listener.
        :param event_listener: Buttonwood.MarketObjects.OrderEventListener.OrderEventListener
        """
        assert isinstance(event_listener_id, str)
        assert isinstance(event_listener, OrderEventListener)

        # if the eventlistener that is passed in is an orderbook then WARN the user
        if isinstance(event_listener, BasicOrderBook):
            self._logger.warning(
                "Registering OrderBook as an EventListener! Much downstream logic depends on EventListeners being updated before OrderBooks.")
        if event_listener_id not in self._event_listeners:
            self._event_listeners[event_listener_id] = event_listener
            self._logger.info("Registered OrderEventListener: '%s': %s" %
                              (event_listener_id, event_listener.__class__.__name__))
        else:
            raise Exception("%s is already registered" % event_listener_id)

    def event_listener(self, event_listener_id):
        """
        Gets the event listener that has been registered wih the passed in id. If the event_listener_id has not been
         registered it will return 100
         
        :param event_listener_id: 
        :return: Buttonwood.MarketObjects.EventListeners.EventListener 
        """
        return self._event_listeners.get(event_listener_id)

    def process(self, event):
        # even though there might not be a handler that is set to debug, the string gets formatted either way,
        #  which is particularly expensive since str(event) actually formats JSON. Thus, the extra level of DEBUG check.
        if logging.DEBUG >= self._logger.getEffectiveLevel():
            self._logger.debug("%s: Processing chain %s event %s: %s" %
                               (self.__class__.__name__, str(event.chain_id()), str(event.event_id()), str(event)))
        order_chain, updated_markets = self._handle_event(event)
        return order_chain, updated_markets

    def _create_new_event_chain(self, new_order_command):
        order_chain = OrderEventChain(new_order_command, self._logger,
                                      subchain_id_generator=self._sub_chain_id_generator)
        return order_chain

    def _handle_new_order_command(self, new_order_command):
        chain_id = new_order_command.chain_id()
        if self._chain_id_to_chain.get(chain_id) is not None:
            chain_id = new_order_command.chain_id()
            self._logger.error("%s: %s for already existing OrderChain %s" %
                               (self.__class__.__name__,
                                new_order_command.event_type_str(),
                                str(self._chain_id_to_chain.get(chain_id))))
        else:
            order_chain = self._create_new_event_chain(new_order_command)
            self._chain_id_to_chain[chain_id] = order_chain
            self._new_order_command_notification(new_order_command, order_chain)

    def _handle_cancel_replace_command(self, cancel_replace_command):
        chain_id = cancel_replace_command.chain_id()
        order_chain = self._chain_id_to_chain.get(chain_id)
        if order_chain is None:
            self._logger.error("%s: Cannot Handle. No OrderChain %s for %s" %
                               (self.__class__.__name__,
                                str(chain_id),
                                cancel_replace_command.event_type_str()))
            return
        order_chain.apply_cancel_replace_command(cancel_replace_command)
        self._cancel_replace_command_notification(cancel_replace_command, order_chain)

    def _handle_cancel_command(self, cancel_command):
        chain_id = cancel_command.chain_id()
        order_chain = self._chain_id_to_chain[chain_id]
        if order_chain is None:
            self._logger.error("%s: Cannot Handle. No OrderChain %s for %s" %
                               (self.__class__.__name__,
                                str(chain_id),
                                cancel_command.event_type_str()))
            return
        order_chain.apply_cancel_command(cancel_command)
        self._cancel_command_notification(cancel_command, order_chain)

    def _handle_acknowledgement_report(self, acknowledgement_report, order_chain):
        order_chain.apply_acknowledgement_report(acknowledgement_report)
        self._acknowledgement_report_notification(acknowledgement_report, order_chain)

    def _handle_reject_report(self, reject_report, order_chain):
        order_chain.apply_reject_report(reject_report)
        self._reject_report_notification(reject_report, order_chain)

    def _handle_cancel_report(self, cancel_report, order_chain):
        order_chain.apply_cancel_report(cancel_report)
        self._cancel_report_notification(cancel_report, order_chain)

    def _handle_partial_fill_report(self, partial_fill_report, order_chain):
        order_chain.apply_partial_fill_report(partial_fill_report)
        self._partial_fill_report_notification(partial_fill_report, order_chain)

    def _handle_full_fill_report(self, full_fill_report, order_chain):
        order_chain.apply_full_fill_report(full_fill_report)
        self._full_fill_report_notification(full_fill_report, order_chain)

    def _apply_to_orderbooks(self, event, order_chain):
        markets_updated = set()
        if order_chain is not None:
            market = event.market()
            if market in self._market_to_registered_books:
                for order_book in self._market_to_registered_books[market]:
                    self._logger.debug("%s: applying %s chain %s event %s to orderbook %s" %
                                       (self.__class__.__name__,
                                        event.__class__.__name__,
                                        str(event.chain_id()),
                                        str(event.event_id()),
                                        order_book.name()))
                    order_book_updated = False
                    if isinstance(event, AcknowledgementReport):
                        order_book_updated, tob_updated = order_book.handle_acknowledgement_report(event, order_chain)
                    elif isinstance(event, CancelReport):
                        order_book_updated, tob_updated = order_book.handle_cancel_report(event, order_chain)
                    elif isinstance(event, PartialFillReport):
                        order_book_updated, tob_updated = order_book.handle_partial_fill_report(event, order_chain)
                    elif isinstance(event, FullFillReport):
                        order_book_updated, tob_updated = order_book.handle_full_fill_report(event, order_chain)
                    else:
                        self._logger.warning("%s: don't know how to handle %s when applying to order book." %
                                             (self.__class__.__name__, event.__class__.__name__))
                    if order_book_updated:
                        markets_updated.add(market)
        return markets_updated

    def _handle_event(self, event):
        """
        A clearing house that takes in an event, figures out what the event is, apply them to the correct order chain,
         and update the correct order book(s) if the event impacts the order book.

        Returns a tuple of the updated data: the order chain and an iterable of markets that had updated order books.

        :param event: Buttonwood.MarketObjects.Events.OrderEvent
        :return: (Buttonwood.MarketObjects.Events.EventChains.OrderEventChain, set of markets)
        """
        # while the command vs execution report check seems unnecessary,
        # it prevents execution reports from having to be checked for each Command
        is_closed_before = False
        is_closed_after = False
        chain_id = event.chain_id()
        markets_with_updated_books = set()
        if isinstance(event, OrderCommand):
            # order is such because in most markets I expect New, than Replace, then cancel in that order
            if isinstance(event, NewOrderCommand):
                # should have been no order_chain if there was a NewOrderCommand, so need to set it
                self._handle_new_order_command(event)
            elif isinstance(event, CancelReplaceCommand):
                self._handle_cancel_replace_command(event)
            elif isinstance(event, CancelCommand):
                self._handle_cancel_command(event)
            else:
                self._logger.error("%s: Cannot handle unknown OrderCommand: %s" %
                                   (self.__class__.__name__,
                                    event.__class__.__name__))
        elif isinstance(event, ExecutionReport):
            order_chain = self._chain_id_to_chain.get(chain_id)
            if order_chain is None:
                self._logger.warning("%s: Cannot Handle. No OrderChain %s for %s" %
                                     (self.__class__.__name__,
                                      str(chain_id),
                                      event.event_type_str()))
                return
            # closes can only happen as result of an ExecutionReport
            is_closed_before = not order_chain.is_open()
            # the ordering is because I expect to see more Acks, cancel confirms, then partial fills, then full fills, then rejects in most markets
            if isinstance(event, AcknowledgementReport):
                self._handle_acknowledgement_report(event, order_chain)
            elif isinstance(event, CancelReport):
                self._handle_cancel_report(event, order_chain)
            elif isinstance(event, PartialFillReport):
                self._handle_partial_fill_report(event, order_chain)
            elif isinstance(event, FullFillReport):
                self._handle_full_fill_report(event, order_chain)
            elif isinstance(event, RejectReport):
                self._handle_reject_report(event, order_chain)
            else:
                self._logger.error("%s: Cannot handle unknown ExecutionReport: %s" %
                                   (self.__class__.__name__,
                                    event.__class__.__name__))
                return None, markets_with_updated_books
            is_closed_after = not order_chain.is_open()

            # apply to the registered order book (if one is registered)
            # only execution reports impact an order book so only applying to order book here
            markets_with_updated_books = self._apply_to_orderbooks(event, order_chain)
        else:
            self._logger.error("%s: Cannot handle unknown Event: %s" %
                               (self.__class__.__name__,
                                event.__class__.__name__))
            return None, markets_with_updated_books

        # order_chain close notifications
        order_chain = self._chain_id_to_chain.get(chain_id)
        if order_chain is not None and not is_closed_before and is_closed_after:
            self._close_chain_notification(order_chain)
            # if closed then no longer need to keep it in map:
            del self._chain_id_to_chain[chain_id]
        return order_chain, markets_with_updated_books

    def _new_order_command_notification(self, new_order_command, resulting_order_chain):
        for listener in self._event_listeners.itervalues():
            listener.handle_new_order_command(new_order_command, resulting_order_chain)

    def _cancel_replace_command_notification(self, cancel_replace_command, resulting_order_chain):
        for listener in self._event_listeners.itervalues():
            listener.handle_cancel_replace_command(cancel_replace_command, resulting_order_chain)

    def _cancel_command_notification(self, cancel_command, resulting_order_chain):
        for listener in self._event_listeners.itervalues():
            listener.handle_cancel_command(cancel_command, resulting_order_chain)

    def _acknowledgement_report_notification(self, acknowledgement_report, resulting_order_chain):
        for listener in self._event_listeners.itervalues():
            listener.handle_acknowledgement_report(acknowledgement_report, resulting_order_chain)

    def _partial_fill_report_notification(self, partial_fill_report, resulting_order_chain):
        for listener in self._event_listeners.itervalues():
            listener.handle_partial_fill_report(partial_fill_report, resulting_order_chain)

    def _full_fill_report_notification(self, full_fill_report, resulting_order_chain):
        for listener in self._event_listeners.itervalues():
            listener.handle_full_fill_report(full_fill_report, resulting_order_chain)

    def _cancel_report_notification(self, cancel_report, resulting_order_chain):
        for listener in self._event_listeners.itervalues():
            listener.handle_cancel_report(cancel_report, resulting_order_chain)

    def _reject_report_notification(self, reject_report, resulting_order_chain):
        for listener in self._event_listeners.itervalues():
            listener.notify_reject_reort(reject_report, resulting_order_chain)

    def _close_chain_notification(self, closed_order_chain):
        if closed_order_chain.is_open():
            self._logger.error("%s: _close_chain_notification called for order chain %s and it is NOT closed! Not notifying listeners." %
                               (self.__class__.__name__, str(closed_order_chain.chain_id())))
            return
        for listener in self._event_listeners.itervalues():
            listener.handle_chain_close(closed_order_chain)

    def chain_ids(self):
        return self._chain_id_to_chain.keys()

    def order_chain(self, chain_id):
        return self._chain_id_to_chain.get(chain_id)
