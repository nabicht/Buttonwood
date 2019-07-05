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

from buttonwood.MarketObjects.Events import OrderEventConstants
from buttonwood.MarketObjects.Events.OrderEvents import AcknowledgementReport
from buttonwood.MarketObjects.Events.OrderEvents import CancelCommand
from buttonwood.MarketObjects.Events.OrderEvents import CancelReplaceCommand
from buttonwood.MarketObjects.Events.OrderEvents import CancelReport
from buttonwood.MarketObjects.Events.OrderEvents import ExecutionReport
from buttonwood.MarketObjects.Events.OrderEvents import FullFillReport
from buttonwood.MarketObjects.Events.OrderEvents import NewOrderCommand
from buttonwood.MarketObjects.Events.OrderEvents import PartialFillReport
from buttonwood.MarketObjects.Events.OrderEvents import RejectReport
from buttonwood.utils.IDGenerators import IDGenerator

import logging
import json


class CancelReplaceInfo(object):
    # TODO document class
    # TODO unit test

    def __init__(self, previous_exposure, new_exposure, side, market):
        self._prev = previous_exposure
        self._new = new_exposure
        mpi = market.product().mpi()
        if side.is_bid():
            self._price_delta = (self._new.price() - self._prev.price()) / mpi
        else:
            self._price_delta = (self._prev.price() - self._new.price()) / mpi
        self._qty_delta = new_exposure.qty() - previous_exposure.qty()

    def previous_exposure(self):
        return self._prev

    def new_exposure(self):
        return self._new

    def is_price_change(self):
        return self._price_delta != 0

    def is_better_price(self):
        return self._price_delta > 0

    def is_worse_price(self):
        return self._price_delta < 0

    def is_qty_change(self):
        return self._qty_delta != 0

    def is_qty_increase(self):
        return self._qty_delta > 0

    def is_qty_decrease(self):
        return self._qty_delta < 0

    def price_delta(self):
        return self._price_delta

    def qty_delta(self):
        return self._qty_delta


class Exposure(object):
    # TODO document this class

    def __init__(self, price, qty, causing_event_id):
        self._price = price
        self._qty = qty
        self._causing_event_id = causing_event_id

    def price(self):
        return self._price

    def qty(self):
        return self._qty

    def dec_qty(self, dec_amount):
        assert dec_amount > 0, "Must decrement qty with a positive integer."
        self._qty -= dec_amount

    def causing_event_id(self):
        return self._causing_event_id

    def equivalent_exposure(self, other):
        """
        This is to test that one exposure is equivalent to another. equivalent
         exposure is when the exposures are for the same price and the same qty.

        Not using __eq__ here because it does not matter if the causing_event_id
         is the same. So, equal exposures are equivalent but not all equivalent
         exposures are equal.

        If other is not an Exposure object then returns False.

        :param other: MarketObjects.Events.EventChains.Exposure
        :return: bool
        """
        if isinstance(other, Exposure):
            return self.price() == other.price() and self.qty() == other.qty()
        else:
            return False

    def __str__(self):
        return "%s: %d @ %s" % (str(self.causing_event_id()), self.qty(), str(self.price()))

    def __eq__(self, other):
        return self.price() == other.price() and \
               self.qty() == other.qty() and \
               self.causing_event_id() == other.causing_event_id()


