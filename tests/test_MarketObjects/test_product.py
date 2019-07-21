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

import json
from buttonwood.MarketObjects.Product import Product


def test_product_creation():
    prod = Product("MSFT", "Microsoft")
    assert prod.symbol() == "MSFT"
    assert prod.name() == "Microsoft"

def test_basic_equality():
    prod1 = Product("msft", "mICRoSOFT")
    prod2 = Product("MSFT", "Microsoft")
    assert prod1 == prod2
    assert (prod1 != prod2) is False

    prod1 = Product("AAPL", "Apple")
    prod2 = Product("MSFT", "Microsoft")
    assert (prod1 == prod2) is False
    assert prod1 != prod2

    prod1 = Product("msft", "mICRoSOFT")
    prod2 = Product("MSFT", "Microsoft")
    assert (prod1 == prod2) is True
    assert prod1 == prod2

    prod1 = Product("msft", "mICRoSOFT")
    prod2 = Product("MSFT", "Microsoft")
    prod2.set_identifier("CUSIP", "20200")
    prod1.set_identifier("CUSIP", "23222")
    assert (prod1 == prod2) is False
    assert prod1 != prod2


def test_equality_identifiers():
    prod1 = Product("msft", "mICRoSOFT")
    prod2 = Product("MSFT", "Microsoft")

    # identifier doesn't exist in other then then we can't assume inequality
    prod1.set_identifier("cusip", "XTR2302")
    prod2.set_identifier("BBID", "weq34")
    assert prod1 == prod2
    assert (prod1 != prod2) is False

    # same identifier exists in both with same value, so should be equal
    prod2.set_identifier("CUSIP", "XTR2302")
    assert prod1 == prod2
    assert (prod1 != prod2) is False

    # same identifier exists in both with different values, then not equal
    prod1.set_identifier("bbid", "asads222")
    assert (prod1 == prod2) is False
    assert prod1 != prod2


def test_to_json():
    # this is only testing that it isn't broken / bad code
    prod1 = Product("msft", "mICRoSOFT")
    json.dumps(prod1.to_json())


def test_to_detailed_json():
    # this is only testing that it isn't broken / bad code
    prod1 = Product("msft", "mICRoSOFT")
    prod1.set_identifier("CUSIP", "12345")
    prod1.set_identifier("internal_id", "8u98792")
    json.dumps(prod1.to_detailed_json())

