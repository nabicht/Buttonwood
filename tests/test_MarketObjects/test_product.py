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

from cdecimal import Decimal
from Buttonwood.MarketObjects.Product import Product
from Buttonwood.MarketObjects.Price import Price


def test_product_creation():
    prod = Product("MSFT", "Microsoft", Decimal("0.01"), "0.01")
    assert prod.symbol() == "MSFT"
    assert prod.name() == "Microsoft"
    assert prod.min_price_increment() == Decimal("0.01")
    assert prod.min_price_increment_value() == Decimal("0.01")


def test_function_shortcuts_equal():
    prod = Product("MSFT", "Microsoft", Decimal("0.01"), "0.05")
    assert prod.mpi_value() - prod.min_price_increment_value() == 0
    assert prod.min_price_increment() - prod.mpi() == 0
    prod = Product("PROD", "Some Product", Decimal("4"), Decimal("73"))
    assert prod.mpi_value() == prod.min_price_increment_value()
    assert prod.min_price_increment() == prod.mpi()


def test_basic_equality():
    prod1 = Product("msft", "mICRoSOFT", Decimal("0.01"), Decimal("0.01"))
    prod2 = Product("MSFT", "Microsoft", Decimal("0.01"), Decimal("0.01"))
    assert prod1 == prod2
    assert (prod1 != prod2) is False

    prod1 = Product("AAPL", "Apple", Decimal("0.01"), Decimal("0.01"))
    prod2 = Product("MSFT", "Microsoft", Decimal("0.01"), Decimal("0.01"))
    assert (prod1 == prod2) is False
    assert prod1 != prod2

    prod1 = Product("msft", "mICRoSOFT", Decimal("0.01"), Decimal("0.03"))
    prod2 = Product("MSFT", "Microsoft", Decimal("0.01"), Decimal("0.01"))
    assert (prod1 == prod2) is False
    assert prod1 != prod2

    prod1 = Product("msft", "mICRoSOFT", Decimal("0.1"), Decimal("0.01"))
    prod2 = Product("MSFT", "Microsoft", Decimal("0.01"), Decimal("0.01"))
    assert (prod1 == prod2) is False
    assert prod1 != prod2


def test_equality_identifiers():
    prod1 = Product("msft", "mICRoSOFT", Decimal("0.01"), Decimal("0.01"))
    prod2 = Product("MSFT", "Microsoft", Decimal("0.01"), Decimal("0.01"))

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


def test_price_validation():
    p = Price("23.455")
    prod = Product("MSFT", "Microsoft", Decimal("0.01"), Decimal("0.01"))
    assert prod.is_valid_price(p) is False

    p = Price("23.45")
    prod = Product("MSFT", "Microsoft", Decimal("0.005"), Decimal("0.01"))
    assert prod.is_valid_price(p)

    p = Price("23.455")
    prod = Product("MSFT", "Microsoft", Decimal("0.005"), Decimal("0.01"))
    assert prod.is_valid_price(p)

    p = Price("23.45")
    prod = Product("GEU5", "Eurdollar Sep 2015", Decimal("1"), Decimal("12.50"))
    assert prod.is_valid_price(p) is False

    p = Price("23.45")
    prod = Product("GEU5", "Eurdollar Sep 2015", Decimal(".45"), Decimal(".45"))
    assert prod.is_valid_price(p) is False
