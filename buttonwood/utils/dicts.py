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

from collections import defaultdict


class NDeepDict(defaultdict):

    def __init__(self, depth, default_factory=None):
        assert depth > 0
        if depth > 1:
            super().__init__(lambda: NDeepDict(depth-1, default_factory=default_factory))
        else:
            super().__init__(default_factory)
        self._depth = depth
    
    def get(self, key):
        if isinstance(key, list):
            return self.__getitem__(key)
        else:
            return super().get(key)

    def __getitem__(self, key):
        if isinstance(key, list):
            if len(key) > 1:
                ret = super().__getitem__(key[0]).get(key[1:])
            else:
                ret = super().__getitem__(key[0])
        else:
            ret = super().__getitem__(key)
        return ret
    
    def __setitem__(self, key, value):
        if isinstance(key, list):
            if len(key) > 1:
                self.__getitem__(key[0]).__setitem__(key[1:], value)
            else:
                super().__setitem__(key[0], value)
        else:
            super().__setitem__(key, value)
    
    def __delitem__(self, key):
        if isinstance(key, list):
            if len(key) > 1:
                self.__getitem__(key[0]).__delitem__(key[1:])
            else:
                super().__delitem__(key[0])
        else:
            super().__delitem__(key)

