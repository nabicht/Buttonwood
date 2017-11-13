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

import logging
from MarketPy.MarketObjects.CancelReasons import USER_CANCEL
from MarketPy.MarketObjects.Events.EventChains import OrderEventChain
from MarketPy.MarketObjects.Events.OrderEventConstants import FAR
from MarketPy.MarketObjects.Events.OrderEventConstants import FAK
from MarketPy.MarketObjects.Events.OrderEventConstants import FOK
from MarketPy.MarketObjects.Events.OrderEvents import AcknowledgementReport
from MarketPy.MarketObjects.Events.OrderEvents import CancelCommand
from MarketPy.MarketObjects.Events.OrderEvents import CancelReplaceCommand
from MarketPy.MarketObjects.Events.OrderEvents import CancelReport
from MarketPy.MarketObjects.Events.OrderEvents import NewOrderCommand
from MarketPy.MarketObjects.Events.OrderEvents import PartialFillReport
from MarketPy.MarketObjects.OrderBooks.OrderLevelBook import OrderLevelBook
from MarketPy.MarketObjects.Endpoint import Endpoint
from MarketPy.MarketObjects.Market import Market
from MarketPy.MarketObjects.Price import Price
from MarketPy.MarketObjects.PriceLevel import PriceLevel
from MarketPy.MarketObjects.Product import Product
from MarketPy.MarketObjects.Side import BID_SIDE
from MarketPy.MarketObjects.Side import ASK_SIDE
from MarketPy.utils.IDGenerators import MonotonicIntID

MARKET = Market(Product("MSFT", "Microsoft", "0.01", "0.01"),
                Endpoint("Nasdaq", "NSDQ"))
LOGGER = logging.getLogger()
SUBCHAIN_ID_GENERATOR = MonotonicIntID()


def test_populating_tob():
    ob = OrderLevelBook(MARKET, LOGGER)
    b1 = NewOrderCommand(1, 1234000.123, 1001, "user_a", MARKET, BID_SIDE, FAR,
                         Price("34.50"), 50)
    bid_oec1 = OrderEventChain(b1, LOGGER, SUBCHAIN_ID_GENERATOR)
    b1_ack = AcknowledgementReport(2, 1234000.123, 1001, "user_a", MARKET, b1, Price("34.50"), 50, 50)
    bid_oec1.apply_acknowledgement_report(b1_ack)
    ob.handle_acknowledgement_report(b1_ack, bid_oec1)
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_priority_chain(BID_SIDE).chain_id() == bid_oec1.chain_id()
    assert ob.best_bid_level().price() == Price("34.50")
    assert ob.best_bid_level().visible_qty() == 50
    assert ob.best_bid_level().hidden_qty() == 0

    # now add an offer
    a1 = NewOrderCommand(3, 1234000.888, 1002, "user_b", MARKET, ASK_SIDE, FAR,
                         Price("34.52"), 35, 10)
    ask_oec1 = OrderEventChain(a1, LOGGER, SUBCHAIN_ID_GENERATOR)
    a1_ack = AcknowledgementReport(4, 1234000.888, 1002, "user_b", MARKET, a1, Price("34.52"), 35, 10)
    ask_oec1.apply_acknowledgement_report(a1_ack)
    ob.handle_acknowledgement_report(a1_ack, ask_oec1)
    assert ob.best_ask_price() == Price("34.52")
    assert ob.best_priority_chain(ASK_SIDE).chain_id() == ask_oec1.chain_id()
    assert ob.best_ask_level().price() == Price("34.52")
    assert ob.best_ask_level().visible_qty() == 10
    assert ob.best_ask_level().hidden_qty() == 25
    assert ob.best_ask_level().number_of_orders() == 1

    # bid should not have changed
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_priority_chain(BID_SIDE).chain_id() == bid_oec1.chain_id()
    assert ob.best_bid_level().price() == Price("34.50")
    assert ob.best_bid_level().visible_qty() == 50
    assert ob.best_bid_level().hidden_qty() == 0
    assert ob.best_ask_level().number_of_orders() == 1
    assert ob.num_orders_at_price(BID_SIDE, Price("34.50")) == 1

    # add a second ask order to top of book
    a2 = NewOrderCommand(5, 1234001.888, 1003, "user_c", MARKET, ASK_SIDE, FAR,
                         Price("34.52"), 20, 20)
    ask_oec2 = OrderEventChain(a2, LOGGER, SUBCHAIN_ID_GENERATOR)
    a2_ack = AcknowledgementReport(6, 1234001.888, 1003, "user_b", MARKET, a2, Price("34.52"), 20, 20)
    ask_oec2.apply_acknowledgement_report(a2_ack)
    ob.handle_acknowledgement_report(a2_ack, ask_oec2)
    assert ob.best_ask_price() == Price("34.52")  # best price has not changed
    assert ob.best_priority_chain(ASK_SIDE).chain_id() == ask_oec1.chain_id()  # best priority chain has not changed
    assert ob.best_ask_level().price() == Price("34.52")  # price of best level has not changed
    print ob.best_ask_level().visible_qty()
    assert ob.best_ask_level().visible_qty() == 10 + 20  # visible qty should have got up by 20
    assert ob.best_ask_level().hidden_qty() == 25  # hidden qty should not have changed
    assert ob.best_ask_level().number_of_orders() == 2  # num orders should go up 2
    assert ob.num_orders_at_price(ASK_SIDE, Price("34.52")) == 2

    # bid should not have changed
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_priority_chain(BID_SIDE).chain_id() == bid_oec1.chain_id()
    assert ob.best_bid_level().price() == Price("34.50")
    assert ob.best_bid_level().visible_qty() == 50
    assert ob.best_bid_level().hidden_qty() == 0
    assert ob.best_bid_level().number_of_orders() == 1
    assert ob.num_orders_at_price(BID_SIDE, Price("34.50")) == 1

    # add a new bid at tob price
    b2 = NewOrderCommand(9, 1234000.123, 1004, "user_z", MARKET, BID_SIDE, FAR,
                         Price("34.50"), 70)
    bid_oec2 = OrderEventChain(b2, LOGGER, SUBCHAIN_ID_GENERATOR)
    b2_ack = AcknowledgementReport(10, 1234000.123, 1004, "user_z", MARKET, b2, Price("34.50"), 70, 70)
    bid_oec2.apply_acknowledgement_report(b2_ack)
    ob.handle_acknowledgement_report(b2_ack, bid_oec2)
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_priority_chain(BID_SIDE).chain_id() == bid_oec1.chain_id()
    assert ob.best_bid_level().price() == Price("34.50")
    assert ob.best_bid_level().visible_qty() == 120
    assert ob.best_bid_level().hidden_qty() == 0
    assert ob.best_ask_level().number_of_orders() == 2
    assert ob.num_orders_at_price(BID_SIDE, Price("34.50")) == 2

    # asks should not have changed
    assert ob.best_ask_price() == Price("34.52")  # best price has not changed
    assert ob.best_priority_chain(ASK_SIDE).chain_id() == ask_oec1.chain_id()  # best priority chain has not changed
    assert ob.best_ask_level().price() == Price("34.52")  # price of best level has not changed
    assert ob.best_ask_level().visible_qty() == 10 + 20  # visible qty should have got up by 20
    assert ob.best_ask_level().hidden_qty() == 25  # hidden qty should not have changed
    assert ob.best_ask_level().number_of_orders() == 2  # num orders should go up 2
    assert ob.num_orders_at_price(ASK_SIDE, Price("34.52")) == 2


