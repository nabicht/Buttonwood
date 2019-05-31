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

from datetime import datetime
from datetime import timedelta

DATE_TEMPLATE = '%Y%m%d'
TIME_TEMPLATE = '%H:%M:%S.%f'
DATETIME_TEMPLATE = '%Y%m%d-%H:%M:%S.%f'
EPOCH = datetime(1970, 1, 1)


def timestamp_to_epoch(timestamp):
    assert isinstance(timestamp, str)
    return datetime_to_epoch(timestamp_to_datetime(timestamp))


def datetime_to_epoch(the_datetime):
    assert isinstance(the_datetime, datetime)
    return (the_datetime - EPOCH).total_seconds()


def timestamp_to_datetime(timestamp):
    assert isinstance(timestamp, str)
    return datetime.strptime(timestamp, DATETIME_TEMPLATE)


def epoch_to_datetime(secs):
    assert isinstance(secs, float)
    return EPOCH + timedelta(seconds=secs)


def epoch_to_timestamp(secs):
    assert isinstance(secs, float)
    return epoch_to_datetime(secs).strftime(DATETIME_TEMPLATE)


def millis_string(secs):
    return '%.3f' % secs


def mics_string(secs):
    return '%.6f' % secs
