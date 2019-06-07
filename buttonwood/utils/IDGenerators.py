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

import sys
import random


class IDGenerator:

    def __init__(self):
        pass

    def id(self):
        """
        Return the next ID.

        :return: the next ID
        """
        raise NotImplemented("id() to be implemented by the inheriting class.")

    def last_id(self):
        """
        Gets the ID that was returned by the last id() call.

        :return: the last id
        """
        raise NotImplemented("last_id() to be implemented by the inheriting class.")


class MonotonicIntID(IDGenerator):

    def __init__(self, seed=0, increment=1, max_id=sys.maxint):
        """
        A monotonically increasing integer.  increases by the passed the increment value, starting at the seed value.
         The seed value is reserved. It itself will not be returned as an ID

        :param seed:
        :param increment:
        """
        assert isinstance(seed, int) or isinstance(seed, long)
        assert isinstance(increment, int)
        IDGenerator.__init__(self)
        self._seed = seed
        self._increment = increment
        self._value = seed
        self._max_id = max_id

    def id(self):
        self._value += self._increment
        if self._value > self._max_id:
            raise Exception("ID would be greater than %d, which generator cannot handle" % self._max_id)
        return self._value

    def last_id(self):
        return self._value

    def seed(self):
        return self._seed

    def increment(self):
        return self._increment


class RandomPositiveIntID(IDGenerator):

    def __init__(self, floor=1, ceiling=sys.maxint, attempts=20000):
        assert isinstance(floor, int)
        assert isinstance(ceiling, int)
        assert ceiling > floor
        IDGenerator.__init__(self)
        self._floor = floor
        self._ceiling = ceiling
        self._attempts = attempts
        self._ids = set()
        self._id_count = 0 # should be cheaper to do this then do len over and over again
        self._max_id_count = ceiling - floor + 1

    def id(self):
        if self._id_count >= self._max_id_count:
            raise Exception("%d IDs distributed. All possible IDs have been used." % self._id_count)
        for x in xrange(1, self._attempts):
            x = random.randint(self._floor, self._ceiling)
            if x not in self._ids:
                self._ids.add(x)
                self._id_count += 1
                return x
        raise Exception("%d attempts at generating an ID. You need a bigger ID universe or to allow for more attempts" % self._attempts)