def build_base_order_book():
    ob = OrderLevelBook(MARKET, LOGGER)
    b1 = NewOrderCommand(1, 1234000.123, 1001, "user_a", MARKET, BID_SIDE, FAR,
                         Price("34.50"), 50)
    bid_oec1 = OrderEventChain(b1, LOGGER, SUBCHAIN_ID_GENERATOR)
    b1_ack = AcknowledgementReport(2, 1234000.123, 1001, "user_a", MARKET, b1, Price("34.50"), 50, 50)
    bid_oec1.apply_acknowledgement_report(b1_ack)
    ob.handle_acknowledgement_report(b1_ack, bid_oec1)
    a1 = NewOrderCommand(3, 1234000.888, 1002, "user_b", MARKET, ASK_SIDE, FAR,
                         Price("34.52"), 35, 10)
    ask_oec1 = OrderEventChain(a1, LOGGER, SUBCHAIN_ID_GENERATOR)
    a1_ack = AcknowledgementReport(4, 1234000.888, 1002, "user_b", MARKET, a1, Price("34.52"), 35, 10)
    ask_oec1.apply_acknowledgement_report(a1_ack)
    ob.handle_acknowledgement_report(a1_ack, ask_oec1)
    a2 = NewOrderCommand(5, 1234001.888, 1003, "user_c", MARKET, ASK_SIDE, FAR,
                         Price("34.52"), 20, 20)
    ask_oec2 = OrderEventChain(a2, LOGGER, SUBCHAIN_ID_GENERATOR)
    a2_ack = AcknowledgementReport(6, 1234001.888, 1003, "user_b", MARKET, a2, Price("34.52"), 20, 20)
    ask_oec2.apply_acknowledgement_report(a2_ack)
    ob.handle_acknowledgement_report(a2_ack, ask_oec2)
    b2 = NewOrderCommand(9, 1234000.123, 1004, "user_z", MARKET, BID_SIDE, FAR,
                         Price("34.50"), 70)
    bid_oec2 = OrderEventChain(b2, LOGGER, SUBCHAIN_ID_GENERATOR)
    b2_ack = AcknowledgementReport(10, 1234000.123, 1004, "user_z", MARKET, b2, Price("34.50"), 70, 70)
    bid_oec2.apply_acknowledgement_report(b2_ack)
    ob.handle_acknowledgement_report(b2_ack, bid_oec2)

    # do some asserts to ensure we built book as expected
    bid_prices = ob.prices(BID_SIDE)
    print ob.best_bid_price()
    print bid_prices
    assert len(bid_prices) == 1
    assert bid_prices[0] == Price("34.50")
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_bid_level() == PriceLevel(Price("34.50"), 120, 0, 2)
    assert ob.best_priority_chain(BID_SIDE) == bid_oec1
    ask_prices = ob.ask_prices()
    assert len(ask_prices) == 1
    assert ask_prices[0] == Price("34.52")
    assert ob.best_ask_price() == Price("34.52")
    assert ob.best_ask_level() == PriceLevel(Price("34.52"), 30, 25, 2)
    assert ob.best_priority_chain(ASK_SIDE) == ask_oec1
    return ob


