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

from nose.tools import *
from Buttonwood.utils.IDGenerators import MonotonicIntID


def test_monotonicintid():
    #test with the default values (should be 0 as the seed and 1 as the increment
    generator = MonotonicIntID()
    for i in xrange(1,1000):
        assert generator.id() == i

    #test with increment being 2
    generator = MonotonicIntID(increment = 2)
    for i in xrange(2, 1000, 2):
        assert generator.id() == i

    #test with a seed number
    generator = MonotonicIntID(seed=2016113000000)
    for i in range(2016113000000+1, 1000, 2):
        assert generator.id() == i


@raises(AssertionError)
def test_monotonicintid_seed_must_be_int():
    MonotonicIntID(seed = 2.5)

@raises(AssertionError)
def test_monotonicintid_increment_must_be_int():
    MonotonicIntID(increment = 6.5)
