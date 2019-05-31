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
from buttonwood.MarketObjects.OrderBookListeners.OrderLevelBookListener import OrderLevelBookListener
from buttonwood.MarketObjects.Side import BID_SIDE, ASK_SIDE
from buttonwood.utils.dicts import NDeepDict
from collections import defaultdict


class MarketOrderTicksFromCrossing(OrderLevelBookListener, OrderEventListener):
    """
    Tracks how far away a MarketOrder was from crossing the opposite TOB.
     * Greater than 0 is how many ticks away from crossing (but did not cross)
     * 0 means it crossed TOB
     * less than 0 is how many ticks through the opposite TOB the order went
     * None means there was no opposite side to cross (or the order chain id
       being asked about wasn't a market order)

    Tracks only for order chain id because at the time of the new order, the
     subchain hasn't been created yet (doesn't get created until the execution
     report) so does not have a subchain id to use.

    This is designed so it can work with mulitiple order books at once.
    """
    # TODO UNIT TEST
    def __init__(self, logger):
        OrderLevelBookListener.__init__(self, logger)
        self._market_chain_id_ticks = NDeepDict(2)
        self._market_side_tob = {}
        self._market_side_tob[BID_SIDE] = defaultdict()
        self._market_side_tob[ASK_SIDE] = defaultdict()

    def handle_new_order_command(self, new_order_command, resulting_order_chain):
        # only applies to new order commands
        if new_order_command.is_market_order():
            side = new_order_command.side()
            price = new_order_command.price()
            market = new_order_command.market()
            mpi = market.product().mpi()
            opp_price = self._market_side_tob[market][side.other_side()]
            ticks_away = ((opp_price - price) if side.is_bid() else (price - opp_price)) / mpi
            self._market_chain_id_ticks.set([market, new_order_command.chain_id()], value=ticks_away)

    def notify_book_update(self, order_book, causing_order_chain, tob_updated):
        """
        Every time an orderbook comes in and tob updated need to save the bid price and the ask
         price. And only need to update for the side that is being updated.
        """
        if tob_updated:
            market = order_book.market()
            side = causing_order_chain.side()
            self._market_side_tob[market][side] = order_book.best_price(side)

    def ticks_from_crossing(self, market, chain_id):
        """
        Gets how many ticks away from crossing the chain id was.
         * Greater than 0 is how many ticks away from crossing (but did not cross)
         * 0 means it crossed TOB
         * less than 0 is how many ticks through the opposite TOB the order went
         * None means there was no opposite side to cross (or the order chain id
           being asked about wasn't a market order)

        :param market: MarketObjects.Market.Market
        :param chain_id: order chain's unique identifier
        :return: int
        """
        return self._market_chain_id_ticks.get([market, chain_id])
