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

import json


class Endpoint(object):

    def __init__(self, name, abbreviation=None):
        """
        Contains all the information needed about an Endpoint.

        An endpoint is the *point* where an order *ends*. Some synonyms might be:
         * Liquidity pool
         * ECN
         * Exchange
         * Venue

        The name should be completely unique value for identifying the endpoint. It will be used as an identifying hash.

        The abbreviation can be whatever the user prefers but will be more helpful if unique among endpoints

        A product + an endpoint == a trade-able asset

        :param name: str. the name of the endpoint.
        :param abbreviation: str. an abbreviation of the endpoint. Optional. Defaults to name.
        """
        assert isinstance(name, str)
        assert abbreviation is None or isinstance(abbreviation, str)
        self._name = name
        self._abbr = abbreviation if abbreviation is not None else name
        # since this should be an immutable object we can go ahead and create the following
        #  if someone wants to overwrite how the name or abbreviation gets formatted they'll need to overwrite __str__
        #  and to_json
        self.__json = {"name": self._name, "abbreviation": self._abbr}
        self.__str = json.dumps(self.__json)
        self.__hash = hash(name)

    def name(self):
        """
        Get the name of the Endpoint

        :return: str.
        """
        return self._name

    def abbreviation(self):
        """
        Get the abbreviation of the Endpoint

        :return:
        """
        return self._abbr

    def __eq__(self, other):
        return isinstance(other, Endpoint) and other.__hash__() == self.__hash__()

    def __ne__(self, other):
        return not self.__eq__(other)

    def __str__(self):
        return self.__str

    def to_json(self):
        return self.__json

    def __hash__(self):
        return self.__hash
