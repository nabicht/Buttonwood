"""
This file is part of Buttonwood.

Buttonwood is a python software package created to help quickly create, (re)build, or 
analyze markets, market structures, and market participants. 

MIT License

Copyright (c) 2016-2019 Peter F. Nabicht

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

import logging
from nose.tools import *
from buttonwood.MarketObjects import CancelReasons
from buttonwood.MarketObjects.Events.EventChains import Exposure
from buttonwood.MarketObjects.Events.EventChains import OrderEventChain
from buttonwood.MarketObjects.Events.OrderEventConstants import FAR, FAK, FOK
from buttonwood.MarketObjects.Events.OrderEvents import AcknowledgementReport
from buttonwood.MarketObjects.Events.OrderEvents import CancelCommand
from buttonwood.MarketObjects.Events.OrderEvents import CancelReplaceCommand
from buttonwood.MarketObjects.Events.OrderEvents import CancelReport
from buttonwood.MarketObjects.Events.OrderEvents import FullFillReport
from buttonwood.MarketObjects.Events.OrderEvents import NewOrderCommand
from buttonwood.MarketObjects.Events.OrderEvents import PartialFillReport
from buttonwood.MarketObjects.Endpoint import Endpoint
from buttonwood.MarketObjects.Market import Market
from buttonwood.MarketObjects.Price import Price
from buttonwood.MarketObjects.Price import PriceFactory
from buttonwood.MarketObjects.Product import Product
from buttonwood.MarketObjects.Side import BID_SIDE, ASK_SIDE
from buttonwood.utils.IDGenerators import MonotonicIntID


MARKET = Market(Product("MSFT", "Microsoft"), Endpoint("Nasdaq", "NSDQ"), PriceFactory("0.01"))

LOGGER = logging.getLogger()


def test_exposure():
    e1 = Exposure(Price("1.1"), 2, 12345)
    e2 = Exposure(Price("1.1"), 2, 12345)
    assert e1 == e2
    assert e1.equivalent_exposure(e2)
    assert e1.equivalent_exposure(e1)
    assert e2.equivalent_exposure(e1)
    e3 = Exposure(Price("1.1"), 2, 6789)
    assert e1 != e3
    assert e1.price() == e2.price()
    print(e1, e2)
    assert e1.equivalent_exposure(e3)
    assert e3.equivalent_exposure(e1)
    e4 = Exposure(Price("1.1"), 3, 6789)
    assert e1 != e4
    assert e1.equivalent_exposure(e4) is False
    e5 = Exposure(Price("1.2"), 2, 6789)
    assert e1 != e5
    assert e1.equivalent_exposure(e5) is False


def test_creation():
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    assert oec.side().is_bid()
    assert oec.market() == MARKET
    assert oec.time_in_force() == FAR
    # no ack yet
    assert oec.current_exposure() is None
    assert len(oec.open_exposure_requests()) == 1
    assert oec.most_recent_requested_exposure() == Exposure(Price("34.52"), 1000, 121234)
    # visible qty should be nothing still
    assert oec.visible_qty() == 0


def test_acknowledgement():
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # no ack yet
    assert oec.most_recent_event() == n
    # check exposure
    assert len(oec.open_exposure_requests()) == 1
    assert oec.most_recent_requested_exposure() == oec.open_exposure_requests()[-1]
    assert oec.current_exposure() is None
    assert oec.most_recent_requested_exposure() == Exposure(Price("34.52"), 1000, 121234)
    # visible qty should be nothing still
    assert oec.visible_qty() == 0

    # now ack it
    ack = AcknowledgementReport(121235, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 1000, None)
    oec.apply_acknowledgement_report(ack)
    assert oec.most_recent_event() == ack
    # check exposure
    assert len(oec.open_exposure_requests()) == 0
    assert oec.most_recent_requested_exposure() is None
    assert oec.current_exposure() == Exposure(Price("34.52"), 1000, 121235)
    # check visible qty
    print(oec.visible_qty())
    assert oec.visible_qty() == 1000


def test_new_iceberg_order_ack():
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000, 50)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # no ack yet
    assert oec.most_recent_event() == n
    # check exposure
    assert len(oec.open_exposure_requests()) == 1
    assert oec.most_recent_requested_exposure() == oec.open_exposure_requests()[-1]
    assert oec.current_exposure() is None
    assert oec.most_recent_requested_exposure() == Exposure(Price("34.52"), 1000, 121234)
    # visible qty should be nothing still
    assert oec.visible_qty() == 0

    # now ack it
    ack = AcknowledgementReport(121235, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 1000, 50)
    oec.apply_acknowledgement_report(ack)
    assert oec.most_recent_event() == ack
    # check exposure
    assert len(oec.open_exposure_requests()) == 0
    assert oec.most_recent_requested_exposure() is None
    assert oec.current_exposure() == Exposure(Price("34.52"), 1000, 121235)
    # check visible qty
    assert oec.visible_qty() == 50


def test_close_exposure_fails_partial_fill():
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # _close_exposure(...) should fail for type PartialFill
    # TODO in OrderEventChain, check that the user hasn't changed on us mid chain
    aggressing_cmd = NewOrderCommand(1214321, 1234235.823, 2354, "user_y", MARKET, ASK_SIDE, FAK, Price("34.52"), 100)
    pf = PartialFillReport(121236, 1234237.723, 2342, "user_x", MARKET, aggressing_cmd, 100, Price("34.52"), ASK_SIDE,
                           987654, 900)
    assert_raises(Exception, oec._close_requested_exposure, pf)  # TODO change to EventChainLogicException


def test_close_exposure_cancel_closes_all():
    id_gen = MonotonicIntID(seed=23043, increment=1)
    n = NewOrderCommand(id_gen.id(), 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # should have 1 open exposure
    assert len(oec.open_exposure_requests()) == 1
    assert oec.most_recent_requested_exposure() == Exposure(Price("34.52"), 1000, id_gen.last_id())

    cr = CancelReplaceCommand(id_gen.id(), 1234235.863, 2342, "user_x", MARKET, BID_SIDE, Price("34.51"), 800)
    oec.apply_cancel_replace_command(cr)
    # now should have 2 open exposures
    assert len(oec.open_exposure_requests()) == 2
    assert oec.open_exposure_requests()[1] == Exposure(Price("34.51"), 800, id_gen.last_id())
    assert oec.most_recent_requested_exposure() == Exposure(Price("34.51"), 800, id_gen.last_id())

    cancel_command = CancelCommand(id_gen.id(), 1234274.663, 2342, "user_x", MARKET, CancelReasons.USER_CANCEL)
    oec.apply_cancel_command(cancel_command)
    # now should have 3 open exposures
    assert len(oec.open_exposure_requests()) == 3
    assert oec.open_exposure_requests()[2] == Exposure(None, 0, id_gen.last_id())
    assert oec.most_recent_requested_exposure() == Exposure(None, 0, id_gen.last_id())

    cancel_confirm = CancelReport(id_gen.id(), 1234278.663, 2342, "user_x", MARKET, cancel_command, CancelReasons.USER_CANCEL)
    oec.apply_cancel_report(cancel_confirm)
    # all exposures should be closed now
    assert len(oec.open_exposure_requests()) == 0
    assert oec.most_recent_requested_exposure() is None
    assert oec.has_partial_fill() is False


def test_basic_partial_fill():
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # now ack it
    ack = AcknowledgementReport(121235, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 1000, 1000)
    oec.apply_acknowledgement_report(ack)
    aggressor = NewOrderCommand(1111, 1234237.123, 22222, "user_x", MARKET, ASK_SIDE, FAR, Price("34.52"), 44)
    # now resting partial fill
    pf = PartialFillReport(121236, 1234237.123, 2342, "user_x", MARKET, aggressor, 44, Price("34.52"),
                           BID_SIDE, 99999, 1000-44)
    oec.apply_partial_fill_report(pf)

    assert oec.open_exposure_requests() == []
    assert oec.current_exposure().price() == Price("34.52")
    assert oec.current_exposure().qty() == 1000-44
    assert oec.visible_qty() == 1000-44
    assert oec.iceberg_peak_qty() == 1000  # should not have changed
    assert oec.has_partial_fill()


def test_basic_partial_fill_replenish_visible():
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 100, 40)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # now ack it
    ack = AcknowledgementReport(121235, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 100, 40)
    oec.apply_acknowledgement_report(ack)
    aggressor = NewOrderCommand(1111, 1234237.123, 22222, "user_y", MARKET, ASK_SIDE, FAR, Price("34.52"), 40)
    # now resting partial fill
    pf = PartialFillReport(121236, 1234237.123, 2342, "user_x", MARKET, aggressor, 40, Price("34.52"),
                           BID_SIDE, 99999, 100-40)
    oec.apply_partial_fill_report(pf)

    assert oec.open_exposure_requests() == []
    assert oec.current_exposure().price() == Price("34.52")
    assert oec.current_exposure().qty() == 100-40
    assert oec.visible_qty() == 40  # should have replenished
    assert oec.iceberg_peak_qty() == 40  # should not have changed
    assert oec.has_partial_fill()

    # now test the partial fill wipes out 40 more, so visible is min
    aggressor2 = NewOrderCommand(1114, 1234237.123, 33333, "user_y", MARKET, ASK_SIDE, FAR, Price("34.52"), 40)
    # now resting partial fill
    pf2 = PartialFillReport(121236, 1234237.123, 2342, "user_x", MARKET, aggressor2, 40, Price("34.52"),
                            BID_SIDE, 99999, 100-40-40)  # subtract out the size of 2 40 lot fills now
    oec.apply_partial_fill_report(pf2)
    assert oec.open_exposure_requests() == []
    assert oec.current_exposure().price() == Price("34.52")
    assert oec.current_exposure().qty() == 100-40-40
    assert oec.visible_qty() == 100-40-40  # should have replenished to min of 40 and 100-40-40
    assert oec.iceberg_peak_qty() == 40  # should not have changed
    assert oec.has_partial_fill()


def test_partial_fill_to_zero_closes_out_order():
    # when a partialfill closses out to an order there should be a balking because it is a paritial fill so shouldn't happen, but should allow
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 100)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # now ack it
    ack = AcknowledgementReport(121235, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 100, 100)
    oec.apply_acknowledgement_report(ack)
    aggressor = NewOrderCommand(1111, 1234237.123, 22222, "user_y", MARKET, ASK_SIDE, FAR, Price("34.52"), 100)
    # now resting partial fill
    pf = PartialFillReport(1212344, 1234237.123, 2342, "user_x", MARKET, aggressor, 100, Price("34.52"),
                           BID_SIDE, 99999, 0)
    oec.apply_partial_fill_report(pf)
    assert oec.open_exposure_requests() == []
    assert oec.is_open() is False
    assert oec.visible_qty() == 0
    assert oec.current_exposure() == Exposure(None, 0, 1212344)


def test_partial_fill_on_unacked_order():
    # when an unacked order is filled the requested exposure gets impacted
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 100)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    assert oec.current_exposure() is None
    assert oec.most_recent_requested_exposure().qty() == 100
    assert oec.most_recent_requested_exposure().price() == Price("34.52")

    # now resting partial fill
    pf = PartialFillReport(1212344, 1234237.123, 2342, "user_x", MARKET, n, 10, Price("34.52"),
                           BID_SIDE, 99999, 90)
    oec.apply_partial_fill_report(pf)
    assert oec.current_exposure() is None
    assert oec.most_recent_requested_exposure().qty() == 90
    assert oec.most_recent_requested_exposure().price() == Price("34.52")


def test_partial_fill_on_multiple_unacked_requests():
    n = NewOrderCommand(1, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # should have 1 open exposure
    assert len(oec.open_exposure_requests()) == 1
    assert oec.most_recent_requested_exposure() == Exposure(Price("34.52"), 1000, 1)

    cr1 = CancelReplaceCommand(2, 1234235.863, 2342, "user_x", MARKET, BID_SIDE, Price("34.51"), 800)
    oec.apply_cancel_replace_command(cr1)
    # now should have 2 open exposures
    assert len(oec.open_exposure_requests()) == 2
    assert oec.open_exposure_requests()[0] == Exposure(Price("34.52"), 1000, 1)
    assert oec.open_exposure_requests()[1] == Exposure(Price("34.51"), 800, 2)

    cr2 = CancelReplaceCommand(3, 1234236.842, 2342, "user_x", MARKET, BID_SIDE, Price("34.55"), 800)
    oec.apply_cancel_replace_command(cr2)
    # now should have 2 open exposures
    assert len(oec.open_exposure_requests()) == 3
    assert oec.open_exposure_requests()[0] == Exposure(Price("34.52"), 1000, 1)
    assert oec.open_exposure_requests()[1] == Exposure(Price("34.51"), 800, 2)
    assert oec.open_exposure_requests()[2] == Exposure(Price("34.55"), 800, 3)

    cr3 = CancelReplaceCommand(4, 1234236.842, 2342, "user_x", MARKET, BID_SIDE, Price("34.56"), 800)
    oec.apply_cancel_replace_command(cr3)
    # now should have 2 open exposures
    assert len(oec.open_exposure_requests()) == 4
    assert oec.open_exposure_requests()[0] == Exposure(Price("34.52"), 1000, 1)
    assert oec.open_exposure_requests()[1] == Exposure(Price("34.51"), 800, 2)
    assert oec.open_exposure_requests()[2] == Exposure(Price("34.55"), 800, 3)
    assert oec.open_exposure_requests()[3] == Exposure(Price("34.56"), 800, 4)

    # a partial fill should should only impact the one the partial fill is for
    # partially filling orderid 3 (cr2)
    pf1 = PartialFillReport(5, 1234237.123, 2342, "user_x", MARKET, cr2, 10, Price("34.55"),
                            BID_SIDE, 999, 790)
    oec.apply_partial_fill_report(pf1)
    assert len(oec.open_exposure_requests()) == 4
    assert oec.open_exposure_requests()[0] == Exposure(Price("34.52"), 1000, 1)
    assert oec.open_exposure_requests()[1] == Exposure(Price("34.51"), 800, 2)
    assert oec.open_exposure_requests()[2] == Exposure(Price("34.55"), 790, 3)
    assert oec.open_exposure_requests()[3] == Exposure(Price("34.56"), 800, 4)

    # and again
    pf2 = PartialFillReport(6, 1234237.123, 2342, "user_x", MARKET, cr2, 10, Price("34.55"),
                            BID_SIDE, 1000, 780)
    oec.apply_partial_fill_report(pf2)
    assert len(oec.open_exposure_requests()) == 4
    assert oec.open_exposure_requests()[0] == Exposure(Price("34.52"), 1000, 1)
    assert oec.open_exposure_requests()[1] == Exposure(Price("34.51"), 800, 2)
    assert oec.open_exposure_requests()[2] == Exposure(Price("34.55"), 780, 3)
    assert oec.open_exposure_requests()[3] == Exposure(Price("34.56"), 800, 4)

    # and now I can fill order id 4 (cr 3)
    pf3 = PartialFillReport(6, 1234237.123, 2342, "user_x", MARKET, cr3, 50, Price("34.56"),
                            BID_SIDE, 1001, 750)
    oec.apply_partial_fill_report(pf3)
    assert len(oec.open_exposure_requests()) == 4
    assert oec.open_exposure_requests()[0] == Exposure(Price("34.52"), 1000, 1)
    assert oec.open_exposure_requests()[1] == Exposure(Price("34.51"), 800, 2)
    assert oec.open_exposure_requests()[2] == Exposure(Price("34.55"), 780, 3)
    assert oec.open_exposure_requests()[3] == Exposure(Price("34.56"), 750, 4)

    # now start acking them
    ack1 = AcknowledgementReport(10, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 1000, None)
    oec.apply_acknowledgement_report(ack1)
    assert len(oec.open_exposure_requests()) == 3
    assert oec.open_exposure_requests()[0] == Exposure(Price("34.51"), 800, 2)
    assert oec.open_exposure_requests()[1] == Exposure(Price("34.55"), 780, 3)
    assert oec.open_exposure_requests()[2] == Exposure(Price("34.56"), 750, 4)
    assert oec.current_exposure() == Exposure(Price("34.52"), 1000, 10)

    ack2 = AcknowledgementReport(11, 1234235.123, 2342, "user_x", MARKET, cr1, Price("34.51"), 800, None)
    oec.apply_acknowledgement_report(ack2)
    assert len(oec.open_exposure_requests()) == 2
    assert oec.open_exposure_requests()[0] == Exposure(Price("34.55"), 780, 3)
    assert oec.open_exposure_requests()[1] == Exposure(Price("34.56"), 750, 4)
    assert oec.current_exposure() == Exposure(Price("34.51"), 800, 11)

    ack3 = AcknowledgementReport(12, 1234235.123, 2342, "user_x", MARKET, cr2, Price("34.55"), 780, None)
    oec.apply_acknowledgement_report(ack3)
    assert len(oec.open_exposure_requests()) == 1
    print(oec.open_exposure_requests()[0])
    assert oec.open_exposure_requests()[0] == Exposure(Price("34.56"), 750, 4)
    assert oec.current_exposure() == Exposure(Price("34.55"), 780, 12)

    ack4 = AcknowledgementReport(13, 1234235.123, 2342, "user_x", MARKET, cr3, Price("34.56"), 750, None)
    oec.apply_acknowledgement_report(ack4)
    assert len(oec.open_exposure_requests()) == 0
    assert oec.current_exposure() == Exposure(Price("34.56"), 750, 13)


def test_basic_full_fill_on_acked_order():
    n = NewOrderCommand(1, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # now ack it
    ack = AcknowledgementReport(2, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 1000, 1000)
    oec.apply_acknowledgement_report(ack)
    assert oec.visible_qty() == 1000
    assert oec.current_exposure().qty() == 1000
    assert oec.current_exposure().price() == Price("34.52")
    assert oec.is_open()
    aggressor = NewOrderCommand(1111, 1234237.123, 22222, "user_y", MARKET, ASK_SIDE, FAR, Price("34.52"), 1000)
    full_fill = FullFillReport(3, 1234237.123, 2342, "user_x", MARKET, aggressor, 1000, Price('34.52'), BID_SIDE, 12345)
    oec.apply_full_fill_report(full_fill)
    assert oec.visible_qty() == 0
    assert oec.current_exposure().price() is None
    assert oec.current_exposure().qty() == 0
    assert oec.current_exposure().causing_event_id() == 3
    assert oec.is_open() is False


def test_basic_full_fill_on_unacked_order():
    n = NewOrderCommand(1, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    assert oec.visible_qty() == 0
    assert oec.current_exposure() is None
    assert oec.most_recent_requested_exposure().price() == Price("34.52")
    assert oec.most_recent_requested_exposure().qty() == 1000
    assert oec.is_open()
    full_fill = FullFillReport(3, 1234237.123, 2342, "user_x", MARKET, n, 1000, Price('34.52'), BID_SIDE, 12345)
    oec.apply_full_fill_report(full_fill)
    assert oec.visible_qty() == 0
    assert oec.current_exposure().price() is None
    assert oec.current_exposure().qty() == 0
    assert oec.current_exposure().causing_event_id() == 3
    assert len(oec.open_exposure_requests()) == 0
    assert oec.is_open() is False


def test_full_fill_on_acked_order_with_unacked_cr_in_flight():
    n = NewOrderCommand(1, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # now ack it
    ack = AcknowledgementReport(2, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 1000, 1000)
    oec.apply_acknowledgement_report(ack)
    assert oec.visible_qty() == 1000
    assert oec.current_exposure().qty() == 1000
    assert oec.current_exposure().price() == Price("34.52")
    assert len(oec.open_exposure_requests()) == 0
    assert oec.is_open()

    cr = CancelReplaceCommand(2, 1234236.842, 2342, "user_x", MARKET, BID_SIDE, Price("34.56"), 800)
    oec.apply_cancel_replace_command(cr)
    # now should have 2 open exposures
    assert oec.visible_qty() == 1000
    assert oec.current_exposure().qty() == 1000
    assert oec.current_exposure().price() == Price("34.52")
    assert oec.is_open()
    assert len(oec.open_exposure_requests()) == 1
    assert oec.most_recent_requested_exposure() == Exposure(Price("34.56"), 800, 2)

    aggressor = NewOrderCommand(1111, 1234237.123, 22222, "user_y", MARKET, ASK_SIDE, FAR, Price("34.52"), 1000)
    full_fill = FullFillReport(3, 1234237.123, 2342, "user_x", MARKET, aggressor, 1000, Price('34.52'), BID_SIDE, 12345)
    oec.apply_full_fill_report(full_fill)
    assert oec.visible_qty() == 0
    assert oec.current_exposure().price() is None
    assert oec.current_exposure().qty() == 0
    assert oec.current_exposure().causing_event_id() == 3
    assert len(oec.open_exposure_requests()) == 0
    assert oec.is_open() is False


def test_full_fill_on_unacked_cr_with_acked_new_order():
    n = NewOrderCommand(1, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # now ack it
    ack = AcknowledgementReport(2, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 1000, 1000)
    oec.apply_acknowledgement_report(ack)
    assert oec.visible_qty() == 1000
    assert oec.current_exposure().qty() == 1000
    assert oec.current_exposure().price() == Price("34.52")
    assert len(oec.open_exposure_requests()) == 0
    assert oec.is_open()

    cr = CancelReplaceCommand(3, 1234236.842, 2342, "user_x", MARKET, BID_SIDE, Price("34.56"), 800)
    oec.apply_cancel_replace_command(cr)
    # now should have 2 open exposures
    assert oec.visible_qty() == 1000
    assert oec.current_exposure().qty() == 1000
    assert oec.current_exposure().price() == Price("34.52")
    assert oec.is_open()
    assert len(oec.open_exposure_requests()) == 1
    assert oec.most_recent_requested_exposure() == Exposure(Price("34.56"), 800, 3)

    full_fill = FullFillReport(4, 1234237.123, 2342, "user_x", MARKET, cr, 800, Price("34.56"), BID_SIDE, 12345)
    oec.apply_full_fill_report(full_fill)
    assert oec.visible_qty() == 0
    assert oec.current_exposure().price() is None
    assert oec.current_exposure().qty() == 0
    assert oec.current_exposure().causing_event_id() == 4
    assert len(oec.open_exposure_requests()) == 0
    assert oec.is_open() is False


def test_full_fill_with_not_enough_size_on_acked_new_order():
    # should balk but shouldn't keep it from working
    n = NewOrderCommand(1, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # now ack it
    ack = AcknowledgementReport(2, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 1000, 1000)
    oec.apply_acknowledgement_report(ack)
    assert oec.visible_qty() == 1000
    assert oec.current_exposure().qty() == 1000
    assert oec.current_exposure().price() == Price("34.52")
    assert oec.is_open()
    aggressor = NewOrderCommand(1111, 1234237.123, 22222, "user_y", MARKET, ASK_SIDE, FAR, Price("34.52"), 1000)
    full_fill = FullFillReport(3, 1234237.123, 2342, "user_x", MARKET, aggressor, 17, Price('34.52'), BID_SIDE, 12345)
    oec.apply_full_fill_report(full_fill)
    assert oec.visible_qty() == 0
    assert oec.current_exposure().price() is None
    assert oec.current_exposure().qty() == 0
    assert oec.current_exposure().causing_event_id() == 3
    assert oec.is_open() is False


def test_full_fill_with_too_much_size_on_acked_new_order():
    # should balk but shouldn't keep it from working
    n = NewOrderCommand(1, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # now ack it
    ack = AcknowledgementReport(2, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 1000, 1000)
    oec.apply_acknowledgement_report(ack)
    assert oec.visible_qty() == 1000
    assert oec.current_exposure().qty() == 1000
    assert oec.current_exposure().price() == Price("34.52")
    assert oec.is_open()
    aggressor = NewOrderCommand(1111, 1234237.123, 22222, "user_y", MARKET, ASK_SIDE, FAR, Price("34.52"), 1000)
    full_fill = FullFillReport(3, 1234237.123, 2342, "user_x", MARKET, aggressor, 3400, Price('34.52'), BID_SIDE, 12345)
    oec.apply_full_fill_report(full_fill)
    assert oec.visible_qty() == 0
    assert oec.current_exposure().price() is None
    assert oec.current_exposure().qty() == 0
    assert oec.current_exposure().causing_event_id() == 3
    assert oec.is_open() is False


def test_full_fill_with_not_enough_size_on_unacked_new_order():
    # should balk but shouldn't keep it from working
    n = NewOrderCommand(1, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    assert oec.visible_qty() == 0
    assert oec.current_exposure() is None
    assert oec.most_recent_requested_exposure().price() == Price("34.52")
    assert oec.most_recent_requested_exposure().qty() == 1000
    assert oec.is_open()
    full_fill = FullFillReport(3, 1234237.123, 2342, "user_x", MARKET, n, 17, Price('34.52'), BID_SIDE, 12345)
    oec.apply_full_fill_report(full_fill)
    assert oec.visible_qty() == 0
    assert oec.current_exposure().price() is None
    assert oec.current_exposure().qty() == 0
    assert oec.current_exposure().causing_event_id() == 3
    assert oec.is_open() is False


def test_full_fill_with_too_much_size_on_unacked_new_order():
    # should balk but shouldn't keep it from working
    n = NewOrderCommand(1, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    assert oec.visible_qty() == 0
    assert oec.current_exposure() is None
    assert oec.most_recent_requested_exposure().price() == Price("34.52")
    assert oec.most_recent_requested_exposure().qty() == 1000
    assert oec.is_open()
    full_fill = FullFillReport(3, 1234237.123, 2342, "user_x", MARKET, n, 17, Price('34.52'), BID_SIDE, 12345)
    oec.apply_full_fill_report(full_fill)
    assert oec.visible_qty() == 0
    assert oec.current_exposure().price() is None
    assert oec.current_exposure().qty() == 0
    assert oec.current_exposure().causing_event_id() == 3
    assert oec.is_open() is False


@raises(AssertionError)
def test_creation_without_neworder():
    cr = CancelReplaceCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, Price("43.01"), 234)
    OrderEventChain(cr, LOGGER, MonotonicIntID())


def test_cancel_replace_not_allowed_on_fak_or_fok():
    # FAK
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAK, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    cr = CancelReplaceCommand(121235, 1234235.324, 2342, "user_x", MARKET, BID_SIDE, Price("43.01"), 234)
    assert_raises(AssertionError, oec.apply_cancel_replace_command, cr)
    # FOK
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FOK, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    cr = CancelReplaceCommand(121235, 1234235.324, 2342, "user_x", MARKET, BID_SIDE, Price("43.01"), 234)
    assert_raises(AssertionError, oec.apply_cancel_replace_command, cr)


def test_subchain_str():
    # pretty basic, just testing that it doesn't break
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # now ack it
    ack = AcknowledgementReport(121235, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 1000, None)
    oec.apply_acknowledgement_report(ack)
    assert oec.most_recent_event() == ack

    # now check I can get a __str__ of the subchain no problem
    str(oec.most_recent_subchain())


def test_subchain_to_json():
    # pretty basic, just testing that it doesn't break
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # now ack it
    ack = AcknowledgementReport(121235, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 1000, None)
    oec.apply_acknowledgement_report(ack)
    assert oec.most_recent_event() == ack

    # now check I can get a to_json of the subchain no problem
    oec.most_recent_subchain().to_json()



def test_subchain_getters():
    # pretty basic, just testing that it doesn't break
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # now ack it
    ack = AcknowledgementReport(121235, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 1000, None)
    oec.apply_acknowledgement_report(ack)
    # and partial fill
    aggressor = NewOrderCommand(1111, 1234237.123, 22222, "user_y", MARKET, ASK_SIDE, FAR, Price("34.52"), 44)
    # now resting partial fill
    pf = PartialFillReport(121236, 1234237.123, 2342, "user_x", MARKET, aggressor, 44, Price("34.52"),
                           BID_SIDE, 99999, 1000 - 44)
    oec.apply_partial_fill_report(pf)

    subchain = oec.most_recent_subchain()
    assert subchain.open_event() == n
    assert subchain.first_execution_report() == ack
    assert subchain.fills() == [pf]
    assert subchain.last_event() == pf


def test_subchain_getters_partial_fill_before_ack():
    # pretty basic, just testing that it doesn't break
    n = NewOrderCommand(121234, 1234235.123, 2342, "user_x", MARKET, BID_SIDE, FAR, Price("34.52"), 1000)
    oec = OrderEventChain(n, LOGGER, MonotonicIntID())
    # now aggressive partial fill
    pf = PartialFillReport(121236, 1234237.123, 2342, "user_x", MARKET, n, 44, Price("34.52"),
                           BID_SIDE, 99999, 1000 - 44)
    oec.apply_partial_fill_report(pf)
    # now ack it
    ack = AcknowledgementReport(121235, 1234235.123, 2342, "user_x", MARKET, n, Price("34.52"), 1000-44, None)
    oec.apply_acknowledgement_report(ack)

    subchain = oec.most_recent_subchain()
    assert subchain.open_event() == n
    assert subchain.first_execution_report() == pf
    assert subchain.fills() == [pf]
    assert subchain.last_event() == ack

