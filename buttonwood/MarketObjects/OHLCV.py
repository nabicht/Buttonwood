
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

from buttonwood.MarketObjects.Price import Price

class OHLC(object):

    def __init__(self, start_time, stop_time, open, close, low, high):
        assert low <= high, "High cannot be lower than low."
        self._start_time = start_time
        self._stop_time = stop_time
        self._open = open
        self._close = close
        self._low = low
        self._high = high

    def open(self):
        return self._open

    def close(self):
        return self._close

    def high(self):
        return self._high

    def low(self):
        return self._low

    def __eq__(self, other):
        if other is None or not isinstance(other, OHLC):
            return False
        return self.open() == other.open() and self.close() == other.close() and self.low() == other.low() and self.high() == other.high()

    def __ne__(self, other):
        return not self.__eq__(other)


class OHLCPricesAndVolume(OHLC):

    def __init__(self, open, close, low, high, volume):
        assert volume >=0, "Volume should not be a negative number."
        OHLC.__init__(self, open, close, low, high)
        self._volume = volume

    def volume(self):
        return self._volume


