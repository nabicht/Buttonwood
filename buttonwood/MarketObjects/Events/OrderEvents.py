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

from buttonwood.MarketObjects.CancelReasons import CANCEL_TYPES_STRINGS, CANCEL_REASON_STRINGS
from buttonwood.MarketObjects.Events.BasicEvents import BasicEvent
from buttonwood.MarketObjects.Price import Price
from buttonwood.MarketObjects.Market import Market
from buttonwood.MarketObjects.RejectReasons import REJECT_REASON_STRINGS
from buttonwood.MarketObjects.Side import Side
from buttonwood.MarketObjects.Events import OrderEventConstants


class OrderEvent(BasicEvent):
    """
    An OrderEvent is the base class for matching engine order events, which are the messages a customer/user/participant
     sends into the matching engine and the resulting executions the matching engine sends out.

    OrderEvent has two sub categories that are both classes inheriting from it:
      * Commands
      * Execution Reports

    Commands are the events sent into the matching engine. They are the events that express a desire that the matching
     engine then tries to execute on.

    Execution Reports are the events the matching engine sends back after acting on a Command. Every Execution Report
     should have a causing OrderEvent.

    A series of events can be strung together to make up the life cycle of an order. For example:
     * New Order
     * Acknowledgement
     * Cancel Replace
     * Acknowledgement
     * Partial Fill
     * Cancel
     * Cancel Confirm

    This is referred to as an order chain. Events have an order chain ID that
     is used to clearly identify all events that belong to the same order chain.
    """

    def __init__(self, event_id, timestamp, chain_id, user_id, market, other_key_values=None):
        """
        The initializer of the base OrderEvent class.

        While it seems like one wouldn't need product, it is great to have here
         for filtering, comparisons, etc.

        `other_key_values` is used for keeping key/value pairs around that don't
         fit the defined arguments. This is an quick and easy way to track meta
         data that a particular matching venue uses/keeps without having to
         create custom versions of the OrderEvent just to keep this data.

        :param event_id: unique identifier of the event
        :param timestamp: float. microsecond time stamp of event. Expecting format of seconds.microseconds (ex: 1234.001123)
        :param chain_id: str or int. the unique identifier fo the orderchain
        :param user_id: str or int. unique identifier of the user who sent the command
        :param market: MarketObjects.Market
        :param other_key_values: dict
        """
        assert isinstance(chain_id, str) or isinstance(chain_id, int)
        assert isinstance(user_id, str) or isinstance(user_id, int)
        assert isinstance(market, Market)
        assert other_key_values is None or isinstance(other_key_values,
                                                      dict), "other_key_values must be none or of type dict"
        BasicEvent.__init__(self, event_id, timestamp)
        self._user_id = user_id
        self._chain_id = chain_id
        self._market = market
        self._other_key_values = {} if other_key_values is None else other_key_values

    def market(self):
        """
        The market of the order event
        :return:
        """
        return self._market

    def user_id(self):
        """
        The user id of the order event

        :return: int or str
        """
        return self._user_id

    def chain_id(self):
        """
        The order chain id of the order event

        :return: int or str
        """
        return self._chain_id

    def get_other_value(self, key):
        """
        Returns the value for the given key from `other_key_values`.

        If the key does not exist in `other_key_values` then returns `None`

        :param key: object
        :return: object. Can be `None`.
        """
        return self._other_key_values.get(key)

    def other_data(self):
        """
        Gets the dictionary of optional other key/value pairs that are stored with the event.
        
        :return: dict. Can be None
        """
        return self._other_key_values

    def _other_values_json(self):
        d = {}
        if self._other_key_values is not None:
            for key, value in self._other_key_values.iteritems():
                if isinstance(value, Market):
                    d[str(key)] = value.to_json()
                elif isinstance(value, Price):
                    d[str(key)] = str(value.price())
                elif hasattr(value, '__dict__'):  # cheap hack to figure out if a primative or not
                    d[str(key)] = str(value)
                else:
                    d[str(key)] = value
        return d


class OrderCommand(OrderEvent):
    """
    The base class for an order's commands that go into a matching engine. These
     are the events that express a desire
     from a participant that the matching engine attempts to execute.
    """

    def __init__(self, event_id, timestamp, chain_id, user_id, market, other_key_values=None):
        OrderEvent.__init__(self, event_id, timestamp, chain_id, user_id, market, other_key_values=other_key_values)


