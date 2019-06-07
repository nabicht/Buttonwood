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

FAR = 1
FOK = 2
FAK = 3

TIME_IN_FORCE_STRINGS = {FAR: "FAR",
                         FOK: "FOK",
                         FAK: "FAK",
                        }

TIME_IN_FORCE_STR_TO_INT = {v: k for k, v in TIME_IN_FORCE_STRINGS.iteritems()}

def time_in_force_str(int_id):
    assert isinstance(int_id, int)
    if not TIME_IN_FORCE_STRINGS.has_key(int_id):
        raise Exception("%d is an unknown time in force identifier")
    return TIME_IN_FORCE_STRINGS[int_id]

LIMIT = 100
MARKET = 101

ORDER_TYPE_STRINGS = {LIMIT: "Limit",
                      MARKET: "Market",
                     }