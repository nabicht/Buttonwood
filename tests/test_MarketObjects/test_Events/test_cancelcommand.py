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

from nose.tools import *
from MarketPy.MarketObjects.Events.OrderEvents import CancelCommand
from MarketPy.MarketObjects import CancelReasons
from MarketPy.MarketObjects.Product import Product

PRODUCT = Product("MSFT", "Microsoft", "0.01", "0.01")

def test_creation():
    cancel = CancelCommand(12, 324893458.324313, "342adf24441", "user_x", PRODUCT, CancelReasons.SYSTEM_CANCEL)
    assert cancel.cancel_type() == CancelReasons.SYSTEM_CANCEL
    assert cancel.cancel_type_str() == CancelReasons.CANCEL_TYPES_STRINGS[CancelReasons.SYSTEM_CANCEL]
    assert cancel.product() == PRODUCT
    assert cancel.user_id() == "user_x"
    assert cancel.timestamp() == 324893458.324313
    assert cancel.event_id() == 12