class NewOrderCommand(OrderCommand):
    """
    A new order. A new order is necessarily the first event in an order chain.

    If iceberg_peak_qty is None then not taking advantage of iceberg functionality.
    """

    def __init__(self, event_id, timestamp, chain_id, user_id, market, side, time_in_force,
                 price, qty, iceberg_peak_qty=None, limit_or_market=OrderEventConstants.LIMIT, other_key_values=None):
        # TODO documentation
        assert isinstance(side, Side)
        assert isinstance(price, Price)
        assert isinstance(qty, int)
        assert isinstance(limit_or_market, int)
        assert limit_or_market in [OrderEventConstants.MARKET, OrderEventConstants.LIMIT]
        assert iceberg_peak_qty is None or isinstance(iceberg_peak_qty, int)
        assert isinstance(time_in_force, int)
        assert qty > 0, "Qty must be greater than 0"
        assert iceberg_peak_qty is None or iceberg_peak_qty >= 0, "Iceberg Peak Qty must be None or an int >= 0"
        OrderCommand.__init__(self, event_id, timestamp, chain_id, user_id, market, other_key_values=other_key_values)
        assert market.product().is_valid_price(price), "Price %s is not valid for Product %s" % (str(price), str(market))

        self._side = side
        self._price = price
        self._qty = qty
        self._limit_or_market = limit_or_market
        self._iceberg_peak_qty = iceberg_peak_qty
        if self._iceberg_peak_qty is None:
            self._iceberg_peak_qty = qty
        self._time_in_force = time_in_force

    def side(self):
        """
        Get the side.

        :return: MarketObjects.Side
        """
        return self._side

    def price(self):
        """
        Get the price.

        :return: MarketObjects.Price
        """
        return self._price

    def qty(self):
        """
        Get the qty of the new order.

        :return: int
        """
        return self._qty

    def iceberg_peak_qty(self):
        """
        Get the iceberg_peak_qty of the new order

        :return: int
        """
        return self._iceberg_peak_qty

    def time_in_force(self):
        """
        Gets the integer that identifies the order type.

        :return: int
        """
        return self._time_in_force

    def is_far(self):
        """
        Helper function to say if it is a FAR order or not.
        
        :return: bool 
        """
        return self._time_in_force == OrderEventConstants.FAR

    def is_fak(self):
        """
        Helper function to say if it is a FAK order or not.

        :return: bool 
        """
        return self._time_in_force == OrderEventConstants.FAK

    def is_fok(self):
        """
        Helper function to say if it is a FOK order or not.

        :return: bool 
        """
        return self._time_in_force == OrderEventConstants.FOK

    def is_limit_order(self):
        """
        Returns True if the new order is a limit order; false if it is not.

        :return: bool
        """
        return self._limit_or_market == OrderEventConstants.LIMIT

    def is_market_order(self):
        """
        Returns True if the new order is a market order; false if it is not.

        :return: bool
        """
        return self._limit_or_market == OrderEventConstants.MARKET

    def event_type_str(self):
        return "New Order Command"

    def to_json(self):
        return {self.__class__.__name__: {'user_id': self.user_id(),
                                          'chain_id': self.chain_id(),
                                          'event_id': self.event_id(),
                                          'timestamp': self.timestamp(),
                                          'product_name': self.market().product().name(),
                                          'endpoint_name': self.market().endpoint().name(),
                                          'side': int(self.side()),
                                          'price': str(self.price()),
                                          'qty': self.qty(),
                                          'iceberg_peak_qty': self.iceberg_peak_qty(),
                                          'time_in_force': OrderEventConstants.TIME_IN_FORCE_STRINGS[
                                              self.time_in_force()],
                                          'other_key_values': self._other_values_json()}}


