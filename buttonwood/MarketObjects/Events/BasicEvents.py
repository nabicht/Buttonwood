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


class BasicEvent(object):

    def __init__(self, event_id, timestamp):
        """
        Event is a fairly generic object. It is the base object for any market or market impacting event. There is not
        much that is shared by all events, resulting in a bare bones object.

        :param event_id: the unique identifier of the event
        :param timestamp: float. The time of the event in standard python representation of microseconds where left of 
                            the decimal is the number of seconds and to the right of the decimal is the number of us.
        """
        assert isinstance(timestamp, float)
        self._event_id = event_id
        self._timestamp = timestamp

    def event_type_str(self):
        raise NotImplemented("event_type_str to be implemented by inheriting sub class.")

    def timestamp(self):
        """
        Get the timestamp of an event in standard python representation of microseconds where left of the
         decimal is the number of seconds and to the right of the decimal is the number of microseconds.

        :return: float
        """
        return self._timestamp

    def event_id(self):
        """
        Get the unique identifier of the event.

        :return: the identifier
        """
        return self._event_id

    def to_json(self):
        return {self.__class__.__name__: {"event_id": self.event_id(), "timestamp": self.timestamp()}}

    def __str__(self):
        return json.dumps(self.to_json())