def test_establish_new_bid_tob():
    ob = build_base_order_book()
    b = NewOrderCommand(56, 1234002.123, 1008, "user_z", MARKET, BID_SIDE, FAR,
                        Price("34.51"), 35)
    bid_oec = OrderEventChain(b, LOGGER, SUBCHAIN_ID_GENERATOR)
    b_ack = AcknowledgementReport(57, 1234002.123, 1008, "user_z", MARKET, b, Price("34.51"), 35, 35)
    bid_oec.apply_acknowledgement_report(b_ack)
    ob.handle_acknowledgement_report(b_ack, bid_oec)
    # bid should have changed
    bid_prices = ob.bid_prices()
    assert len(bid_prices) == 2  # now 2 prices
    assert ob.best_priority_chain(BID_SIDE) == bid_oec  # the bid order chain above should now be best
    assert bid_prices[0] == Price("34.51")  # should be new best price
    assert ob.best_bid_price() == Price("34.51")  # should be new best price
    assert ob.best_bid_level() == PriceLevel(Price("34.51"), 35, 0,
                                             1)  # should have new best price level with only 1 order
    # ask should not have changed
    ask_prices = ob.ask_prices()
    assert len(ask_prices) == 1
    assert ask_prices[0] == Price("34.52")
    assert ob.best_ask_price() == Price("34.52")
    assert ob.best_ask_level() == PriceLevel(Price("34.52"), 30, 25, 2)


def test_establish_new_ask_tob():
    ob = build_base_order_book()
    a = NewOrderCommand(56, 1234002.123, 1008, "user_z", MARKET, ASK_SIDE, FAR,
                        Price("34.51"), 35)
    ask_oec = OrderEventChain(a, LOGGER, SUBCHAIN_ID_GENERATOR)
    a_ack = AcknowledgementReport(57, 1234002.123, 1008, "user_z", MARKET, a, Price("34.51"), 35, 35)
    ask_oec.apply_acknowledgement_report(a_ack)
    ob.handle_acknowledgement_report(a_ack, ask_oec)
    # ask should  have changed
    ask_prices = ob.ask_prices()
    assert len(ask_prices) == 2  # now 2 prices
    assert ob.best_priority_chain(ASK_SIDE) == ask_oec  # the bid order chain above should now be best
    assert ask_prices[0] == Price("34.51")  # should be new best price
    assert ob.best_ask_price() == Price("34.51")  # should be new best price
    assert ob.best_ask_level() == PriceLevel(Price("34.51"), 35, 0,
                                             1)  # should have new best price level with only 1 order
    # bid should not have changed
    bid_prices = ob.bid_prices()
    assert len(bid_prices) == 1
    assert bid_prices[0] == Price("34.50")
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_bid_level() == PriceLevel(Price("34.50"), 120, 0, 2)


def test_acking_fok():
    # should not allow -- so no changes to order book
    ob = build_base_order_book()
    a = NewOrderCommand(56, 1234002.123, 1008, "user_z", MARKET, ASK_SIDE, FOK,
                        Price("34.51"), 35)
    ask_oec = OrderEventChain(a, LOGGER, SUBCHAIN_ID_GENERATOR)
    a_ack = AcknowledgementReport(57, 1234002.123, 1008, "user_z", MARKET, a, Price("34.51"), 35, 35)
    ask_oec.apply_acknowledgement_report(a_ack)
    ob.handle_acknowledgement_report(a_ack, ask_oec)
    # NOTHING SHOULD HAVE CHANGED
    bid_prices = ob.bid_prices()
    assert len(bid_prices) == 1
    assert bid_prices[0] == Price("34.50")
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_bid_level() == PriceLevel(Price("34.50"), 120, 0, 2)
    ask_prices = ob.ask_prices()
    assert len(ask_prices) == 1
    assert ask_prices[0] == Price("34.52")
    assert ob.best_ask_price() == Price("34.52")
    assert ob.best_ask_level() == PriceLevel(Price("34.52"), 30, 25, 2)