class SubChain(object):
    # OPEN & CLOSE REASONS
    NEW_ORDER = 10  # open
    CANCEL_REPLACE_INCREASE_QTY = 20  # open and close
    CANCEL_REPLACE_PRICE = 30  # open and close
    CANCEL = 50  # close
    REJECT = 60  # close
    FULLY_FILLED = 70  # close
    CANCEL_REPLACE_TO_ZERO = 80  # close

    def __init__(self, subchain_id, open_event, open_reason, logger):
        """
        Subchain objects track the data around a subchain, including all the events, the open reason and the close
         reason.

        The open reasons are:
          * New Order
          * Cancel Replace to a different price
          * Cancel Replace that increases the open qty

        The close reasons are anything that opens a new subchain or closes out the entire order chain:
          * Cancel replace to a different price
          * Cancel Replace that increases qty
          * Cancel Report
          * Fully Filled

        In the event that a cancel replace changes price and increases quantity, the change in price should take
         precedent as to the reason for the open or close

        :param subchain_id:
        :param open_event:
        :param open_reason:
        """
        self._logger = logger
        try:
            self._debug = debug_logging
        except NameError:
            global debug_logging
            debug_logging = self._debug = self._logger.isEnabledFor(logging.DEBUG)
        self._chain_id = open_event.chain_id()
        self._events = [open_event]
        self._open_reason = open_reason
        self._close_reason = None
        self._close_event = None
        self._subchain_id = subchain_id
        if self._debug:
            self._logger.debug("OrderChain %s: Created new SubChain %s" % (self._chain_id, self.subchain_id()))

    def add_event(self, event):
        if not self.is_open():
            raise Exception("Adding event to closed Subchain. EventID %s, Chain %s, SubChain %s" %
                            event.event_id(), event.chain_id(), self._subchain_id)
        if self._debug:
            self._logger.debug("OrderChain %s: Add %s %s to SubChain %s" %
                               (self._chain_id, event.event_type_str(), event.event_id(),
                                self.subchain_id()))
        self._events.append(event)

    def close_subchain(self, close_reason):
        if self.is_open():
            self._close_event = close_reason
        else:
            raise Exception("Closing an already closed subchain: %s" % str(self.subchain_id()))

    def open_event(self):
        return self._events[0]

    def events(self):
        return self._events

    def is_open(self):
        return self._close_reason is None

    def chain_id(self):
        return self._chain_id

    def subchain_id(self):
        return self._subchain_id


