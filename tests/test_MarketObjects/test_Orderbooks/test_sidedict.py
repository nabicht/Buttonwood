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

from buttonwood.MarketObjects.OrderBooks.OrderLevelBook import SideDict
from buttonwood.MarketObjects.Price import Price

def test_creation():
    sd = SideDict()
    # no prices means no min and max
    assert sd.min_price() is None
    assert sd.max_price() is None

    # should not be sort_dirty and list should be empty
    assert sd._sort_dirty == False
    assert len(sd.sorted_prices()) == 0

def test_sort_dirty_flag():
    # a delete and an add of a new price should make it dirty
    sd = SideDict()
    assert sd._sort_dirty == False

    # adding makes dirty
    sd[Price("100.0")] = 1
    assert sd._sort_dirty

    # adding again at same price shouldn't change that
    sd[Price("100.0")] = 2
    assert sd._sort_dirty

    # because the function that gets sorted prices hasn't been called yet, the internal list should still be empty
    assert sd._sorted == []

    # adding a new price shouldn't change flag, should still be dirty and list still empty
    sd[Price("101.0")] = 1
    assert sd._sort_dirty
    assert sd._sorted == []

    # deleting at this point shouldn't change flag
    del sd[Price("101.0")]
    assert sd._sort_dirty
    assert sd._sorted == []

    # getting a sorted list should set flag to not dirty and list should be sorted now
    l = sd.sorted_prices()
    assert len(l) == 1
    assert l[0] == Price("100.0")
    assert len(sd._sorted) == 1
    assert sd._sorted[0] == Price("100.0")
    assert sd._sort_dirty == False

    # do a bunch of ads and we should be dirty after each one and len of sorted should not change
    #  because list not updated
    length = len(sd._sorted)
    sd[Price("101.0")] = 1
    assert sd._sort_dirty
    assert len(sd._sorted) == length
    sd[Price("102.0")] = 1
    assert sd._sort_dirty
    assert len(sd._sorted) == length
    sd[Price("103.0")] = 1
    assert sd._sort_dirty
    assert len(sd._sorted) == length
    sd[Price("104.0")] = 1
    assert sd._sort_dirty

    # get sorted and flag should go back to false
    l = sd.sorted_prices()
    assert sd._sort_dirty == False
    assert len(sd._sorted) == 5

    # adding a price that already exists should keep dirty flag dirty
    sd[Price("104.0")] = 1
    assert sd._sort_dirty == False


def test_sorting():
    # a delete and an add of a new price should make it dirty
    sd = SideDict()
    # sorted should be empty
    l = sd.sorted_prices()
    assert len(l) == 0

    # add one
    sd[Price("33.00")] = 1
    l = sd.sorted_prices()
    assert len(l) == 1
    r = sd.sorted_prices(reverse=True)
    # should be same as forward with only one
    assert len(r) == 1
    assert l == r

    # add 4 more
    sd[Price("32.00")] = 2
    sd[Price("33.5")] = 3
    sd[Price("36.00")] = 4
    sd[Price("15.00")] = 5
    sd[Price("17.00")] = 3
    sd[Price("31.00")] = 5

    # sorted should be 7 long
    l = sd.sorted_prices()
    assert len(l) == 7
    # test for sorted
    assert l[0] == Price("15.00")
    assert l[1] == Price("17.00")
    assert l[2] == Price("31.00")
    assert l[3] == Price("32.00")
    assert l[4] == Price("33.0")
    assert l[5] == Price("33.50")
    assert l[6] == Price("36.0")

    l = sd.sorted_prices(reverse=True)
    assert len(l) == 7
    # test for sorted in reverse
    assert l[6] == Price("15.00")
    assert l[5] == Price("17.00")
    assert l[4] == Price("31.00")
    assert l[3] == Price("32.00")
    assert l[2] == Price("33.0")
    assert l[1] == Price("33.50")
    assert l[0] == Price("36.0")

    # sort regular again to make sure can do that after going in reverse
    l = sd.sorted_prices()
    assert len(l) == 7
    # test for sorted
    assert l[0] == Price("15.00")
    assert l[1] == Price("17.00")
    assert l[2] == Price("31.00")
    assert l[3] == Price("32.00")
    assert l[4] == Price("33.0")
    assert l[5] == Price("33.50")
    assert l[6] == Price("36.0")

    # insert another and test the sorting again for good measure
    sd[Price("19.75")] = 7

    # test reverse set to false, should be like not setting it at all
    l = sd.sorted_prices(reverse=False)
    l2 = sd.sorted_prices()
    assert l == l2
    assert len(l) == 8
    # test for sorted
    assert l[0] == Price("15.00")
    assert l[1] == Price("17.00")
    assert l[2] == Price("19.75")
    assert l[3] == Price("31.00")
    assert l[4] == Price("32.00")
    assert l[5] == Price("33.0")
    assert l[6] == Price("33.50")
    assert l[7] == Price("36.0")

    # now delete a couple and sort
    del sd[Price("15.00")]
    del sd[Price("33.00")]

    l = sd.sorted_prices(reverse=True)
    assert l[5] == Price("17.00")
    assert l[4] == Price("19.75")
    assert l[3] == Price("31.00")
    assert l[2] == Price("32.00")
    assert l[1] == Price("33.50")
    assert l[0] == Price("36.0")

