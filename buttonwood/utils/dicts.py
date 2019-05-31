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

from collections import defaultdict

"""
this isn't a true dict, but it wraps a dict and allows for easily initializing
 and using (in simple cases), an n deep dict, where the structure is:
  key1 -> key2 ->.... -> keyn -> payload
"""


def _establish_level(levels, default_value):
    if levels < 2:
        return defaultdict(default_value)
    return defaultdict(lambda: _establish_level(levels - 1, default_value))


class NDeepDict:
    def __init__(self, depth, default_value=None):
        assert depth > 0
        if default_value is None:
            default_value = lambda: None
        assert callable(default_value), "default_value must be not defined or callable"
        self._depth = depth
        self._dict = _establish_level(depth, default_value)

    def get(self, keys):
        """
        Pulling data out of the dict. Must have a number of args that is less
         than or equal to the depth of the dict.

        This returns what the args map to. If the same number of args as the
         defined depth it returns whatever object is in the final payload.
         Otherwise it returns the dict that the given keys lead to.

        :param keys: a list of the keys you want to use for accessing the dict.
        :return: the value of the passed in args
        """
        assert len(keys) <= self._depth, "To access a value out of dict hierarchy, number of keys must be less than or equal to depth of dict"
        result = self._dict
        for key in keys:
            result = result[key]
        return result

    def set(self, keys, value=None):
        """
        Setting data in the dict. This requires all keys that lead to final
         payload, so the number of args must equal the defined depth.

        Value defaults to None and if None then nothing happens.

        :param keys: a list of the keys you want to use for accessing the dict
        :param value: the value you want to set payload to. If None (the default), then nothing happens
        """
        assert len(keys) == self._depth, "Number of arguments must equal depth of dict to set a value"
        result = self._dict
        for key in keys[:-1]:
            result = result[key]
        result[keys[-1]] = value

    def inc(self, keys, amount=1):
        """
        Increment the payload of the dict. Note, if the payload isn't a numeric
         then this fails. This requires all keys that lead to final
         payload, so the number of args must equal the defined depth.

        amount is the amount to increment. It defaults to 1.

        :param keys: the keys you want to use for accessing the dict
        :param amount: amount to increment by, it defaults to 1.
        """
        assert len(keys) == self._depth, "Number of arguments must equal depth of dict to increment the payload value"
        result = self._dict
        for key in keys[:-1]:
            result = result[key]
        result[keys[-1]] += amount

    def dec(self, keys, amount=1):
        """
        Decrement the payload of the dict. Note, if the payload isn't a numeric
         then this fails. This requires all keys that lead to final
         payload, so the number of args must equal the defined depth.

        amount is the amount to decrement. It defaults to 1.

        :param keys: the keys you want to use for accessing the dict
        :param amount: amount to increment by, it defaults to 1.
        """
        assert len(keys) == self._depth, "Number of arguments must equal depth of dict to decrement the payload value"
        result = self._dict
        for key in keys[:-1]:
            result = result[key]
        result[keys[-1]] -= amount

    def _sum(self, v):
        total = 0
        if isinstance(v, dict):
            for value in v.itervalues():
                total += self._sum(value)
        else:
            total += v
        return total

    def sum(self, keys):
        """
        Sums the payloads that fall under the dict the keys return. If the keys
         return just a payload, the sum is just that payload.

        WARNING: If += doesn't work on the payload this will fail.

        :param keys: the keys you want to use for accessing the dict
        :return: the sum
        """
        assert len(
            keys) <= self._depth, "To sum values in dict hierarchy, number of keys must be less than or equal to depth of dict"
        return self._sum(self.get(keys))

    def delete(self, keys):
        # TODO document
        # TODO unit test
        assert len(keys) == self._depth, "Number of arguments must equal depth of dict to decrement the payload value"
        result = self._dict
        for key in keys[:-1]:
            result = result[key]
        if keys[-1] in result:
            del result[keys[-1]]

    def __str__(self):
        return str(self._dict)
