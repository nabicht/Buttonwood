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

from buttonwood.utils import timehelpers


class TimeRange(object):
    def __init__(self, start_time, payload):
        self._start_time = start_time
        self._end_time = None
        self._payload = payload

    def start_time(self):
        return self._start_time

    def end_time(self):
        return self._end_time

    def set_end_time(self, time):
        if time < self._start_time:
            raise Exception("%.6f is less than start time: %.6f" % (self._start_time, time))
        self._end_time = time

    def is_closed(self):
        return self._end_time is not None

    def payload(self):
        return self._payload

    def __str__(self):
        return "%.6f - %.6f : %s" % (self.start_time(), self.end_time(), self.payload())


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
        assert len(self._list) == 0 or (not self._list[-1].is_closed()) or (time_range_item.start_time() >= self._list[-1].end_time()), "New item's start time must be >= last item's end time"
        if len(self._list) > 0 and not self._list[-1].is_closed():
            self.set_last_end_time(time_range_item.start_time())
        self._list.append(time_range_item)

    def items_in_window(self, window_start_time, window_end_time, enforce_window=True):
        items = []
        for time_range_item in self._list:
            # we care about three options.
            # 1) start_time is between time_range_item start and end, or
            # 2) end_time is between time_range_itme start and end
            # 3) the entire time_range_item falls within the window
            # if the time_range falls within the entire window, you use it and only it, whether enforcing the window or not
            tr_start_time = time_range_item.start_time()
            tr_end_time = time_range_item.end_time()
            if tr_start_time >= window_start_time and time_range_item.is_closed() and tr_end_time <= window_end_time:
                items.append(time_range_item)
            # otherwise, if there is any window overlap then you do the max and mins
            elif time_range_item.is_closed() and \
                    ((time_range_item.start_time() <= window_start_time <= time_range_item.end_time()) or
                     (time_range_item.start_time() <= window_end_time <= time_range_item.end_time())):
                if enforce_window:
                    use_start_time = max(window_start_time, time_range_item.start_time())
                    use_end_time = min(window_end_time, time_range_item.end_time())
                    tr = TimeRange(use_start_time, time_range_item.payload())
                    tr.set_end_time(use_end_time)
                    items.append(tr)
                else:
                    items.append(time_range_item)
            elif not time_range_item.is_closed() and tr_start_time < window_end_time:
                if enforce_window:
                    use_start_time = max(window_start_time, time_range_item.start_time())
                    use_end_time = window_end_time
                    tr = TimeRange(use_start_time, time_range_item.payload())
                    tr.set_end_time(use_end_time)
                    items.append(tr)
                else:
                    items.append(time_range_item)
            # TODO should make sure that anything else is ust outside of the window and closed
        return items

    def trim_to_start_time(self, start_time):
        trim_to = 0
        for index, time_range_item in enumerate(self._list):
            if time_range_item.is_closed() and time_range_item.end_time() < start_time:
                trim_to = index + 1
            else:
                break
        if trim_to > 0:  # only bother doing it if no change
            if trim_to >= len(self._list):
                self._list = self._list[len(self._list) - 1:]  # this way we never delete the last item (# TODO  this might be redundant safety)
            else:
                self._list = self._list[trim_to:]
            if len(self._list) == 0:
                raise Exception("List ended up at 0 length! Something not right! (%s)" % str(timehelpers.epoch_to_timestamp(start_time)))  # TODO delete this, should never happen
