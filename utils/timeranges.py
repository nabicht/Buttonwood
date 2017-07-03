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

from MarketPy.utils import timehelpers


class TimeRange(object):
    def __init__(self, start_time, end_time, payload):
        assert end_time >= start_time, "End time (%.6f) should be greater than or equal to start time (%.6f)." % (end_time, start_time)
        self._start_time = start_time
        self._end_time = end_time
        self._payload = payload

    def start_time(self):
        return self._start_time

    def end_time(self):
        return self._end_time

    def set_end_time(self, time):
        self._end_time = time

    def payload(self):
        return self._payload


class TimeRangeList(object):
    def __init__(self):
        self._list = []

    def __len__(self):
        return len(self._list)

    def set_last_end_time(self, end_time):
        self._list[-1].set_end_time(end_time)

    def last_payload(self):
        return self._list[-1].payload()

    def append(self, time_range_item):
        assert isinstance(time_range_item, TimeRange)
        assert len(self._list) == 0 or (time_range_item.start_time() >= self._list[-1].end_time()), "New item's start time must be >= last item's end time"
        self._list.append(time_range_item)

    def items_in_window(self, window_start_time, window_end_time, enforce_window=True):
        items = []
        for time_range_item in self._list:
            # we care about three options.
            # 1) start_time is between time_range_item start and end, or
            # 2) end_time is between time_range_itme start and end
            # 3) the entire time_range_item falls within the window
            # if the time_range falls within the entire window, you use it and only it, whether enforcing the window or not
            if time_range_item.start_time() >= window_start_time and time_range_item.end_time() <= window_end_time:
                items.append(time_range_item)
            # otherwise, if there is any window overlap then you do the max and mins
            elif (time_range_item.start_time() <= window_start_time <= time_range_item.end_time()) or (
                    time_range_item.start_time() <= window_end_time <= time_range_item.end_time()):
                if enforce_window:
                    items.append(TimeRange(max(window_start_time, time_range_item.start_time()),
                                           min(window_end_time, time_range_item.end_time()),
                                           time_range_item.payload()))
                else:
                    items.append(time_range_item)
        return items

    def trim_to_start_time(self, start_time):
        trim_to = 0
        # Because of the last time range possibly still being "open" (or added to) you can't ever delete the last thing in the list. Enforcing windows makes up for this os don't worry.
        for index, time_range_item in enumerate(self._list):
            if time_range_item.end_time() < start_time:
                trim_to = index + 1
            else:
                break
        if trim_to > 0:  # only bother doing it if no change
            if trim_to >= len(self._list):
                self._list = self._list[len(self._list) - 1:]  # this way we never delete the last item
            else:
                self._list = self._list[trim_to:]
            if len(self._list) == 0:
                raise Exception("List ended up at 0 length! Something not right! (%s)" % str(timehelpers.epoch_to_timestamp(start_time)))  # TODO delete this, should never happen
