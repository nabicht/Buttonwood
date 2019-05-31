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

from buttonwood.MarketObjects.OrderBookListeners.OrderLevelBookListener import OrderLevelBookListener
from buttonwood.utils.dicts import NDeepDict


class SubchainTimeAtTopPriorityListener(OrderLevelBookListener):

    def __init__(self, logger):
        OrderLevelBookListener.__init__(self, logger)
        self._market_to_subchain_id_to_time = NDeepDict(depth=2, default_value=list)
        self._market_to_side_to_prev_tob_subchain_id = NDeepDict(depth=2, default_value=lambda: None)

    def notify_book_update(self, order_book, causing_order_chain, tob_updated):
        """
        every time an order book updates, for the side of the causing order chain check the top priority subchain and
         track the amount of time that subchain is at top priority.
         
        Top priority means it is the next to be filled.
        """
        side = causing_order_chain.side()
        top_priority_subchain_id = None
        chains = order_book.order_chains_at_price(side, order_book.best_price(side))
        if len(chains) > 0:
            top_priority_subchain_id = chains[0].most_recent_subchain().subchain_id()
        market = order_book.market()
        use_time = order_book.last_update_time()
        prev_top_priority_subchain_id = self._market_to_side_to_prev_tob_subchain_id.get((market, side))
        if prev_top_priority_subchain_id is not None:
            # if top priority subchain is none and previous top subchain is not None, then close out open time range
            #  of prev
            if top_priority_subchain_id is None:
                l = self._market_to_subchain_id_to_time.get((market, prev_top_priority_subchain_id))
                l[-1] = (l[-1][0], use_time)
            # if top priority id is different than the previous then close out previous and open new one
            elif top_priority_subchain_id != prev_top_priority_subchain_id:
                l_old = self._market_to_subchain_id_to_time.get((market, prev_top_priority_subchain_id))
                l_old[-1] = (l_old[-1][0], use_time)
                l_new = self._market_to_subchain_id_to_time.get((market, top_priority_subchain_id))
                l_new.append((use_time, None))

            # if the same then just keep going, no need to update anything
        else:  # if prev is None then we are just creating a new one
            l = self._market_to_subchain_id_to_time.get((market, top_priority_subchain_id))
            l.append((use_time, None))

        # and set prev to current
        self._market_to_side_to_prev_tob_subchain_id.set((market, side), value=top_priority_subchain_id)

    def time_at_top_priority(self, market, subchain_id, query_time=None):
        """
        Gets the time a subchain spent at top priority. If subchain was never
         at top priority (or didn't even exit) returns 0.

        if query_time is not None (defaults to None) then that time will be used as the ceiling for the query.
         This means if no end time on the last tuple this will be used as the end time. It also means that if any tuple
          overlaps the query time the query time will be used as a cut off.

        :param market: MarketObjects.Market.Market
        :param subchain_id: subchain identifier
        :param query_time: float. The time since epoch of the query (seconds.milli/microseconds)
        :return: float
        """
        total_time = 0
        tob_time_ranges = self._market_to_subchain_id_to_time.get((market, subchain_id))
        if len(tob_time_ranges) == 0:
            return 0
        for tob_time_range in tob_time_ranges[:-1]:
            if query_time is not None and tob_time_range[0] >= query_time:
                return total_time  # no need to go through the rest of list, found the forced end here
            if tob_time_range[1] is None:
                self._logger.warning("%s %s: Cannot correctly calculate top priority time because a non last range end time is None: %s" %
                                     (str(market), str(subchain_id), str(tob_time_ranges)))
                continue

            if query_time is not None and tob_time_range[1] > query_time:
                total_time += query_time - tob_time_range[0]
                return total_time  # no need to go through the rest of list, found the forced end here

            total_time += tob_time_range[1] - tob_time_range[0]

        tob_time_range = tob_time_ranges[-1]
        if query_time is None:
            if tob_time_range[1] is None:
                self._logger.warning(
                    "%s %s: Cannot correctly calculate top priority time because last range end time and query time are None: %s" %
                    (str(market), str(subchain_id), str(tob_time_ranges)))
            else:
                total_time += tob_time_range[1] - tob_time_range[0]
        else:
            if tob_time_range[0] < query_time:
                if query_time >= tob_time_range[1]:
                    total_time += tob_time_range[1] - tob_time_range[0]
                else:
                    total_time += query_time - tob_time_range[0]

        return total_time

    def clean_up_order_chain(self, order_chain):
        market = order_chain.market()
        for subchain in order_chain.subchains():
            self._market_to_subchain_id_to_time.delete([market, subchain.subchain_id()])