class OrderEventChain(object):
    def __init__(self, new_order_command, logger, subchain_id_generator):
        """
        OrderEventChain is data structure to track a complete chain of events that concern one order. This includes
         Commands, such as:
          * New Order
          * Cancel Replace
          * Cancel Request

        and Execution Reports, such as:
          * Acknowledgement
          * Reject
          * Partial Fill
          * Full Fill
          * Cancel Confirm

        Each Command should have at least one ExecutionReport and can have more.  Also, there can be Execution Reports
         that were not caused by a Command in the OrderEventChain, such as a fill that results from another order being
         the aggressor

        All Order Events in the OrderEventChain will share the same Chain ID.

        Further assumptions are made about all events in the same OrderEventChain:
          * For the same product
          * For the same side of the book
          * Events are in chronological order
          * Time in force (ex: FAK, FAR, or FOK) does not change
          * Order type (ex: market or limit) does not change

        An OrderEventChain also tracks subchains. Subchains are individual stretches of desired liquidity
         within an EventOrderChain. A new subchain is created with every user caused change in priority, assuming a
         standard order book. Changes in priority are triggered by:
          * New Order
          * Cancel Replace to a new price
          * Cancel Replace that increases the visible exposure (visible quantity), whether or not the price changes

        A subchain is closed by either the opening of a new subchain (a cancel replace to new price or up in visilbe
         quantity) or by the closing of the entire order chain (a Full Fill or a Cancel Confirm).

        Since matching engines do not typically track subchains or uniquely identify them, unique identifers have to
         be applied here. The passed in instance of IDGenerator will do this creation of IDs.

        :param new_order_command: MarketObjects.Events.OrderEvents.NewOrderCommand. NewOrderCommand that starts the chain.
        :param logger: logger.
        :param subchain_id_generator: the IDGenerator to be used for creating subchain_IDs
        """
        assert isinstance(new_order_command, NewOrderCommand)
        assert isinstance(subchain_id_generator, IDGenerator)
        self._logger = logger  # TODO add debug logging throughout
        try:
            self._debug = debug_logging
        except NameError:
            global debug_logging
            debug_logging = self._debug = self._logger.isEnabledFor(logging.DEBUG)

        # keeping this state local, rather than looking it up in self._new_order_command all the time speeds things up
        #  (only doing it for a select few that tend to get called more than others)
        self._chain_id = new_order_command.chain_id()
        self._user_id = new_order_command.user_id()
        self._side = new_order_command.side()

        self._new_order_command = new_order_command
        self._subchain_id_generator = subchain_id_generator

        # requested_exposures is a list in order of Exposure that has been requested by a Command but hasn't been
        #  acked, so isn't real exposure yet as it might not get acked. Will be None if no outstanding, unack'd request.
        self._requested_exposures = [Exposure(new_order_command.price(),
                                              new_order_command.qty(),
                                              new_order_command.event_id())
                                     ]

        # current_exposure is orderchain's currently open qty at price
        #  if no currently acknowledgments so no open exposure.
        self._current_exposure = None

        # add to list of events
        self._events = [new_order_command]
        self._filled_price_to_qty = defaultdict(int)
        if self._debug:
            self._logger.debug("New %s created, OrderChainID %s Market %s" %
                               (self.__class__.__name__, str(self._chain_id), str(self.market())))
        # New Orders start new subchains, so start subchain and put it in list of subchains
        self._sub_chains = []
        self._visible_qty = 0  # an unack'd order has no qty showing on the book
        self._iceberg_peak_qty = new_order_command.iceberg_peak_qty()
        self._open = True
        self._event_id_to_cancel_replace_info = {}
        self._events_that_caused_visible_qty_refresh = set()
        self._price_at_close = None  # starts as none because this doesn't get populated until it is closed
        self._open_qty_at_close = None  # starts as none because isn't populated until it is closed
        self._match_ids = set()  # unique negotation ids that the order chain is part of

    def new_order_command(self):
        """
        Gets the NewOrderCommand that started the order chain

        :return: MarketObjects.Events.OrderEvents.NewOrderCommand
        """
        return self._new_order_command

    def chain_id(self):
        return self._chain_id

    def user_id(self):
        return self._user_id

    def visible_qty(self):
        # TODO document
        return self._visible_qty

    def hidden_qty(self):
        # TODO document
        # TODO unit test
        return self.current_qty() - self.visible_qty()

    def iceberg_peak_qty(self):
        # TODO document
        return self._iceberg_peak_qty

    def side(self):
        """
        Gets the Product of the OrderEventChain

        :return: MarketObjects.Side.Side
        """
        return self._side

    def is_limit_order(self):
        """
        Returns True if the order chain is for a limit order; false if it is not.

        :return: bool
        """
        return self.new_order_command().is_limit_order()

    def is_market_order(self):
        """
        Returns True if the new order is a market order; false if it is not.

        :return: bool
        """
        return self.new_order_command().is_market_order()

    def product(self):
        """
        Gets the Product of the OrderEventChain

        :return: MarketObjects.Product.Product
        """
        return self._new_order_command.market().product()

    def market(self):
        """
        Gets the Market of the OrderEventChain

        :return: MarketObjects.Market.Market
        """
        return self._new_order_command.market()

    def time_in_force(self):
        """
        Gets the Time in Force of the OrderEventChain

        :return: int
        """
        return self._new_order_command.time_in_force()

    def is_far(self):
        """
        True if the time in force of the chain is FAR

        :return: bool
        """
        return self._new_order_command.is_far()

    def is_fak(self):
        """
        True if the time in force of the chain is FAK

        :return: bool
        """
        return self._new_order_command.is_fak()

    def is_fok(self):
        """
        True if the time in force of the chain is FOK

        :return: bool
        """
        return self._new_order_command.is_fok()

    def current_exposure(self):
        """
        Gets the current exposed (ie. acknowledged) pricelevel . If no exposure then returns None.

        :return: MarketObjects.PriceLevel.PriceLevel Could be None.
        """
        return self._current_exposure if self.current_exposure is not None else None

    def current_price(self):
        """
        Gets the currently acknowledged price.

        This is a helper function that is the same as self.current_exposure().price()

        :return: MarketObjects.Price.Price. Can be None
        """
        return self.current_exposure().price() if self.current_exposure() is not None else None

    def current_qty(self):
        """
        Gets the currently acknowledged qty.

        This is a helper function that is the same as self.current_exposure().qty(), returns 0 if current_exposure() is
         None

        :return: int. Can be None
        """
        return self.current_exposure().qty() if self.current_exposure() is not None else 0

    def most_recent_requested_exposure(self):
        """
        Gets the most recently requested exposure that has not been acknowledged. If no unacknowledged exposure requests
         then returns None
        :return: MarketObjects.PriceLevel.PriceLevel Could be None.
        """
        return None if len(self._requested_exposures) == 0 else self._requested_exposures[-1]

    def open_exposure_requests(self):
        return self._requested_exposures

    def events(self):
        """
        Gets the Event objects in the OrderChain in order of occurrence.

        :return: list of MarketObjects.Events.OrderEvents.OrderEvent
        """
        return self._events

    def most_recent_event(self):
        """
        Gets the most recent OrderEvent in the OrderEventChain.

        :return:  MarketObjects.Events.OrderEvents.OrderEvent
        """
        return self._events[-1]

    def last_update_time(self):
        """
        Gets the last time that the chain was updated (the time of the chain's last event).

        :return: float
        """
        return self._events[-1].timestamp()

    def most_recent_subchain(self):
        """
        Gets the most recent subchain in the OrderEventChain.

        Returns None if no subchains yet (which happens if no execution reports yet)

        :return:  MarketObjects.Events.EventChains.SubChain. Can be None.
        """
        return None if len(self._sub_chains) == 0 else self._sub_chains[-1]

    def subchains(self):
        """
        Returns the in-order list of subchains in the OrderEventChain.

        :return: list of MarketObjects.Events.EventChains.SubChain
        """
        return self._sub_chains

    def has_full_fill(self):
        """
        Determines if the orderchain contains a full fill

        :return: Bool, True if has FullFillReport, False otherwise
        """
        # since a full fill should be at end of event chain, more efficient to go backwards
        for event in reversed(self._events):
            if isinstance(event, FullFillReport):
                return True
        return False

    def match_ids(self):
        """
        Returns a set of the IDs of all the negotations that the order chain is
         part of.

        :return: set() of match ids
        """
        return self._match_ids

    def is_open(self):
        """
        Returns whether or not the order event chain is open. An event chain is open if it is still has exposure in the
         market. This means it has not received a Cancel Report, Full Fill Report, or has an any way had its qty set to
         0.
        :return:
        """
        return self._open

    def has_partial_fill(self):
        """
        Determines if the orderchain contains a partial fill

        :return: Bool, True if has PartialFillReport, False otherwise
        """
        for event in self._events:
            if isinstance(event, PartialFillReport):
                return True
        return False

    def has_acknowledgement(self):
        """
        Determines if the orderchain contains an acknowledgement

        :return: Bool, True if has AcknowledgementReport, False otherwise
        """
        for event in self._events:
            if isinstance(event, AcknowledgementReport):
                return True
        return False

    def last_acknowledgement(self):
        """
        Gets the last acknowledgement in the order chain. Can be None.

        :return: Buttonwood.MarketObjects.Price.Price (can be None)
        """
        for event in reversed(self._events):
            if isinstance(event, AcknowledgementReport):
                return event
        return None

    def caused_visible_qty_refresh(self, event_id):
        """
        Is the event one that caused a refresh of the visible qty?

        :param event_id: unique identifier of event
        :return: bool
        """
        return event_id in self._events_that_caused_visible_qty_refresh

    def find_requested_exposure(self, causing_event_id):
        """
        For a given event this returns the events requested exposure.

        This can be None if the event did not result in a new requested exposure.

        :param causing_event_id: unique identifier of event.
        :return: Exposure. (or None)
        """
        for exposure in self._requested_exposures:
            if exposure.causing_event_id() == causing_event_id:
                return exposure
        return None

    def cancel_replace_information(self, ack_event_id):
        """
        Cancel replace history kept for the ack of the cancel replace, so the
         event id passed in needs to be for an ack of a cancel replace. If it
         isn't then None will be returned.

        :param ack_event_id: unique identifier of the ack event
        :return: Bool. Can be None.
        """
        return self._event_id_to_cancel_replace_info.get(ack_event_id)

    def price_at_close(self):
        """
        The price of the chain at the time it was closed.

        Can be None for the following reasons:
         1) order event chain is not closed yet
         2) order was fully filled, so no exposure left, thus no price.
        """
        return self._price_at_close

    def open_qty_at_close(self):
        """
        The open qty of the chain at the time it was closed.

        Can be None for the following reasons:
         1) order event chain is not closed yet
         2) order was fully filled, so no exposure left, thus no price.
        """
        return self._open_qty_at_close

    # TODO track qty remaining at close

    def __str__(self):
        s = ""
        for event in self._events:
            event_json = event.to_json()
            s += json.dumps(event_json) + "\n"
        s += "\n%s: %s %s %s %d (%d) @ %s" % \
             (str(self._chain_id), self.user_id(), str(self.market()), self.side(), self.visible_qty(),
              self.current_qty() - self.visible_qty(), str(self.current_price()))
        return s

    ############################################################################
    # Functions for updating the OrderEventChain  ##############################
    ############################################################################

    def _close_chain(self, closing_event):
        # TODO unit test!
        if self._current_exposure is not None and self._current_exposure.qty() > 0:
            self._price_at_close = self.current_exposure().price()
            self._open_qty_at_close = self.current_exposure().qty()
        else:  # for example, FAKs and other aggressive orders that get cancelled without an acknowledgement
            self._price_at_close = self.most_recent_requested_exposure().price()
            self._open_qty_at_close = self.most_recent_requested_exposure().qty()
        self._open = False
        self._visible_qty = 0
        # wipe out current exposure
        self._current_exposure = Exposure(None, 0, closing_event.event_id())
        # close out exposures
        self._requested_exposures = []

    def _close_requested_exposure(self, execution_report):
        """
        Close the exposure the execution_report is for

        :param execution_report:
        :return:
        """
        assert execution_report is not None, \
            "execution_report must be a valid ExecutionReport instance"
        assert isinstance(execution_report, ExecutionReport), \
            "execution_report must be a valid ExecutionReport instance"
        # partial fills can't close out exposure
        assert not isinstance(execution_report,
                              PartialFillReport), "PartialFillReports cannot close requested exposure."
        closed_exposure = False
        # if execution_report is a cancel confirm or full fill then close out all open requested exposures
        if isinstance(execution_report, CancelReport) or isinstance(execution_report, FullFillReport):
            self._requested_exposures = []  # TODO unit test this
            closed_exposure = True
        # if execution_report is an ack or a reject then close out the correct
        elif isinstance(execution_report, AcknowledgementReport) or isinstance(execution_report, RejectReport):
            response_to_event_id = execution_report.causing_command().event_id()
            # go through the open exposures and when/if we find the causing command event id, remove it
            index_to_remove = -1
            for i, requested_exposure in enumerate(self._requested_exposures):
                if requested_exposure.causing_event_id() == response_to_event_id:
                    # found it, so set the index for removal and since should only exist once, break the loop
                    index_to_remove = i
                    break
            del self._requested_exposures[index_to_remove]
            closed_exposure = True
        return closed_exposure

    def _close_current_subchain(self, subchain_close_reason):
        self.most_recent_subchain().close_subchain(subchain_close_reason)

    def _open_new_subchain(self, opening_cmd, open_reason):
        new_subchain = SubChain(self._subchain_id_generator.id(), opening_cmd, open_reason, self._logger)
        self._sub_chains.append(new_subchain)

    def apply_acknowledgement_report(self, ack):
        """
        Apply an acknowledgement to the OrderEventChain.

        :param ack: MarketObjects.Events.OrderEvents.AcknowledgementReport
        """
        ack_chain_id = ack.chain_id()
        ack_cmd = ack.acknowledged_command()
        assert isinstance(ack, AcknowledgementReport)
        assert ack.market() == self.market(), \
            "Acknowledgement does NOT have same market as the OrderEventChain expects"
        assert ack_chain_id == self._chain_id, \
            "Acknowledgement's chain ID (%s) does not match chain's ID (%s)" % (ack_chain_id, self._chain_id)
        assert ack_cmd.chain_id() == ack_chain_id, \
            "Acknowledgements should have the same chain id as the command they are in response to."

        # append the ack to the underlying list of events
        self._events.append(ack)
        # close out the open exposure the ack is for
        if not self._close_requested_exposure(ack):
            raise Exception("Received an acknowledgement for event id %s but that event is not open in the chain." %
                            str(ack_cmd.event_id()))  # TODO unit test this behavior

        # if current exposure is not None then we need to set the cancel replace history
        ack_exposure = Exposure(ack.price(), ack.qty(), ack.event_id())
        if self.current_exposure() is not None:
            self._event_id_to_cancel_replace_info[ack.event_id()] = CancelReplaceInfo(self.current_exposure(),
                                                                                      ack_exposure, self.side(),
                                                                                      self.market())
        # handle subchains
        subchain_open_reason = None
        subchain_close_reason = None
        if isinstance(ack_cmd, NewOrderCommand):
            subchain_open_reason = SubChain.NEW_ORDER
        elif isinstance(ack_cmd, CancelReplaceCommand):
            if ack.qty() == 0:
                subchain_close_reason = SubChain.CANCEL_REPLACE_TO_ZERO
            else:
                # see if cancel replace to new price for current subchain close / new subchain open
                if self._event_id_to_cancel_replace_info[ack.event_id()].is_price_change():
                    subchain_close_reason = SubChain.CANCEL_REPLACE_PRICE
                    subchain_open_reason = SubChain.CANCEL_REPLACE_PRICE
                # see if cancel replace to more qty for current subchain close / new subchain open
                elif self._event_id_to_cancel_replace_info[ack.event_id()].is_qty_increase():
                    subchain_close_reason = SubChain.CANCEL_REPLACE_INCREASE_QTY
                    subchain_open_reason = SubChain.CANCEL_REPLACE_INCREASE_QTY
        # if we have a subchain reason then we need to close current subchain and open a new one
        # don't need to worry about opening and closing if this already happened due to a aggressing partial fill
        if self.most_recent_subchain() is None or self.most_recent_subchain().open_event().event_id() != ack_cmd.event_id():
            if subchain_close_reason is not None:
                self._close_current_subchain(subchain_close_reason)
            if subchain_open_reason is not None:  # if a new one is open then the ack'd event opens it
                self._open_new_subchain(ack_cmd, subchain_open_reason)
            else:  # else the ack'd event gets added to already open SubChain
                self.most_recent_subchain().add_event(ack_cmd)
        # now, add the ack to the most recently open subchain
        self.most_recent_subchain().add_event(ack)

        # set the current exposure
        self._current_exposure = ack_exposure
        # set iceberg to new iceberg qty incase it changed
        self._iceberg_peak_qty = ack.iceberg_peak_qty()

        # visible qty gets resized if:
        # 1) new total qty is less than visible,
        # 2) a new price
        # 3) it is a cancel replace up in qty
        # 4) new visible is less than previous visible
        self._visible_qty = min(ack.iceberg_peak_qty(), ack.qty())

        # if the ack'd qty is 0, then this order chain is closed.
        if ack.qty() == 0:
            self._close_chain(ack)

    def apply_cancel_replace_command(self, cr):
        """
        Apply the cancel replace event to the OrderEventChain

        :param cr: MarketObjects.Events.OrderEvents.CancelReplaceCommand
        """
        assert isinstance(cr, CancelReplaceCommand)
        assert cr.market() == self.market(), \
            "Cancel Replace does NOT have same market as the OrderEventChain expects"
        assert cr.chain_id() == self._chain_id, \
            "Cancel Replace's chain ID (%s) does not match chain's ID (%s)" % (cr.chain_id(), self._chain_id)
        assert self.time_in_force() == OrderEventConstants.FAR, \
            "Cancel Replace commands only allowed for FAR time in force. This is a %s" % OrderEventConstants.time_in_force_str(
                self.time_in_force())
        self._events.append(cr)
        # set the requested exposure
        cr_exposure = Exposure(cr.price(), cr.qty(), cr.event_id())

        # add the requested exposure
        self._requested_exposures.append(cr_exposure)

    def apply_cancel_command(self, cc):
        """
        Apply the cancel command to the order chain

        :param cc: MarketObjects.Events.OrderEvents.CancelCommand
        """
        assert isinstance(cc, CancelCommand)
        assert cc.market() == self.market(), \
            "Cancel Command does NOT have same market as the OrderEventChain expects"
        assert cc.chain_id() == self._chain_id, \
            "Cancel Commnad chain ID (%s) does not match chain's ID (%s)" % (cc.chain_id(), self._chain_id)

        # append to list of events
        self._events.append(cc)
        # add a None exposure to the list of exposures
        self._requested_exposures.append(Exposure(None, 0, cc.event_id()))

    def apply_cancel_report(self, cr):
        """
        Apply the cancel report to the order chain.

        :param cr: MarketObjects.Events.OrderEvents.CancelReport
        """
        assert isinstance(cr, CancelReport)
        assert cr.market() == self.market(), \
            "Cancel Report does NOT have same market as the OrderEventChain expects"
        assert cr.chain_id() == self._chain_id, \
            "Cancel Report chain ID (%s) does not match chain's ID (%s)" % (cr.chain_id(), self._chain_id)
        # append to events
        self._events.append(cr)

        # if for some reason no subchain has been created to this point then one needs to be created and all events
        #  added to it. This could happen when for some reason a new order doesn't get acked, nor a cancel replace
        #  ack'd, and then the order is cancelled.
        #  This can also happen when there is a new order then cancel, like a FOK or FAK with no fill.
        if len(self._sub_chains) == 0:
            self._open_new_subchain(self._new_order_command, SubChain.NEW_ORDER)
            for event in self._events[1:]:  # skipping first one since already added in the creation of subchain
                self._sub_chains[0].add_event(event)
        else:
            # add to subchain
            if cr.cancel_command() is not None:  # need to add causing command to subchain
                self.most_recent_subchain().add_event(cr.cancel_command())

        self.most_recent_subchain().add_event(cr)
        # close open subchain
        self.most_recent_subchain().close_subchain(SubChain.CANCEL)
        # close order chain
        self._close_chain(cr)

    def _modify_exposure_by_partial_fill(self, pf):
        # if the aggressor then
        #  change outstanding exposure request because not ack'd yet
        #       - if outstanding exposure for causing event goes to zero or below then log an error
        #             and close order chain and subchain
        # don't need to change visible qty because not ack'd yet
        if pf.is_aggressor():
            requested_exposure = self.find_requested_exposure(pf.aggressing_command().event_id())
            if requested_exposure is None:
                self._logger.error(
                    "OrderChain state issue: %s. Aggressive partial fill (%s) with no outstanding exposure request for the aggressing event %s" %
                    (self._chain_id, str(pf.event_id()), str(pf.aggressing_command().event_id())))
            else:
                requested_exposure.dec_qty(pf.fill_qty())
                if requested_exposure.qty() <= 0:
                    self._logger.error(
                        "OrderChain state issue: %s. Aggressive partial fill (%s) took requested exposure from %s to %d. Closing Order Chain." %
                        (self._chain_id, str(pf.event_id()), str(pf.aggressing_command().event_id()),
                         pf.fill_qty()))
                    # close subchain down below after adding it
                    close_sub_chain = True
                    self._close_requested_exposure(pf)
                    self._close_chain(pf)
        else:
            # if passive then
            #  change open exposure by the fill size (because it has been ack'd)
            #       - if exposure goes to 0 or less then log a critical error and close order chain and subchain
            # change visible size
            #       - reduce by amount filled. If this is 0 or less then replenish min(iceberg peak qty, open exposure qty)
            if self._current_exposure is None:
                self._logger.error("OrderChain state issue: %s. Passive partial fill (%s) with no current exposure." %
                                   (self._chain_id, pf.event_id()))
            else:
                if self._current_exposure.qty() - pf.fill_qty() <= 0:
                    self._logger.error(
                        "OrderChain state issue: %s. Passive partial fill (%s) took open exposure to %d" %
                        (self._chain_id, pf.event_id(), pf.fill_qty()))
                    # subchain closed down below, after the partial fill is added to it
                    close_sub_chain = True
                    # don't decrement qty because this, in essence, gets taken care of in the close and we still want
                    #  some qty so we can grab the closing price
                    self._close_chain(pf)
                else:
                    self._current_exposure.dec_qty(pf.fill_qty())
                    self._visible_qty -= pf.fill_qty()
                    if self._visible_qty <= 0:
                        self._visible_qty = min(self.iceberg_peak_qty(), self._current_exposure.qty())
                        self._events_that_caused_visible_qty_refresh.add(pf.event_id())

    def _modify_exposure_by_full_fill(self, ff):
        if ff.is_aggressor():
            requested_exposure = self.find_requested_exposure(ff.aggressing_command().event_id())
            if ff.fill_qty() > requested_exposure.qty():
                self._logger.warn("OrderChain state issue: %s. Aggressive full fill (%s) for %d is more than open exposure for %s. Took open exposure to %d" %
                                  (str(self.chain_id()), str(ff.event_id()), ff.fill_qty(),
                                   str(requested_exposure.causing_event_id()),
                                   requested_exposure.qty() - ff.fill_qty()))
            elif ff.fill_qty() < requested_exposure.qty():
                self._logger.warn("OrderChain state issue: %s. Aggressive full fill (%s) for %d is less than open exposure for %s. Took open exposure to %d. Should NOT be full fill." %
                                  (str(self.chain_id()), str(ff.event_id()), ff.fill_qty(),
                                   str(requested_exposure.causing_event_id()),
                                   requested_exposure.qty() - ff.fill_qty()))
                self._logger.warn(str(self))
                self._logger.warn(str(requested_exposure))
        else:
            if ff.fill_qty() > self._current_exposure.qty():
                self._logger.warn("OrderChain state issue: %s. Passive full fill (%s) for %d is more than current exposure. Took exposure to %d" %
                                  (str(self.chain_id()), str(ff.event_id()), ff.fill_qty(),
                                   self._current_exposure.qty() - ff.fill_qty()))
            elif ff.fill_qty() < self._current_exposure.qty():
                self._logger.warn("OrderChain state issue: %s. Passive full fill (%s) for %d is less than current exposure. Took exposure to %d. Should NOT be full fill." %
                                  (str(self.chain_id()), str(ff.event_id()), ff.fill_qty(),
                                   self._current_exposure.qty() - ff.fill_qty()))
                self._logger.warn(str(self))
                self._logger.warn(str(self._current_exposure))

    def apply_partial_fill_report(self, pf):
        """
        Apply the partial fill report to the order chain.

        :param pf: MarketObjects.Events.OrderEvents.PartialFillReport
        """
        assert isinstance(pf, PartialFillReport), "applyPartialFill called with an event that is not a PartialFillReport."
        # add to the list of events
        self._events.append(pf)
        # populate the map of qty at price for fills
        self._filled_price_to_qty[pf.fill_price()] = pf.fill_qty()
        # track the match id
        self._match_ids.add(pf.match_id())
        close_sub_chain = False
        self._modify_exposure_by_partial_fill(pf)
        if pf.is_aggressor():
            # if aggressor then could be opening a new subchain
            # but dont' need to worry about it if second partial fill of subchain, only handle it if aggressing event id doens't match the current subchain open id
            if self.most_recent_subchain() is None or self.most_recent_subchain().open_event().event_id() != pf.aggressing_command().event_id():
                subchain_open_reason = None
                subchain_close_reason = None
                if isinstance(pf.aggressing_command(), NewOrderCommand):
                    subchain_open_reason = SubChain.NEW_ORDER
                elif isinstance(pf.aggressing_command(), CancelReplaceCommand):
                    if self.most_recent_subchain() is not None:  # if it is then there is no subchain to close
                        subchain_close_reason = SubChain.CANCEL_REPLACE_PRICE
                    subchain_open_reason = SubChain.CANCEL_REPLACE_PRICE
                # if we have a subchain reason then we need to close current subchain and open a new one
                if subchain_close_reason is not None:
                    if self.most_recent_subchain() is not None:
                        self._close_current_subchain(subchain_close_reason)
                if subchain_open_reason is not None:  # if a new one is open then the ack'd event opens it
                    self._open_new_subchain(pf.aggressing_command(), subchain_open_reason)

        # add to the open subchain
        self.most_recent_subchain().add_event(pf)
        if close_sub_chain:
            self.most_recent_subchain().close_subchain(SubChain.FULLY_FILLED)

    def apply_full_fill_report(self, ff):
        """
        Apply the partial fill report to the order chain.

        :param ff: MarketObjects.Events.OrderEvents.FullFillReport
        """
        # TODO unit test
        assert isinstance(ff, FullFillReport), "applyFullFill called with an event that is not a FullFillReport."
        # add to the list of events
        self._events.append(ff)
        # populate the map of qty at price for fills
        self._filled_price_to_qty[ff.fill_price()] = ff.fill_qty()
        # track the match id
        self._match_ids.add(ff.match_id())
        # log warning if amount filled wouldn't actually fully fill the chain (using open requested exposure if aggressor and acked exposure if passive)
        self._modify_exposure_by_full_fill(ff)
        if ff.is_aggressor():
            # if subchain for the aggressor command is not already open then need to open it and close previous
            if self.most_recent_subchain() is None or self.most_recent_subchain().open_event().event_id() != ff.aggressing_command().event_id():
                # cancel replace price is only thing that would result in a new subchain from a full fill
                if self.most_recent_subchain() is not None:
                    self.most_recent_subchain().close_subchain(SubChain.CANCEL_REPLACE_PRICE)
                    self._open_new_subchain(ff.aggressing_command(), SubChain.CANCEL_REPLACE_PRICE)
                else:
                    self._open_new_subchain(ff.aggressing_command(), SubChain.NEW_ORDER)
        # add to the open subchain
        self.most_recent_subchain().add_event(ff)
        # close the open subchain
        self.most_recent_subchain().close_subchain(SubChain.FULLY_FILLED)
        # close the order chain
        self._close_chain(ff)

    def apply_reject_report(self, rej):
        """
        Apply a reject to the OrderEventChain.

        :param rej: MarketObjects.Events.OrderEvents.RejectReport
        """
        assert isinstance(rej, RejectReport)
        assert rej.market() == self.market(), \
            "Reject does NOT have same market as the OrderEventChain expects"
        assert rej.chain_id() == self.chain_id(), \
            "Reject's chain ID (%s) does not match chain's ID (%s)" % (str(rej.chain_id()), str(self.chain_id()))
        assert rej.rejected_command().chain_id() == rej.chain_id(), \
            "Reject should have the same chain id as the command they are in response to."
        # add reject and what is being rejected to the subchain.
        self._events.append(rej)
        # add to subchain
        if self.most_recent_subchain() is not None:
            self.most_recent_subchain().add_event(rej.rejected_command())
        else:  # else it si the new order that needs to be added (new order is the only way we get here)
            self._open_new_subchain(rej.rejected_command(), SubChain.NEW_ORDER)
        self.most_recent_subchain().add_event(rej)

        # close out the exposure that is open
        self._close_requested_exposure(rej)