def test_acking_fak():
    # should not allow -- so no changes to order book
    ob = build_base_order_book()
    a = NewOrderCommand(56, 1234002.123, 1008, "user_z", MARKET, ASK_SIDE, FAK,
                        Price("34.51"), 35)
    ask_oec = OrderEventChain(a, LOGGER, SUBCHAIN_ID_GENERATOR)
    a_ack = AcknowledgementReport(57, 1234002.123, 1008, "user_z", MARKET, a, Price("34.51"), 35, 35)
    ask_oec.apply_acknowledgement_report(a_ack)
    ob.handle_acknowledgement_report(a_ack, ask_oec)
    # NOTHING SHOULD HAVE CHANGED
    bid_prices = ob.bid_prices()
    assert len(bid_prices) == 1
    assert bid_prices[0] == Price("34.50")
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_bid_level() == PriceLevel(Price("34.50"), 120, 0, 2)
    ask_prices = ob.ask_prices()
    assert len(ask_prices) == 1
    assert ask_prices[0] == Price("34.52")
    assert ob.best_ask_price() == Price("34.52")
    assert ob.best_ask_level() == PriceLevel(Price("34.52"), 30, 25, 2)


def test_cancel_replace_order_up_in_qty():
    ob = build_base_order_book()
    # add a third order to the base order book bid side
    b = NewOrderCommand(56, 1234002.123, 1008, "user_z", MARKET, BID_SIDE, FAR,
                        Price("34.50"), 35)
    bid_oec = OrderEventChain(b, LOGGER, SUBCHAIN_ID_GENERATOR)
    b_ack = AcknowledgementReport(57, 1234002.123, 1008, "user_z", MARKET, b, Price("34.50"), 35, 35)
    bid_oec.apply_acknowledgement_report(b_ack)
    ob.handle_acknowledgement_report(b_ack, bid_oec)
    # should now be three order chains
    prev_order_chains = ob.order_chains_at_price(BID_SIDE, Price("34.50"))
    prev_visible_qty_at_tob = ob.visible_qty_at_price(BID_SIDE, Price("34.50"))
    prev_hidden_qty_at_tob = ob.hidden_qty_at_price(BID_SIDE, Price("34.50"))
    assert len(prev_order_chains) == 3
    # and test correct order
    assert prev_order_chains[0].chain_id() == 1001
    assert prev_order_chains[1].chain_id() == 1004
    assert prev_order_chains[2].chain_id() == 1008
    assert ob.best_priority_chain(BID_SIDE).chain_id() == 1001

    # cancel replace the first orderchain up in qty
    cr = CancelReplaceCommand(77, 1234012.123, prev_order_chains[0].chain_id(), prev_order_chains[0].user_id(), MARKET,
                              prev_order_chains[0].side(), prev_order_chains[0].current_price(), prev_order_chains[0].current_qty() + 40)
    prev_order_chains[0].apply_cancel_replace_command(cr)
    cr_ack = AcknowledgementReport(78, 1234012.123, prev_order_chains[0].chain_id(), "user_z", MARKET, cr,
                                   prev_order_chains[0].current_price(), prev_order_chains[0].current_qty() + 40,
                                   prev_order_chains[0].current_qty() + 40)
    prev_order_chains[0].apply_acknowledgement_report(cr_ack)
    ob.handle_acknowledgement_report(cr_ack, prev_order_chains[0])

    # should still only be one price on bid side as no price changes`
    assert len(ob.prices(BID_SIDE)) == 1
    # and that best price is still 34.50
    assert ob.best_price(BID_SIDE) == Price("34.50")
    # visible qty on the bid tob should have gone up by 40
    assert ob.visible_qty_at_price(BID_SIDE, Price("34.50")) == prev_visible_qty_at_tob + 40
    # hidden qty should not have gone up at all
    assert ob.hidden_qty_at_price(BID_SIDE, Price("34.50")) == prev_hidden_qty_at_tob, str(
        ob.hidden_qty_at_price(BID_SIDE, Price("34.50"))) + " != " + str(prev_hidden_qty_at_tob)
    # there should still be three but the order should be different
    current_order_chains = ob.order_chains_at_price(BID_SIDE, Price("34.50"))
    assert len(current_order_chains) == 3
    assert current_order_chains[0].chain_id() == 1004, "First chain at level should be 1004"
    assert current_order_chains[1].chain_id() == 1008, "Second chain at level should be 1008"
    assert current_order_chains[2].chain_id() == 1001, "Third chain at level should be 1001"
    # best priority order chain should now be 1004
    assert ob.best_priority_chain(BID_SIDE).chain_id() == 1004, "Best priority chain in order book should be 1004"

    prev_visible_qty_at_tob = ob.visible_qty_at_price(BID_SIDE, Price("34.50"))
    prev_hidden_qty_at_tob = ob.hidden_qty_at_price(BID_SIDE, Price("34.50"))

    # now move the middle order up in qty, which should move it to back of list
    cr2 = CancelReplaceCommand(79, 1234052.123, current_order_chains[1].chain_id(), current_order_chains[1].user_id(),
                               MARKET, current_order_chains[1].side(), current_order_chains[1].current_price(),
                               current_order_chains[1].current_qty() + 100, current_order_chains[1].current_qty() + 50)
    current_order_chains[1].apply_cancel_replace_command(cr2)
    cr_ack2 = AcknowledgementReport(80, 1234062.123, current_order_chains[1].chain_id(),
                                    current_order_chains[1].user_id(), MARKET, cr2,
                                    current_order_chains[1].current_price(),
                                    current_order_chains[1].current_qty() + 100,
                                    current_order_chains[1].current_qty() + 50)
    current_order_chains[1].apply_acknowledgement_report(cr_ack2)
    ob.handle_acknowledgement_report(cr_ack2, current_order_chains[1])
    # should still only be one price on bid side as no price changes`
    assert len(ob.prices(BID_SIDE)) == 1
    # and that best price is still 34.50
    assert ob.best_price(BID_SIDE) == Price("34.50")
    # visible qty on the bid tob should have gone up by 40
    assert ob.visible_qty_at_price(BID_SIDE, Price("34.50")) == prev_visible_qty_at_tob + 50
    # hidden qty should not have gone up at all
    assert ob.hidden_qty_at_price(BID_SIDE, Price("34.50")) == prev_hidden_qty_at_tob + 50, str(
        ob.hidden_qty_at_price(BID_SIDE, Price("34.50"))) + " != " + str(prev_hidden_qty_at_tob + 50)
    # there should still be three but the order should be different
    current_order_chains = ob.order_chains_at_price(BID_SIDE, Price("34.50"))
    assert len(current_order_chains) == 3
    assert current_order_chains[0].chain_id() == 1004, "First chain at level should be 1004"
    assert current_order_chains[1].chain_id() == 1001, "Second chain at level should be 1001"
    assert current_order_chains[2].chain_id() == 1008, "Third chain at level should be 1008"
    # best priority order chain should now be 1004
    assert ob.best_priority_chain(BID_SIDE).chain_id() == 1004, "Best priority chain in order book should be 1004"