class SubchainTimeAtTOBListener(OrderLevelBookListener):
    """
    Tracks how long a subchain is at the top of book.

    This is designed so it can work with mulitiple order books at once.
    """

    # TODO UNIT TEST

    def __init__(self, logger):
        OrderLevelBookListener.__init__(self, logger)
        self._market_to_subchain_id_to_time = NDeepDict(depth=2, default_value=list) # this a list of tuples (start_time, end_time)
        self._market_to_side_to_prev_tob_subchain_ids = NDeepDict(depth=2, default_value=set)

    def notify_book_update(self, order_book, causing_order_chain, tob_updated):
        """
        Every time an orderbook comes in, look at the top of book subchains. Only need to do it for the side that is 
         updating.

        If the same as the previous top of book price then we just update that
         price's last TOB time.

        If not in previous then create a new time (and make sure previous time, if there is one, is valid)
        If in previous then move on with no change.

        If in open list and not in top of book, then close it with the time of update

        """
        # TODO only run the below code if the top of book for the side in question has changed

        side = causing_order_chain.side()

        use_time = order_book.last_update_time()

        if use_time != causing_order_chain.last_update_time():
            self._logger.warn("Order book update time (%.6f) and causing order chain update time (%.6f) do not match!" %
                              (use_time, causing_order_chain.last_update_time()))

        order_chains = order_book.iter_order_chains_at_price(side, order_book.best_price(side))
        market = order_book.market()
        prev_subchain_ids = self._market_to_side_to_prev_tob_subchain_ids.get((market, side))
        found_subchain_ids = set()
        for order_chain in order_chains:
            subchain_id = order_chain.most_recent_subchain().subchain_id()
            found_subchain_ids.add(subchain_id)
            # if in the previous grouping then do nothing
            # if not in the previous grouping then create a new tuple with None for end time
            if subchain_id not in prev_subchain_ids:
                l = self._market_to_subchain_id_to_time.get((market, subchain_id))
                l.append((use_time, None))

        for prev_subchain_id in prev_subchain_ids:
            # if something previously found wasn't found this time around then we need to close it out
            if prev_subchain_id not in found_subchain_ids:
                l = self._market_to_subchain_id_to_time.get((market, prev_subchain_id))
                l[-1] = (l[-1][0], use_time)

        # set previously found to be the new found
        self._market_to_side_to_prev_tob_subchain_ids.set((market, side), value=found_subchain_ids)

    def time_at_top_of_book(self, market, subchain_id, query_time=None):
        """
        Gets the time a subchain spent at top of book. If subchain was never
         at top of book (or didn't even exit) returns 0.

        if query_time is not None (defaults to None) then that time will be used as the ceiling for the query.
         This means if no end time on the last tuple this will be used as the end time. It also means that if any tuple
          overlaps the query time the query time will be used as a cut off.

        :param market: MarketObjects.Market.Market
        :param subchain_id: subchain identifier
        :param query_time: float. The time since epoch of the query (seconds.milli/microseconds)
        :return: float
        """
        total_time = 0
        tob_time_ranges = self._market_to_subchain_id_to_time.get((market, subchain_id))
        if len(tob_time_ranges) == 0:
            return 0
        for tob_time_range in tob_time_ranges[:-1]:
            if query_time is not None and tob_time_range[0] >= query_time:
                return total_time  # no need to go through the rest of list, found the forced end here
            if tob_time_range[1] is None:
                self._logger.warning("%s %s: Cannot correctly calculate TOB time because a non last range end time is None: %s" %
                                     (str(market), str(subchain_id), str(tob_time_ranges)))
                continue

            if query_time is not None and tob_time_range[1] > query_time:
                total_time += query_time - tob_time_range[0]
                return total_time  # no need to go through the rest of list, found the forced end here

            total_time += tob_time_range[1] - tob_time_range[0]

        tob_time_range = tob_time_ranges[-1]
        if query_time is None:
            if tob_time_range[1] is None:
                self._logger.warning(
                    "%s %s: Cannot correctly calculate TOB time because last range end time and query time are None: %s" %
                    (str(market), str(subchain_id), str(tob_time_ranges)))
            else:
                total_time += tob_time_range[1] - tob_time_range[0]
        else:
            if tob_time_range[0] < query_time:
                if query_time >= tob_time_range[1]:
                    total_time += tob_time_range[1] - tob_time_range[0]
                else:
                    total_time += query_time - tob_time_range[0]

        return total_time

    def clean_up_order_chain(self, order_chain):
        market = order_chain.market()
        for subchain in order_chain.subchains():
            self._market_to_subchain_id_to_time.delete([market, subchain.subchain_id()])