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

from Buttonwood.MarketObjects import Side
from Buttonwood.MarketObjects.Side import BID_SIDE
from Buttonwood.MarketObjects.Side import ASK_SIDE


def test_bid_or_ask_constants():
   # This is simply to test that the constants don't get changed around. A unit test breaking will at least
   #  alert someone to it being a bad idea.
   assert Side.Side.BID == 0
   assert Side.Side.ASK == 1


def test_bid_side_constant():
   assert BID_SIDE.is_bid()
   assert BID_SIDE.is_ask() == False
   assert BID_SIDE.other_side().is_ask()
   assert BID_SIDE.other_side().is_bid() == False
   assert BID_SIDE.is_other_side(ASK_SIDE)
   assert BID_SIDE.is_other_side(Side.Side(Side.Side.ASK))
   assert BID_SIDE.abbreviated_str() == 'B'
   assert str(BID_SIDE) == "Bid"
   assert BID_SIDE == Side.Side(Side.Side.BID)
   assert BID_SIDE != Side.Side(Side.Side.ASK)
   assert int(BID_SIDE) == Side.Side.BID

def test_bid_creation():
   bid_side = Side.Side(Side.Side.BID)
   assert bid_side.is_bid()
   assert bid_side.is_ask() == False
   assert bid_side.other_side().is_ask()
   assert bid_side.other_side().is_bid() == False
   assert bid_side.is_other_side(ASK_SIDE)
   assert bid_side.is_other_side(Side.Side(Side.Side.ASK))
   assert bid_side.abbreviated_str() == 'B'
   assert str(bid_side) == "Bid"
   assert bid_side == Side.Side(Side.Side.BID)
   assert bid_side != Side.Side(Side.Side.ASK)
   assert int(bid_side) == Side.Side.BID

def test_ask_side_constant():
   assert ASK_SIDE.is_bid() == False
   assert ASK_SIDE.is_ask()
   assert ASK_SIDE.other_side().is_ask() == False
   assert ASK_SIDE.other_side().is_bid() == True
   assert ASK_SIDE.is_other_side(BID_SIDE)
   assert ASK_SIDE.is_other_side(Side.Side(Side.Side.BID))
   assert ASK_SIDE.abbreviated_str() == 'A'
   assert str(ASK_SIDE) == "Ask"
   assert ASK_SIDE == Side.Side(Side.Side.ASK)
   assert ASK_SIDE != Side.Side(Side.Side.BID)
   assert int(ASK_SIDE) == Side.Side.ASK

def test_ask_creation():
   ask_side = Side.Side(Side.Side.ASK)
   assert ask_side.is_bid() == False
   assert ask_side.is_ask()
   assert ask_side.other_side().is_ask() == False
   assert ask_side.other_side().is_bid() == True
   assert ask_side.is_other_side(BID_SIDE)
   assert ask_side.is_other_side(Side.Side(Side.Side.BID))
   assert ask_side.abbreviated_str() == 'A'
   assert str(ask_side) == "Ask"
   assert ask_side == Side.Side(Side.Side.ASK)
   assert ask_side != Side.Side(Side.Side.BID)
   assert int(ask_side) == Side.Side.ASK

def test_get_side():
   assert Side.get_side("b") == Side.BID_SIDE
   assert Side.get_side("B") == Side.BID_SIDE
   assert Side.get_side("bid") == Side.BID_SIDE
   assert Side.get_side("bId") == Side.BID_SIDE
   assert Side.get_side("BID") == Side.BID_SIDE
   assert Side.get_side("Buy") == Side.BID_SIDE
   assert Side.get_side("BUY") == Side.BID_SIDE
   assert Side.get_side("buy") == Side.BID_SIDE
   assert Side.get_side("A") == Side.ASK_SIDE
   assert Side.get_side("a") == Side.ASK_SIDE
   assert Side.get_side("ask") == Side.ASK_SIDE
   assert Side.get_side("asK") == Side.ASK_SIDE
   assert Side.get_side("Offer") == Side.ASK_SIDE
   assert Side.get_side("offer") == Side.ASK_SIDE
   assert Side.get_side("oFFer") == Side.ASK_SIDE
   assert Side.get_side("sell") == Side.ASK_SIDE
   assert Side.get_side("SELL") == Side.ASK_SIDE
   assert Side.get_side("SEll") == Side.ASK_SIDE
   assert Side.get_side("s") == Side.ASK_SIDE
   assert Side.get_side("S") == Side.ASK_SIDE
   assert Side.get_side("r") is None
   assert Side.get_side("not a valid string") is None
   assert Side.get_side(" b") is None

