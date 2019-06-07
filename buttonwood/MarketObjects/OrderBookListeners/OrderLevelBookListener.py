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

class OrderLevelBookListener(object):

    def __init__(self, logger):
        self._logger = logger

    def notify_book_update(self, order_book, causing_order_chain, tob_updated):
        """
        This is a stub to be filled in by each implementing inheriting class.

        The causing_order_chain should have already had the the order event that
        caused the book to update applied to it.

        :param order_book: MarketStructures.OrderBooks.OrderLevelOrderBook.OrderLevelOrderBook
        :param causing_order_chain: MarketStructures.Events.EventChains.OrderEventChain
        :param tob_updated: boolean. Whether or not the top of book updated. This is for speed/convenience for the listener.
        """
        raise NotImplemented("notify_book_update to be implemented by inheriting class.")

    def clean_up_order_chain(self, order_chain):
        """
        Function let's the order book listener clean up data it might be storing for the order chain.
        
        Should only be called if the data being kept by the listener for the order chain (or events in the order chain
         is no longer needed)
         
        :param order_chain: Buttonwood.MarketObjects.Events.EventChains.OrderEventChain
        :return: 
        """
        raise NotImplemented("clean_up_order_chain to be implemented by inheriting class.")