def test_cancel_replace_order_down_in_qty():
    # should have no impact
    ob = build_base_order_book()
    prev_order_chains = ob.order_chains_at_price(BID_SIDE, Price("34.50"))
    assert len(prev_order_chains) == 2
    # and test correct order
    assert prev_order_chains[0].chain_id() == 1001
    assert prev_order_chains[1].chain_id() == 1004
    assert ob.best_priority_chain(BID_SIDE).chain_id() == 1001
    prev_visible_qty_at_tob = ob.visible_qty_at_price(BID_SIDE, Price("34.50"))
    prev_hidden_qty_at_tob = ob.hidden_qty_at_price(BID_SIDE, Price("34.50"))
    # now cancel replace the first bid down in size
    cr = CancelReplaceCommand(77, 1234012.123, prev_order_chains[0].chain_id(), prev_order_chains[0].user_id(), MARKET,
                              prev_order_chains[0].side(), prev_order_chains[0].current_price(), prev_order_chains[0].current_qty() - 5)
    prev_order_chains[0].apply_cancel_replace_command(cr)
    cr_ack = AcknowledgementReport(78, 1234012.123, prev_order_chains[0].chain_id(), prev_order_chains[0].user_id(),
                                   MARKET, cr, prev_order_chains[0].current_price(),
                                   prev_order_chains[0].current_qty() - 5, prev_order_chains[0].current_qty() - 5)
    prev_order_chains[0].apply_acknowledgement_report(cr_ack)
    ob.handle_acknowledgement_report(cr_ack, prev_order_chains[0])
    # assert that no ordering has changed
    current_order_chains = ob.order_chains_at_price(BID_SIDE, Price("34.50"))
    assert len(current_order_chains) == 2
    for chain in current_order_chains:
        print chain
    assert prev_order_chains[0].chain_id() == 1001
    assert prev_order_chains[1].chain_id() == 1004
    assert ob.best_priority_chain(BID_SIDE).chain_id() == 1001
    # size is 5 less
    assert ob.visible_qty_at_price(BID_SIDE, Price("34.50")) == prev_visible_qty_at_tob - 5
    assert ob.hidden_qty_at_price(BID_SIDE, Price("34.50")) == prev_hidden_qty_at_tob


# TODO def cancel_replace_order_down_to_zero_qty()
# should remove it from the book (and close order chain)

# TODO def cancel_replace_order_down_to_negative_qty()
# should remove it from the book (and close order chain)

