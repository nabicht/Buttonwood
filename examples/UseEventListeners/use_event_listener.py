
import logging
from buttonwood.MarketObjects.Events.EventHandler import OrderEventHandler
from buttonwood.MarketMetrics.EventListeners.VolumeTrackingListener import VolumeTrackingListener
from buttonwood.MarketMetrics.EventListeners.OrderEventCountListener import OrderEventCountListener
from examples.CSVtoEvents.csv_to_events import get_events


# most buttonwood infrastructure requires a logger. The below logger is a simple console logger.
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.INFO)

# create the Order Event Handler
handler = OrderEventHandler(logger)

# create a couple of listeners and add register them with the order event handler
# registering an event listener takes an event listener id and the event listener object.
#  The event listener id is an arbitraty string you can make up. However, it should be unique across listeners for the
#  instance of the event handler.
vtl = VolumeTrackingListener(logger)
handler.register_event_listener("volume tracker", vtl)

ec = OrderEventCountListener(logger)
handler.register_event_listener("event counter", ec)

# keep track of all markets and user combinations we see for volume reporting
market_user = set()

# now that there are registered listeners, we need to give the handler some events, one at a time
# we're getting our events from another example: CSVtoEvents
for event in get_events():
    # process(event) returns a tuple of the (order_event_chain, updated_markets)
    #   order_event_chain is the OrderEventChain of the processed event in its state after the event was processed
    #   updated_markets is an iterable of all the markets whose order books were updated, if any were
    # this example does not use this data.
    handler.process(event)

    # after calling process(event) the event handlers should have been called. To show this, for each event processed
    #  we'll get and output some data. Since VolumeTrackingListener only updates when there are fills, we won't look at
    #  that one after each event. But we will look at EventCountListener.

    # for getting event counts, we need a user id and a market, we'll use the user id and market for each event.
    print "Event Counts for %s / %s" % (event.user_id(), str(event.market()))
    print "New Order Count: %d" % ec.get_count(event.market(), event.user_id(), OrderEventCountListener.NEW_ORDER)
    print "Cancel Replaces Count: %d" % ec.get_count(event.market(), event.user_id(),
                                                     OrderEventCountListener.CANCEL_REPLACE)
    print "Acknowledgement Count: %d" % ec.get_count(event.market(), event.user_id(), OrderEventCountListener.ACK)
    print "Cancel Request Count: %d" % ec.get_count(event.market(), event.user_id(),
                                                    OrderEventCountListener.CANCEL_REQUEST)
    print "Cancel Confirm Count: %d" % ec.get_count(event.market(), event.user_id(),
                                                    OrderEventCountListener.CANCEL_CONFIRM)
    print "Partial Fill Count: %d" % ec.get_count(event.market(), event.user_id(), OrderEventCountListener.PARTIAL_FILL)
    print "Full Fill Count: %d" % ec.get_count(event.market(), event.user_id(), OrderEventCountListener.FULL_FILL)
    print "\n"
    market_user.add((event.market(), event.user_id()))

# now that all events are processed let's access some volume tracking
for market, user in market_user:
    vol_tracker = vtl.volume_tracker(market, user)
    print "%s / %s" % (str(market), user)
    print "\tPassive Vol: %d" % (vol_tracker.total_passive_volume() if vol_tracker is not None else 0)
    print "\tAggressive Vol: %d" % (vol_tracker.total_aggressive_volume() if vol_tracker is not None else 0)