def test_max_price_when_adding():
    # don't care what the value is in these tests so just setting it to ints
    sd = SideDict()
    # in empty dict the max price is none
    assert sd.max_price() is None

    # the first added price should be the max price
    sd[Price("100.0")] = 1
    assert sd.max_price() == Price("100.0")

    # adding a price that is less than 100 should not change max price
    sd[Price("99.99")] = 1
    assert sd.max_price() == Price("100.0")

    # adding a price greater than 100 should change the max price
    sd[Price("100.001")] = 1
    assert sd.max_price() == Price("100.001")

    # adding higher still should change max again
    sd[Price("100.02")] = 1
    assert sd.max_price() == Price("100.02")

    # adding the same price as the highest should not change the max
    sd[Price("100.02")] = 2
    assert sd.max_price() == Price("100.02")

    # adding the same price that is not the highest should not change the max
    sd[Price("100.001")] = 1
    assert sd.max_price() == Price("100.02")

def test_max_price_when_deleting():
    # don't care what the value is in these tests so just setting it to ints
    sd = SideDict()
    # in empty dict the max price is none
    assert sd.max_price() is None

    # add a few to test when deleting
    sd[Price("100.0")] = 1
    sd[Price("99.99")] = 1
    sd[Price("100.001")] = 1
    sd[Price("100.01")] = 1
    sd[Price("100.02")] = 1

    # at this point max price is 100.02
    assert sd.max_price() == Price("100.02")

    # if I delete the highest price, the max should change
    del sd[Price("100.02")]
    assert sd.max_price() == Price("100.01")

    # deleting a middle price shouldn't change
    del sd[Price("100.0")]
    assert sd.max_price() == Price("100.01")

    # deleting the worst price should't change it
    del sd[Price("99.99")]
    assert sd.max_price() == Price("100.01")

    # deleting highest price should put at best one left
    del sd[Price("100.01")]
    assert sd.max_price() == Price("100.001")

    # deleting last price should result in none
    del sd[Price("100.001")]
    assert sd.max_price() is None

def test_min_price_when_adding():
    # don't care what the value is in these tests so just setting it to ints
    sd = SideDict()
    # in empty dict the min price is none
    assert sd.min_price() is None

    # the first added price should be the min price
    sd[Price("100.0")] = 1
    assert sd.min_price() == Price("100.0")

    # adding a price that is less than 100 should  change min price
    sd[Price("99.99")] = 1
    assert sd.min_price() == Price("99.99")

    # adding a price greater than 100 should change the min price
    sd[Price("100.001")] = 1
    assert sd.min_price() == Price("99.99")

    # adding a price that is second lowest shouldn't change
    sd[Price("99.9999")] = 1
    assert sd.min_price() == Price("99.99")

    # adding a lower price should change the min
    sd[Price("98.5")] = 1
    assert sd.min_price() == Price("98.5")

    # adding lower still should change min again
    sd[Price("98.4")] = 1
    assert sd.min_price() == Price("98.4")

    # adding same as min shouldn't change min
    sd[Price("98.4")] = 2
    assert sd.min_price() == Price("98.4")

    # adding smae not min shoudlnt' chagne the min
    sd[Price("98.4")] = 2
    assert sd.min_price() == Price("98.4")

def test_min_price_when_deleting():
    # don't care what the value is in these tests so just setting it to ints
    sd = SideDict()
    # in empty dict the max price is none
    assert sd.max_price() is None

    # add a few to test when deleting
    sd[Price("100.0")] = 1
    sd[Price("99.99")] = 1
    sd[Price("100.001")] = 1
    sd[Price("100.01")] = 1
    sd[Price("100.02")] = 1

    # at this point MIN price is 99.99
    assert sd.min_price() == Price("99.99")

    # if I delete the lowest price, the min should change
    del sd[Price("99.99")]
    assert sd.min_price() == Price("100.0")

    # deleting a middle price shouldn't change
    del sd[Price("100.01")]
    assert sd.min_price() == Price("100.00")

    # deleting the highest price should't change it
    del sd[Price("100.02")]
    assert sd.min_price() == Price("100.00")

    # deleting lowest price should put at only one left
    del sd[Price("100.0")]
    assert sd.min_price() == Price("100.001")

    # deleting last price should result in none
    del sd[Price("100.001")]
    assert sd.min_price() is None