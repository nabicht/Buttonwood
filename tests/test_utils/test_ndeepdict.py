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

import pytest
from buttonwood.utils.dicts import NDeepDict


def test_first_none_default_2_deep():
    d = NDeepDict(2)
    d[['a', 'b']] = 16
    assert d.get(['d', 'e']) is None


def test_none_default_2_deep():
    d = NDeepDict(2)
    d[['a', 'b']] = 16
    assert d.get(['a', 'b']) == 16
    assert d.get(['a', 'c']) is None
    with pytest.raises(KeyError):
        x = d[['a', 'c']]


def test_none_default_1_deep():
    d = NDeepDict(1)
    d[['a']] = 16
    assert d.get(['a']) == 16
    assert d.get(['c']) is None
    with pytest.raises(KeyError):
        x = d[['c']]


def test_1_deep_with_default_standard_access():
    d = NDeepDict(1, int)
    assert len(d) == 0

    # setting something should work
    d['a'] = 1
    assert len(d) == 1

    # getting 'a' should work
    assert d['a'] == 1
    assert d.get('a') == 1

    
    # getting 'b' should return the default of 0
    assert d['b'] == 0
    assert d.get('b') == 0

    # length should now be two because b was created on the get
    assert len(d) == 2
    assert 'b' in d
    assert 'a' in d
    
    # modifying an unknown int should work too
    assert not 'c' in d
    d['c'] += 1
    assert d['c'] == 1

def test_1_deep_with_default_list_access():
    d = NDeepDict(1, int)
    assert len(d) == 0

    # setting something should work
    d[['a']] = 1
    assert len(d) == 1

    # getting 'a' should work
    assert d[['a']] == 1
    assert d.get(['a']) == 1

    
    # getting 'b' should return the default of 0
    assert d[['b']] == 0
    assert d.get(['b']) == 0

    # length should now be two because b was created on the get
    assert len(d) == 2
    assert 'b' in d
    assert 'a' in d
    
    # modifying an unknown int should work too
    assert not 'c' in d
    d[['c']] += 1
    assert d[['c']] == 1


def test_1_deep_with_no_default_standard_access():
    d = NDeepDict(1, None)
    assert len(d) == 0

    # setting something should work
    d['a'] = 1
    assert len(d) == 1

    # getting 'a' should work
    assert d['a'] == 1
    assert d.get('a') == 1

    # getting 'b' should return the default of None
    with pytest.raises(KeyError):
        d['b']
    assert d.get('b') is None

    # length should still be 1 because getting 'b' shouldn't have added anything
    assert len(d) == 1
    assert 'b' not in d
    assert 'a' in d


def test_1_deep_with_no_default_list_access():
    d = NDeepDict(1, None)
    assert len(d) == 0

    # setting something should work
    d[['a']] = 1
    assert len(d) == 1

    # getting 'a' should work
    assert d[['a']] == 1
    assert d.get(['a']) == 1

    # getting 'b' should return the default of None
    with pytest.raises(KeyError):
        d[['b']]
        d.get(['b'])

    # length should still be 1 because getting 'b' shouldn't have added anything
    assert len(d) == 1
    assert 'b' not in d
    assert 'a' in d
    

def test_2_deep_with_default_standard_access():
    d = NDeepDict(2, int)
    assert len(d) == 0, "Nothing is in new dict so length is 0"
    assert len(d['a']) == 0, "Nothing is in the second level dict so should be 0"
    assert len(d) == 1, "Looking for length of 'a' above should have added it to the first level dict, so now first level length is 0"

    assert d['b'] == {}
    assert 'b' in d

    assert len(d['b']) == 0
    d['b']['level2-a'], "Getting a key for first time in second level dict, so should create an item in b"
    assert len(d['b']) == 1
    assert d['b']['level2-a'] == 0
    d['b']['level2-b'] += 50
    assert d['b']['level2-b'] == 50
    assert d.get('b').get("level2-b") == 50


def test_2_deep_with_default_list_access():
    d = NDeepDict(2, int)
    assert len(d) == 0, "Nothing is in new dict so length is 0"
    assert len(d[['a']]) == 0, "Nothing is in the second level dict so should be 0"
    assert len(d) == 1, "Looking for length of 'a' above should have added it to the first level dict, so now first level length is 0"

    assert d['b'] == {}
    assert 'b' in d

    assert len(d[['b']]) == 0
    d[['b','level2-a']], "Getting a key for first time in second level dict, so should create an item in b"
    assert len(d[['b']]) == 1
    assert d[['b','level2-a']] == 0
    d[['b', 'level2-b']] += 50
    assert d[['b','level2-b']] == 50
    assert d.get(['b',"level2-b"]) == 50


def test_4_deep_create_at_once_standard_access():
    d = NDeepDict(4)
    assert len(d) == 0, "Starts completely empty"
    d["level1"]["level2"]["level3"]["level4"] = 5
    assert "level1" in d
    assert "level2" in d["level1"]
    assert "level3" in d["level1"]["level2"]
    assert "level4" in d["level1"]["level2"]["level3"]
    assert d["level1"]["level2"]["level3"]["level4"] == 5


def test_4_deep_create_at_once_list_access():
    d = NDeepDict(4)
    assert len(d) == 0, "Starts completely empty"
    d[["level1", "level2", "level3", "level4"]] = 5
    assert len(d) == 1
    assert "level1" in d
    assert "level2" in d[["level1"]]
    assert "level3" in d[["level1", "level2"]]
    assert "level4" in d[["level1", "level2", "level3"]]
    assert len(d) ==  1
    assert d[["level1", "level2", "level3", "level4"]] == 5


def test_1_deep_del_standard_access():
    d = NDeepDict(4)
    d[['a1','a1b1','a1b1c1']] = "test value"
    d[['a2','a2b1','a2b1c1']] = "test value 2"
    d[['a1','a1b2','a1b2c1']] = "test value 3"
    d[['a1','a1b1','a1b1c2']] = "test value 4"
    d[['a1','a1b1','a1b1c3']] = "test value 5"
    assert 'a1b1c2' in d['a1']['a1b1']
    del d[['a1', 'a1b1', 'a1b1c2']]
    assert 'a1b1c2' not in d['a1']['a1b1'], "was deleted so should be gone"
    assert 'a1b1c1' in d['a1']['a1b1'], "was not deleted so should be there"
    assert 'a1b1c3' in d['a1']['a1b1'], "was not deleted so should be there"
    assert 'a2b1c1' in d['a2']['a2b1'], "was not deleted so should be there"
    assert 'a1b2c1' in d['a1']['a1b2'], "was not deleted so should be there"


def test_one_level_contains_none_default():
    d = NDeepDict(1)
    d[['a']] = 1
    assert ['a'] in d
    assert 'a' in d
    assert ['b'] not in d
    assert 'b' not in d


def test_two_level_contains_none_default():
    d = NDeepDict(2)
    d[['a', 'b']] = 1
    assert ['a', 'b'] in d
    assert ['a', 'c'] not in d
    assert ['a'] in d
    assert ['b'] not in d
    assert 'a' in d
    assert 'b' not in d