class CancelReplaceCommand(OrderCommand):
    def __init__(self, event_id, timestamp, chain_id, user_id, market, side, price, qty, iceberg_peak_qty=None,
                 other_key_values=None):
        # TODO document
        assert isinstance(price, Price)
        assert isinstance(qty, int)
        assert iceberg_peak_qty is None or isinstance(iceberg_peak_qty, int)
        assert iceberg_peak_qty is None or iceberg_peak_qty >= 0, "iceberg_peak_qty cannot be negative."
        assert qty >= 0, "Qty must be greater than 0"
        assert market.product().is_valid_price(price), "Price %s is not valid for Market %s" % (str(price), str(market))
        OrderCommand.__init__(self, event_id, timestamp, chain_id, user_id, market, other_key_values=other_key_values)
        self._side = side
        self._price = price
        self._iceberg_peak_qty = iceberg_peak_qty
        if self._iceberg_peak_qty is None:
            self._iceberg_peak_qty = qty
        self._qty = qty

    def price(self):
        """
        Get the price of the cancel replace.

        :return: MarketObjects.Price
        """
        return self._price

    def side(self):
        """
        Get the side.

        :return: MarketObjects.Side
        """
        return self._side

    def qty(self):
        """
        Get the qty of the cancel replace request.

        :return: int
        """
        return self._qty

    def iceberg_peak_qty(self):
        """
        Get the iceberg_peak_qty of the cancel replace request

        :return: int
        """
        return self._iceberg_peak_qty

    def event_type_str(self):
        return "Cancel Replace Command"

    def to_json(self):
        """
        Get the json dictionary of the cancel replace message

        :return: dict
        """
        return {self.__class__.__name__: {'user_id': self.user_id(),
                                          'chain_id': self.chain_id(),
                                          'event_id': self.event_id(),
                                          'timestamp': self.timestamp(),
                                          'product_name': self.market().product().name(),
                                          'endpoint_name': self.market().endpoint().name(),
                                          'price': str(self.price()),
                                          'qty': self.qty(),
                                          'iceberg_peak_qty': self.iceberg_peak_qty(),
                                          'other_key_values': self._other_values_json()}}


class CancelCommand(OrderCommand):
    def __init__(self, event_id, timestamp, chain_id, user_id, market, cancel_type, other_key_values=None):
        # TODO document
        assert isinstance(cancel_type, int)
        OrderCommand.__init__(self, event_id, timestamp, chain_id, user_id, market, other_key_values=other_key_values)
        self._cancel_type = cancel_type

    def cancel_type(self):
        """
        Get the cancel type identifier from the Cancel.

        :return: int
        """
        return self._cancel_type

    def cancel_type_str(self):
        """
        Get the cancel type human readable string from the Cancel.

        :return: str
        """
        if self.cancel_type() in CANCEL_TYPES_STRINGS:
            return CANCEL_TYPES_STRINGS[self.cancel_type()]
        return "%d is an unknown cancel reason." % (self.cancel_type())

    def event_type_str(self):
        return "Cancel Command"

    def to_json(self):
        """
        Get the json dictionary of the cancel message

        :return: dict
        """
        return {self.__class__.__name__: {'user_id': self.user_id(),
                                          'chain_id': self.chain_id(),
                                          'event_id': self.event_id(),
                                          'timestamp': self.timestamp(),
                                          'product_name': self.market().product().name(),
                                          'endpoint_name': self.market().endpoint().name(),
                                          'cancel_type': self.cancel_type(),
                                          'cancel_type_str': self.cancel_type_str(),
                                          'other_key_values': self._other_values_json()}}


class ExecutionReport(OrderEvent):
    """
    The base class for the execution reports that come out of the matching engine. These are the events that respond
     to the order commands.
    """

    def __init__(self, event_id, timestamp, chain_id, user_id, market, causing_command, other_key_values=None):
        OrderEvent.__init__(self, event_id, timestamp, chain_id, user_id, market, other_key_values=other_key_values)
        self._causing_command = causing_command

    def causing_command(self):
        """
        Get the command that caused the execution report.

        :return: MarketObjects.Events.OrderEvents.OrderCommand
        """
        return self._causing_command


class AcknowledgementReport(ExecutionReport):
    def __init__(self, event_id, timestamp, chain_id, user_id, market, response_to_command, price,
                 qty, iceberg_peak_qty, other_key_values=None):
        """
        An acknowledgement execution report. Has all the standard data for identifying the message, order, etc.

        Also includes the command it is acknowledging (this is for ease of use for listeners to the data as well as to
         systems and usecases that may not be using order chain tracking.

        Price, qty, and iceberg_peak_qty are contained here since what gets ack'd will not always match what was
         requested based on the situation (ex: aggressive orders getting partially filled pre-ack) or the matching
         engine's rules, or the order type (ex: pegged orders starting off at different prices).

        :param event_id: int
        :param timestamp: float
        :param chain_id: int or str
        :param user_id: int or str
        :param market: MarketObjects.Market.Market
        :param response_to_command: MarketObjects.Events.OrderEvents.OrderCommand
        :param price: MarketObjects.Price.Price
        :param qty: int
        :param iceberg_peak_qty: int
        :param other_key_values: dict
        """
        # TODO finish param documentation above
        # TODO finish asserts below
        assert isinstance(price, Price)
        assert isinstance(qty, int)
        assert iceberg_peak_qty is None or isinstance(iceberg_peak_qty, int)
        ExecutionReport.__init__(self, event_id, timestamp, chain_id, user_id, market, response_to_command,
                                 other_key_values=other_key_values)
        self._price = price
        self._qty = qty
        self._iceberg_peak_qty = iceberg_peak_qty
        if self._iceberg_peak_qty is None:
            self._iceberg_peak_qty = qty

    def acknowledged_command(self):
        """
        Get the event that is being acknowledged. Helper function that returns the same as causing_command()

        :return: MarketObjects.Events.OrderEvents.OrderCommand
        """
        return self._causing_command

    def price(self):
        """
        Get the price.

        :return: MarketObjects.Price
        """
        return self._price

    def qty(self):
        """
        Get the qty

        :return: int
        """
        return self._qty

    def iceberg_peak_qty(self):
        """
        Get the iceberg peak qty

        :return: int
        """
        return self._iceberg_peak_qty

    def event_type_str(self):
        return "Acknowledgement Report"

    def to_json(self):
        """
        Get the json dictionary of the acknowledgement

        :return: dict
        """
        return {self.__class__.__name__: {'user_id': self.user_id(),
                                          'chain_id': self.chain_id(),
                                          'event_id': self.event_id(),
                                          'timestamp': self.timestamp(),
                                          'product_name': self.market().product().name(),
                                          'endpoint_name': self.market().endpoint().name(),
                                          'response_to_command': self.causing_command().to_json(),
                                          'price': str(self.price()),
                                          'qty': self.qty(),
                                          'iceberg_peak_qty': self.iceberg_peak_qty(),
                                          'other_key_values': self._other_values_json()}}