def test_partial_aggressive_fill():
    # nothing should change as we only update orderbook for passive partial fills
    ob = build_base_order_book()
    # get baseline
    ask_prices = ob.ask_prices()
    bid_prices = ob.bid_prices()
    best_ask_price = ob.best_ask_price()
    best_bid_price = ob.best_bid_price()
    bast_ask_level = ob.best_ask_level()
    bast_bid_level = ob.best_bid_level()

    agg_new = NewOrderCommand(101, 1234002.123, 1008, "user_z", MARKET, BID_SIDE, FAR,
                              Price("34.52"), 45)
    oec = OrderEventChain(agg_new, LOGGER, SUBCHAIN_ID_GENERATOR)
    pf = PartialFillReport(102, 1234002.123, 1008, "user_z", MARKET, agg_new, 35, Price('34.52'),
                           BID_SIDE, 3333, 10)
    oec.apply_partial_fill_report(pf)
    ob.handle_partial_fill_report(pf, oec)
    # nothing at the order book should have changed
    assert ask_prices == ob.ask_prices()
    assert bid_prices == ob.bid_prices()
    assert best_ask_price == ob.best_ask_price()
    assert best_bid_price == ob.best_bid_price()
    assert bast_ask_level == ob.best_ask_level()
    assert bast_bid_level == ob.best_bid_level()


def test_parital_passive_fill():
    ob = build_base_order_book()
    # get baseline
    chain_aggressed_into = ob.best_priority_chain(ASK_SIDE)
    visible_qty = ob.visible_qty_at_price(ASK_SIDE, Price("34.52"))
    hidden_qty = ob.hidden_qty_at_price(ASK_SIDE, Price("34.52"))
    num_orders = ob.num_orders_at_price(ASK_SIDE, Price("34.52"))
    best_price = ob.best_price(ASK_SIDE)

    # the ack'd order getting aggresed into:
    # a1_ack = AcknowledgementReport(4, 1234000.888, 1002, "user_b", PROD, a1, Price("34.52"), 35, 10)
    agg_new = NewOrderCommand(101, 1234002.123, 1008, "user_z", MARKET, BID_SIDE, FAR,
                              Price("34.52"), 5)
    pf = PartialFillReport(102, 1234002.123, 1002, "user_b", MARKET, agg_new, 5, Price('34.52'),
                           ASK_SIDE, 3333, 30)
    chain_aggressed_into.apply_partial_fill_report(pf)
    ob.handle_partial_fill_report(pf, chain_aggressed_into)
    # now test for changes
    # ask visible should be 5 less
    assert ob.visible_qty_at_price(ASK_SIDE, Price("34.52")) == visible_qty - 5
    # ask hidden should stay the same
    assert hidden_qty == ob.hidden_qty_at_price(ASK_SIDE, Price("34.52"))
    # best price should be the same
    assert ob.best_ask_price() == best_price == Price("34.52")
    # num orders should stay the same
    assert num_orders == ob.num_orders_at_price(ASK_SIDE, Price("34.52"))
    # best chain on the ask should be the same
    assert ob.best_priority_chain(ASK_SIDE).chain_id() == chain_aggressed_into.chain_id() == 1002

    # nothing on bid should have changed
    bid_prices = ob.bid_prices()
    assert len(bid_prices) == 1
    assert bid_prices[0] == Price("34.50")
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_bid_level() == PriceLevel(Price("34.50"), 120, 0, 2)


def test_partial_passive_fill_resets_visible_qty():
    ob = build_base_order_book()
    # get baseline
    chain_aggressed_into = ob.best_priority_chain(ASK_SIDE)
    second_ask_back = ob.order_chains_at_price(ASK_SIDE, Price("34.52"))[1]
    visible_qty = ob.visible_qty_at_price(ASK_SIDE, Price("34.52"))
    hidden_qty = ob.hidden_qty_at_price(ASK_SIDE, Price("34.52"))
    num_orders = ob.num_orders_at_price(ASK_SIDE, Price("34.52"))
    best_price = ob.best_price(ASK_SIDE)

    # the ack'd order getting aggresed into:
    # a1_ack = AcknowledgementReport(4, 1234000.888, 1002, "user_b", PROD, a1, Price("34.52"), 35, 10)
    agg_new = NewOrderCommand(101, 1234002.123, 1008, "user_z", MARKET, BID_SIDE, FAR,
                              Price("34.52"), 10)
    pf = PartialFillReport(102, 1234002.123, 1002, "user_b", MARKET, agg_new, 10, Price('34.52'),
                           ASK_SIDE, 3333, 25)
    chain_aggressed_into.apply_partial_fill_report(pf)
    ob.handle_partial_fill_report(pf, chain_aggressed_into)
    # now test for changes
    # ask visible qty should stay the same because the 10 was filled and then replenished due to iceberg activity
    assert ob.visible_qty_at_price(ASK_SIDE, Price("34.52")) == visible_qty
    # ask hidden should be 10 less becaue of replenishment of iceberg peak
    assert hidden_qty - 10 == ob.hidden_qty_at_price(ASK_SIDE, Price("34.52"))
    # best price should be the same
    assert ob.best_ask_price() == best_price == Price("34.52")
    # num orders should stay the same
    assert num_orders == ob.num_orders_at_price(ASK_SIDE, Price("34.52"))
    # best chain on the ask should be what was the second back
    assert ob.best_priority_chain(ASK_SIDE).chain_id() == second_ask_back.chain_id()
    # worst chain on the ask should be what was the first
    assert ob.order_chains_at_price(ASK_SIDE, Price("34.52"))[-1].chain_id() == chain_aggressed_into.chain_id()

    # nothing on bid should have changed
    bid_prices = ob.bid_prices()
    assert len(bid_prices) == 1
    assert bid_prices[0] == Price("34.50")
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_bid_level() == PriceLevel(Price("34.50"), 120, 0, 2)


