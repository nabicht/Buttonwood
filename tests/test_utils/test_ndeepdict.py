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

from nose.tools import *
from buttonwood.utils.dicts import NDeepDict


def test_ndeepdict_2_deep():
    #test with the default value being 0
    d = NDeepDict(2, int)
    #so I should be able to get a dict if I look at the first level
    assert len(d._dict) == 0
    assert isinstance(d._dict["foo"], dict)
    #i should be able to get default 0 if I look 2 levels in
    assert isinstance(d._dict["foo"]["bar"], int)
    assert d._dict["foo"]["bar"] == 0
    #still should be nothing in any layer of the dictionary
    assert len(d._dict) == 1
    d.set(["foo","bar"], value=7)
    assert d._dict["foo"]["bar"] == 7
    assert d.get(["foo", "bar"]) == 7

    assert d.get(["foo", "baz"]) == 0

def test_ndeepdict_3_deep():
    #test with the default value being 0
    d = NDeepDict(3, int)
    #so I should be able to get a dict if I look at the first level
    assert len(d._dict) == 0
    assert isinstance(d._dict["foo"], dict)
    #i should be able to get default 0 if I look 2 levels in
    assert isinstance(d._dict["foo"]["bar"], dict)
    print d._dict["foo"]["bar"]["baz"]
    assert isinstance(d._dict["foo"]["bar"]["baz"], int)
    assert d._dict["foo"]["bar"]["baz"] == 0
    #still should be nothing in any layer of the dictionary
    assert len(d._dict) == 1
    d.set(["foo","bar","baz"], value=7)
    assert d._dict["foo"]["bar"]["baz"] == 7
    assert d.get(["foo", "bar", "baz"]) == 7
    assert d.get(["foo", "bar", "zab"]) == 0
    assert d.get(["great", "googly", "moogly"]) == 0

def test_ndeepdict_8_deep():
    #test with the default value being 0
    d = NDeepDict(8, int)
    assert d.get([1,2,3,4,5,6,7,8]) == 0
    d.set([1,2,3,4,5,6,7,8], value=95)
    assert d.get([1,2,3,4,5,6,7,8]) == 95
    assert d.get([1,2,3,4,5,6,7]) == {8: 95}

def test_get():
    #get should work with any number of keys less than or equal to depth
    depth = 9
    d = NDeepDict(depth, lambda: "some value")
    list_of_keys = []
    #leading up to the last level of depth should all be dict type
    for x in range(0, depth-1):
        list_of_keys.append(x)
        temp_dict = d.get(list_of_keys)
        assert isinstance(temp_dict, dict)
    #the last level the value should be the default value ("some value")
    list_of_keys.append(depth-1)
    assert d.get(list_of_keys) == "some value"

@raises(AssertionError)
def test_get_fails_too_many_keys():
    depth = 8
    d = NDeepDict(depth, lambda: "some value")
    list_of_keys = [x for x in range(depth+1)]
    d.get(list_of_keys)

def test_set():
    depth = 5
    d = NDeepDict(depth, lambda: "some value")
    list_of_keys = [x for x in range(depth)]
    d.set(list_of_keys, value = "some other value")
    assert d.get(list_of_keys) == "some other value"

@raises(AssertionError)
def test_set_too_many_keys():
    depth = 5
    d = NDeepDict(depth, lambda: "some value")
    list_of_keys = [x for x in range(depth+1)]
    d.set(list_of_keys, value = "some other value")

@raises(AssertionError)
def test_set_too_few_keys():
    depth = 5
    d = NDeepDict(depth, lambda: "some value")
    list_of_keys = [x for x in range(depth-1)]
    d.set(list_of_keys, value = "some other value")

@raises(AssertionError)
def test_set_no_keys():
    depth = 5
    d = NDeepDict(depth, lambda: "some value")
    list_of_keys = [x for x in range(depth-1)]
    d.set([], value = "some other value")

def test_increment_int():
    depth = 4
    d = NDeepDict(depth, int)
    list_of_keys = [x for x in range(depth)]
    assert d.get(list_of_keys) == 0
    d.inc(list_of_keys, amount=1)
    assert d.get(list_of_keys) == 1
    d.inc(list_of_keys, amount=1)
    assert d.get(list_of_keys) == 2
    d.inc(list_of_keys, amount=5)
    assert d.get(list_of_keys) == 7

@raises(Exception)
def test_increment_string():
    depth = 4
    d = NDeepDict(depth, str)
    list_of_keys = [x for x in range(depth)]
    assert d.get(list_of_keys) == 0
    d.inc(list_of_keys, amount=1)

def test_decrement_int():
    depth = 4
    d = NDeepDict(depth, int)
    list_of_keys = [x for x in range(depth)]
    assert d.get(list_of_keys) == 0
    d.dec(list_of_keys, amount=1)
    assert d.get(list_of_keys) == -1
    d.dec(list_of_keys, amount=1)
    assert d.get(list_of_keys) == -2
    d.dec(list_of_keys, amount=5)
    assert d.get(list_of_keys) == -7

@raises(Exception)
def test_decrement_string():
    depth = 4
    d = NDeepDict(depth, str)
    list_of_keys = [x for x in range(depth)]
    assert d.get(list_of_keys) == 0
    d.dec(list_of_keys, amount=1)

def test_sum_int():
    depth = 3
    d = NDeepDict(depth, int)
    assert d.sum(["a"]) == 0
    d.set(["a",1,1], value = 5)
    d.set(["a",1,2], value = 5)
    d.set(["a",1,3], value = 5)
    assert d.sum(["a"]) == 15
    assert d.sum(["a",1]) == 15
    assert d.sum(["a",1,2]) == 5
    d.set(["a",2,1], value = 2)
    d.set(["a",2,2], value = 2)
    d.set(["a",2,3], value = 2)
    d.set(["a",2,4], value = 2)
    assert d.sum(["a"]) == 23
    assert d.sum(["a",1]) == 15
    assert d.sum(["a",2]) == 8
    assert d.sum(["a",2,1]) == 2
    assert d.sum(["a",2,2]) == 2
    assert d.sum(["a",2,3]) == 2
    assert d.sum(["a",2,4]) == 2
    d.set(["a",3,1], value = 1)
    d.set(["a",3,2], value = 2)
    d.set(["a",3,3], value = 3)
    d.set(["a",3,4], value = 4)
    assert d.sum(["a",1]) == 15
    assert d.sum(["a",2]) == 8
    assert d.sum(["a",3]) == 10
    assert d.sum(["a"]) == 33
    assert d.sum(["b"]) == 0