class RejectReport(ExecutionReport):

    def __init__(self, event_id, timestamp, chain_id, user_id, market, response_to_command, reject_reason,
                 other_key_values=None):
        # TODO document
        assert isinstance(reject_reason, int)
        ExecutionReport.__init__(self, event_id, timestamp, chain_id, user_id, market, response_to_command,
                                 other_key_values=other_key_values)
        self._reject_reason = reject_reason

    def rejected_command(self):
        """
        Get the event that is being rejected. Helper function that returns the same as causing_command()

        :return: MarketObjects.Events.OrderEvents.OrderCommand
        """
        return self._causing_command

    def reject_reason(self):
        """
        Get the reject reason's identifier, which is an int

        :return: int
        """
        return self._reject_reason

    def reject_reason_str(self):
        """
        Get the human readable reject reason string.

        :return: str
        """
        if self.reject_reason() in REJECT_REASON_STRINGS:
            return CANCEL_TYPES_STRINGS[self.reject_reason()]
        return "%d is an unknown cancel reason." % (self.reject_reason())

    def event_type_str(self):
        return "Reject Report"

    def to_json(self):
        """
        Get the json dictionary of the reject report

        :return: dict
        """
        return {self.__class__.__name__: {'user_id': self.user_id(),
                                          'chain_id': self.chain_id(),
                                          'event_id': self.event_id(),
                                          'timestamp': self.timestamp(),
                                          'product_name': self.market().product().name(),
                                          'endpoint_name': self.market().endpoint().name(),
                                          'reject_reason': self.reject_reason(),
                                          'reject_reason_str': self.reject_reason_str(),
                                          'response_to_command': self.causing_command().to_json(),
                                          'other_key_values': self._other_values_json()}}


class CancelReport(ExecutionReport):

    def __init__(self, event_id, timestamp, chain_id, user_id, market, cancel_command, cancel_reason,
                 other_key_values=None):
        # TODO document
        assert isinstance(cancel_reason, int)
        ExecutionReport.__init__(self, event_id, timestamp, chain_id, user_id, market, cancel_command,
                                 other_key_values=other_key_values)
        self._cancel_reason = cancel_reason

    def cancel_command(self):
        """
        Get the cancel command that the report is confirming. This is a helper function that is just here for logical
         naming. It simply returns the causing command.
        :return:
        """
        return self.causing_command()

    def cancel_reason(self):
        """
        Get the cancel reason's identifier, which is an int

        :return: int
        """
        return self._cancel_reason

    def cancel_reason_str(self):
        """
        Get the human readable cancel reason string.

        :return: str
        """
        if self.cancel_reason() in CANCEL_REASON_STRINGS:
            return CANCEL_REASON_STRINGS[self.cancel_reason()]
        return "%d is an unknown cancel reason." % (self.cancel_reason())

    def event_type_str(self):
        return "Cancel Report"

    def to_json(self):
        """
        Get the json dictionary of the cancel message

        :return: dict
        """
        return {self.__class__.__name__: {'user_id': self.user_id(),
                                          'chain_id': self.chain_id(),
                                          'event_id': self.event_id(),
                                          'timestamp': self.timestamp(),
                                          'product_name': self.market().product().name(),
                                          'endpoint_name': self.market().endpoint().name(),
                                          'cancel_reason': self.cancel_reason(),
                                          'cancel_reason_str': self.cancel_reason_str(),
                                          'cancel_command': "None" if self.causing_command() is None else self.cancel_command().to_json(),
                                          'other_key_values': self._other_values_json()}}