def test_partial_passive_fill_for_all_qty():
    # a partial fill for eveything should balk with some logs but should still be successful.
    # NOTE: this scenario is crazy and shouldn't actually happen (hidden getting filled before visible)
    #       but what the hell, let's cut corners on a test
    ob = build_base_order_book()
    # get baseline
    chain_aggressed_into = ob.best_priority_chain(ASK_SIDE)
    second_ask_back = ob.order_chains_at_price(ASK_SIDE, Price("34.52"))[1]
    visible_qty = ob.visible_qty_at_price(ASK_SIDE, Price("34.52"))
    hidden_qty = ob.hidden_qty_at_price(ASK_SIDE, Price("34.52"))
    num_orders = ob.num_orders_at_price(ASK_SIDE, Price("34.52"))
    best_price = ob.best_price(ASK_SIDE)

    # the ack'd order getting aggresed into:
    # a1_ack = AcknowledgementReport(4, 1234000.888, 1002, "user_b", PROD, a1, Price("34.52"), 35, 10)
    agg_new = NewOrderCommand(101, 1234002.123, 1008, "user_z", MARKET, BID_SIDE, FAR,
                              Price("34.52"), 35)
    pf = PartialFillReport(102, 1234002.123, 1002, "user_b", MARKET, agg_new, 35, Price('34.52'),
                           ASK_SIDE, 3333, 25)
    chain_aggressed_into.apply_partial_fill_report(pf)
    ob.handle_partial_fill_report(pf, chain_aggressed_into)
    # now test for changes
    # ask visible qty should be 10 less (the rest came from hidden)
    assert ob.visible_qty_at_price(ASK_SIDE, Price("34.52")) == visible_qty - 10
    # ask hidden should be 25 (35-10 visible) less
    assert hidden_qty - 25 == ob.hidden_qty_at_price(ASK_SIDE, Price("34.52"))
    # best price should be the same
    assert ob.best_ask_price() == best_price == Price("34.52")
    # should be 1 less order
    assert num_orders - 1 == ob.num_orders_at_price(ASK_SIDE, Price("34.52"))
    # best chain on the ask should be what was the second back
    assert ob.best_priority_chain(ASK_SIDE).chain_id() == second_ask_back.chain_id()
    # chain should no longer exist in book
    chains = ob.order_chains_at_price(ASK_SIDE, Price("34.52"))
    found = False
    for chain in chains:
        if chain.chain_id() == chain_aggressed_into.chain_id():
            found = True
    assert not found

    # nothing on bid should have changed
    bid_prices = ob.bid_prices()
    assert len(bid_prices) == 1
    assert bid_prices[0] == Price("34.50")
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_bid_level() == PriceLevel(Price("34.50"), 120, 0, 2)


def test_cancel_confirm_first_order():
    ob = build_base_order_book()
    chain_to_cancel = ob.best_priority_chain(ASK_SIDE)
    second_ask_back = ob.order_chains_at_price(ASK_SIDE, Price("34.52"))[1]
    visible_qty = ob.visible_qty_at_price(ASK_SIDE, Price("34.52"))
    hidden_qty = ob.hidden_qty_at_price(ASK_SIDE, Price("34.52"))
    num_orders = ob.num_orders_at_price(ASK_SIDE, Price("34.52"))
    best_price = ob.best_price(ASK_SIDE)

    cancel_command = CancelCommand(101, 1234002.123, chain_to_cancel.chain_id(), chain_to_cancel.user_id(), MARKET,
                                   USER_CANCEL)
    chain_to_cancel.apply_cancel_command(cancel_command)
    cancel_report = CancelReport(102, 1234002.123, chain_to_cancel.chain_id(), chain_to_cancel.user_id(), MARKET,
                                 cancel_command, USER_CANCEL)
    chain_to_cancel.apply_cancel_report(cancel_report)
    ob.handle_cancel_report(cancel_report, chain_to_cancel)
    # the 10 visible are now gone
    assert ob.visible_qty_at_price(ASK_SIDE, Price("34.52")) == visible_qty - 10
    # the 25 hidden should be gone
    assert hidden_qty - 25 == ob.hidden_qty_at_price(ASK_SIDE, Price("34.52"))
    # best price should be the same
    assert ob.best_ask_price() == best_price == Price("34.52")
    # should be 1 less order
    assert num_orders - 1 == ob.num_orders_at_price(ASK_SIDE, Price("34.52"))
    # best chain on the ask should be what was the second back
    assert ob.best_priority_chain(ASK_SIDE).chain_id() == second_ask_back.chain_id()
    # chain should no longer exist in book
    chains = ob.order_chains_at_price(ASK_SIDE, Price("34.52"))
    found = False
    for chain in chains:
        if chain.chain_id() == chain_to_cancel.chain_id():
            found = True
    assert not found

    # bids shouldn't change
    bid_prices = ob.bid_prices()
    assert len(bid_prices) == 1
    assert bid_prices[0] == Price("34.50")
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_bid_level() == PriceLevel(Price("34.50"), 120, 0, 2)


