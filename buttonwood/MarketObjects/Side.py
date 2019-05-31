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


class Side(object):
    BID = 0
    ASK = 1

    SIDE_STR = {BID: "Bid", ASK: "Ask"}
    ABBREVIATED_SIDE_STR = {BID: "B", ASK: "A"}

    def __init__(self, bid_or_ask):
        assert bid_or_ask in [0, 1]
        self.__bid_or_ask = bid_or_ask
        self._is_bid = self.__bid_or_ask == self.BID

    def is_bid(self):
        return self._is_bid

    def is_ask(self):
        return not self._is_bid

    def is_other_side(self, side):
        if self.is_bid() and side.is_ask():
            return True
        if self.is_ask() and side.is_bid():
            return True
        return False

    def other_side(self):
        if self.__bid_or_ask == self.BID:
            return ASK_SIDE
        else:
            return BID_SIDE

    def __int__(self):
        if self.__bid_or_ask == self.BID:
            return self.BID
        else:
            return self.ASK

    def __str__(self):
        return self.SIDE_STR[self.__bid_or_ask]

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if self.is_bid() and other.is_bid():
            return True
        if self.is_ask() and other.is_ask():
            return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return self.__bid_or_ask

    def abbreviated_str(self):
        return self.ABBREVIATED_SIDE_STR[self.__bid_or_ask]


BID_SIDE = Side(Side.BID)
ASK_SIDE = Side(Side.ASK)


def get_side(side_str):
    """
    Get's the side based on the string that is passed in. Can return None. Not case sensitive.
 
    Bids: b, bid, buy
    Asks: a, ask, sell
 
    :param side_str: str
    :return: Side (can be None)
    """
    assert type(side_str) is str
    use_str = side_str.lower()
    if use_str in ["b", "bid", "buy"]:
        return BID_SIDE
    if use_str in ["a", "ask", "sell", "offer", "s"]:
        return ASK_SIDE
    return None