class FillReport(ExecutionReport):

    def __init__(self, event_id, timestamp, chain_id, user_id, market, aggressing_command, fill_qty, fill_price,
                 side, match_id, other_key_values=None):
        # TODO document
        assert isinstance(fill_price, Price)
        assert isinstance(fill_qty, int)
        assert isinstance(match_id, int) or isinstance(match_id, str)
        assert isinstance(side, Side)
        ExecutionReport.__init__(self, event_id, timestamp, chain_id, user_id, market, aggressing_command,
                                 other_key_values=other_key_values)
        self._fill_price = fill_price
        self._fill_qty = fill_qty
        self._side = side
        self._match_ids = match_id

    def aggressing_command(self):
        """
        Get the aggressing command that the fill was triggered by. This is a helper function that is just here
         for logical naming. It simply returns the causing command.
        :return:
        """
        return self.causing_command()

    def is_aggressor(self):
        """
        Returns True if this fill is for the aggressor that caused the match; returns False otherwise.

        :return: bool
        """
        return self.aggressing_command().chain_id() == self.chain_id()

    def match_id(self):
        """
        Get the match id that the fill is part of.

        :return: int or str.
        """
        return self._match_ids

    def fill_price(self):
        """
        Get the price of the fill.

        :return: MarketObjects.Price
        """
        return self._fill_price

    def fill_qty(self):
        """
        Get the qty filled.

        :return: int
        """
        return self._fill_qty

    def side(self):
        """
        Get the side of the fill.

        :return: MarketObjects.Side
        """
        return self._side

    def event_type_str(self):
        return "Fill Report"

    def to_json(self):
        """
        Get the json dictionary of the fill message.

        :return: dict
        """
        return {self.__class__.__name__: {'user_id': self.user_id(),
                                          'chain_id': self.chain_id(),
                                          'event_id': self.event_id(),
                                          'timestamp': self.timestamp(),
                                          'product_name': self.market().product().name(),
                                          'endpoint_name': self.market().endpoint().name(),
                                          'side': int(self.side()),
                                          'fill_price': str(self.fill_price()),
                                          'fill_qty': self.fill_qty(),
                                          'match_id': self.match_id(),
                                          'aggressing_command': self.aggressing_command().to_json(),
                                          'other_key_values': self._other_values_json()}}


class PartialFillReport(FillReport):

    def __init__(self, event_id, timestamp, chain_id, user_id, market, aggressing_command, fill_qty, fill_price,
                 side, match_id, leaves_qty, other_key_values=None):
        # TODO document
        assert isinstance(leaves_qty, int)
        FillReport.__init__(self, event_id, timestamp, chain_id, user_id, market, aggressing_command, fill_qty,
                            fill_price, side, match_id, other_key_values=other_key_values)
        self._leaves_qty = leaves_qty

    def leaves_qty(self):
        """
        Gets the leaves qty that results from the fill.
        :return:
        """
        return self._leaves_qty

    def event_type_str(self):
        return "Partial Fill Report"

    def to_json(self):
        """
        Get the json dictionary of the partial fill message.

        :return: dict
        """
        return {self.__class__.__name__: {'user_id': self.user_id(),
                                          'chain_id': self.chain_id(),
                                          'event_id': self.event_id(),
                                          'timestamp': self.timestamp(),
                                          'product_name': self.market().product().name(),
                                          'endpoint_name': self.market().endpoint().name(),
                                          'side': int(self.side()),
                                          'fill_price': str(self.fill_price()),
                                          'fill_qty': self.fill_qty(),
                                          'match_id': self.match_id(),
                                          'leaves_qty': self.leaves_qty(),
                                          'aggressing_command': self.aggressing_command().to_json(),
                                          'other_key_values': self._other_values_json()}}


class FullFillReport(FillReport):

    def __init__(self, event_id, timestamp, chain_id, user_id, market, aggressing_command, fill_qty, fill_price,
                 side, match_id, other_key_values=None):
        # TODO document
        FillReport.__init__(self, event_id, timestamp, chain_id, user_id, market, aggressing_command, fill_qty,
                            fill_price, side, match_id, other_key_values=other_key_values)

    def event_type_str(self):
        return "Full Fill Report"
