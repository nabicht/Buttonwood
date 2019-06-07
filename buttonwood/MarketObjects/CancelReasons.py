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


USER_CANCEL = 1
SYSTEM_CANCEL = 2

CANCEL_TYPES_STRINGS = {USER_CANCEL: "User requested cancel.",
                        SYSTEM_CANCEL: "System requested cancel.",
                       }

MARKET_CLOSED = 100
SELF_TRADE = 101
CANCEL_REPLACE_TO_ZERO = 102
FAK_REMAINDER = 103
FOK_CANCEL = 104
UNSPECIFIED = 105
USER_REQUESTED = 106

CANCEL_REASON_STRINGS = {MARKET_CLOSED: "Closing market canceled order.",
                         SELF_TRADE: "Self trade prevention requested cancel.",
                         CANCEL_REPLACE_TO_ZERO: "Cancel replace to zero (0)",
                         FAK_REMAINDER: "FAK Remainder",
                         FOK_CANCEL: "Fill or Kill No Fill",
                         UNSPECIFIED: "Unspecified",
                         USER_REQUESTED: "User requested cancel"
                        }

CANCEL_REASON_INTS = {v: k for k, v in CANCEL_REASON_STRINGS.iteritems()}