def test_cancel_confirm_second_order():
    ob = build_base_order_book()
    first_order_chain = ob.best_priority_chain(ASK_SIDE)
    second_ask_back = ob.order_chains_at_price(ASK_SIDE, Price("34.52"))[1]
    visible_qty = ob.visible_qty_at_price(ASK_SIDE, Price("34.52"))
    hidden_qty = ob.hidden_qty_at_price(ASK_SIDE, Price("34.52"))
    num_orders = ob.num_orders_at_price(ASK_SIDE, Price("34.52"))
    best_price = ob.best_price(ASK_SIDE)

    cancel_command = CancelCommand(101, 1234002.123, second_ask_back.chain_id(), second_ask_back.user_id(), MARKET,
                                   USER_CANCEL)
    second_ask_back.apply_cancel_command(cancel_command)
    cancel_report = CancelReport(102, 1234002.123, second_ask_back.chain_id(), second_ask_back.user_id(), MARKET,
                                 cancel_command, USER_CANCEL)
    second_ask_back.apply_cancel_report(cancel_report)
    ob.handle_cancel_report(cancel_report, second_ask_back)
    # the 20 visible are now gone
    assert ob.visible_qty_at_price(ASK_SIDE, Price("34.52")) == visible_qty - 20
    # hidden should stay the same
    assert hidden_qty == ob.hidden_qty_at_price(ASK_SIDE, Price("34.52"))
    # best price should be the same
    assert ob.best_ask_price() == best_price == Price("34.52")
    # should be 1 less order
    assert num_orders - 1 == ob.num_orders_at_price(ASK_SIDE, Price("34.52"))
    # best chain on the ask should be the original first
    assert ob.best_priority_chain(ASK_SIDE).chain_id() == first_order_chain.chain_id()
    # chain should no longer exist in book
    chains = ob.order_chains_at_price(ASK_SIDE, Price("34.52"))
    found = False
    for chain in chains:
        if chain.chain_id() == second_ask_back.chain_id():
            found = True
    assert not found

    # bids shouldn't change
    bid_prices = ob.bid_prices()
    assert len(bid_prices) == 1
    assert bid_prices[0] == Price("34.50")
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_bid_level() == PriceLevel(Price("34.50"), 120, 0, 2)


def test_cancel_confirm_entire_price_level():
    ob = build_base_order_book()

    # first add an order at a second price (34.53)
    a = NewOrderCommand(56, 1234002.123, 1009, "user_x", MARKET, ASK_SIDE, FAR,
                        Price("34.53"), 20)
    ask_oec = OrderEventChain(a, LOGGER, SUBCHAIN_ID_GENERATOR)
    a_ack = AcknowledgementReport(57, 1234002.123, 1009, "user_z", MARKET, a, Price("34.53"), 20, 20)
    ask_oec.apply_acknowledgement_report(a_ack)
    ob.handle_acknowledgement_report(a_ack, ask_oec)

    # cancel the orderchains at best price
    id_generator = MonotonicIntID()
    for i, chain in enumerate(ob.order_chains_at_price(ASK_SIDE, ob.best_price(ASK_SIDE))):
        cancel_command = CancelCommand(id_generator.id(), 1234002.123, chain.chain_id(), chain.user_id(), MARKET,
                                       USER_CANCEL)
        chain.apply_cancel_command(cancel_command)
        cancel_report = CancelReport(id_generator.id(), 1234002.123, chain.chain_id(), chain.user_id(), MARKET,
                                     cancel_command, USER_CANCEL)
        chain.apply_cancel_report(cancel_report)
        ob.handle_cancel_report(cancel_report, chain)

    assert ob.best_priority_chain(ASK_SIDE).chain_id() == ask_oec.chain_id()
    # best price should now be 34.53
    assert ob.best_ask_price() == Price('34.53')
    # visible qty is 20
    assert ob.visible_qty_at_price(ASK_SIDE, ob.best_ask_price()) == 20
    # hidden qty is 0
    assert ob.hidden_qty_at_price(ASK_SIDE, ob.best_ask_price()) == 0
    # num orders is 1
    assert ob.num_orders_at_price(ASK_SIDE, ob.best_ask_price()) == 1

    # bids shouldn't change
    bid_prices = ob.bid_prices()
    assert len(bid_prices) == 1
    assert bid_prices[0] == Price("34.50")
    assert ob.best_bid_price() == Price("34.50")
    assert ob.best_bid_level() == PriceLevel(Price("34.50"), 120, 0, 2)
