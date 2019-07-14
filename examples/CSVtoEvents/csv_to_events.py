
import StringIO
from cdecimal import Decimal
from datetime import datetime
from buttonwood.MarketObjects.Market import Market
from buttonwood.MarketObjects.Product import Product
from buttonwood.MarketObjects.Endpoint import Endpoint
from buttonwood.MarketObjects import CancelReasons
from buttonwood.MarketObjects.Events.OrderEvents import NewOrderCommand
from buttonwood.MarketObjects.Events.OrderEvents import CancelReplaceCommand
from buttonwood.MarketObjects.Events.OrderEvents import CancelCommand
from buttonwood.MarketObjects.Events.OrderEvents import AcknowledgementReport
from buttonwood.MarketObjects.Events.OrderEvents import CancelReport
from buttonwood.MarketObjects.Events.OrderEvents import PartialFillReport
from buttonwood.MarketObjects.Events.OrderEvents import FullFillReport
from buttonwood.MarketObjects.Events import OrderEventConstants
from buttonwood.MarketObjects import Side
from buttonwood.utils.timehelpers import datetime_to_epoch


EXAMPLE_DATA = StringIO.StringIO("""Order ID,Index,Event,Time,Product Name,Destination,Time In Force,User,Side,Price,Qty,Leaves Qty,Response To Id,Aggressive Event ID,Match ID,Cancel Reason,,,,,,,,,
87AB672,1,New,2019-05-07 12:00:00.001,AAAA,EXC1,FAR,FirmA,B,100.10,50,,,,,,,,,,,,,,
87AB672,2,Ack,2019-05-07 12:00:00.002,AAAA,EXC1,FAR,FirmA,B,100.10,50,,1,,,,,,,,,,,,
87AB673,3,New,2019-05-07 12:00:00.002,AAAA,EXC1,FAR,FirmA,B,100.09,50,,,,,,,,,,,,,,
87AB673,4,Ack,2019-05-07 12:00:00.005,AAAA,EXC1,FAR,FirmA,B,100.09,50,,3,,,,,,,,,,,,
87AB672,5,Mod,2019-05-07 12:00:00.245,AAAA,EXC1,FAR,FirmA,B,100.08,50,,,,,,,,,,,,,,
87AB672,6,Ack,2019-05-07 12:00:00.252,AAAA,EXC1,FAR,FirmA,B,100.08,50,,5,,,,,,,,,,,,
87AB674,7,New,2019-05-07 12:00:01.782,AAAA,EXC1,FAR,FirmA,S,100.10,50,,,,,,,,,,,,,,
87AB674,8,Ack,2019-05-07 12:00:02.007,AAAA,EXC1,FAR,FirmA,S,100.10,50,,7,,,,,,,,,,,,
87AB675,9,New,2019-05-07 12:00:03.654,AAAA,EXC1,FAR,FirmA,S,100.10,50,,,,,,,,,,,,,,
87AB675,10,New,2019-05-07 12:00:03.701,AAAA,EXC1,FAR,FirmA,S,100.11,50,,9,,,,,,,,,,,,
91CD453,11,New,2019-05-07 12:02:17.483,AAAA,EXC1,FAK,FirmX,B,100.10,20,,,,,,,,,,,,,,
87AB674,12,Part Fill,2019-05-07 12:02:17.483,AAAA,EXC1,,FirmA,S,100.10,20,30,,11,MRT201,,,,,,,,,,
91CD453,13,Full Fill,2019-05-07 12:02:17.483,AAAA,EXC1,,FirmX,B,100.10,20,0,,11,MRT201,,,,,,,,,,
745XY321,14,New,2019-05-07 12:12:19.073,AAAA,EXC1,FAR,FirmC,S,100.10,35,,,,,,,,,,,,,,
745XY321,15,Ack,2019-05-07 12:12:19.219,AAAA,EXC1,FAR,FirmC,S,100.10,35,,14,,,,,,,,,,,,
91CD454,16,New,2019-05-07 12:12:29.111,AAAA,EXC1,FOK,FirmY,B,100.10,225,,,,,,,,,,,,,,
91CD454,17,Cancel Conf,2019-05-07 12:12:29.117,AAAA,EXC1,,FirmY,,,,,16,,,FOK Miss,,,,,,,,,
87AB674,18,Cancel,2019-05-07 12:04:23.779,AAAA,EXC1,,FirmA,,,,,,,,,,,,,,,,,
87AB674,19,Cancel Conf,2019-05-07 12:04:23.917,AAAA,EXC1,,FirmA,,,,,18,,,Requested,,,,,,,,,
91CD455,20,New,2019-05-07 12:06:18.411,AAAA,EXC1,FAR,FirmX,B,100.10,40,,,,,,,,,,,,,,
745XY321,21,Full Fill,2019-05-07 12:06:18.429,AAAA,EXC1,,FirmC,S,100.10,35,0,,20,MRT202,,,,,,,,,,
91CD455,22,Part Fill,2019-05-07 12:06:18.429,AAAA,EXC1,,FirmX,B,100.10,35,5,,20,MRT202,,,,,,,,,,
91CD455,23,Ack,2019-05-07 12:06:18.431,AAAA,EXC1,FAR,FirmX,B,100.10,5,,20,,,,,FirmX,B,100.10,35,5,,20,MRT202""")

# set up a Market for the events. For that you need at least:
#  1) the Product
#  2) the Endpoint
#  3) the Minimum Price Increment
prod = Product("AAAA", "Test Product")
ep = Endpoint("Exchange 1", "EXC1")
mpi = Decimal("0.01")
market = Market(prod, ep, mpi)

# now create a mapping of what we'll parse out of the file to the Market.
# This comes in even more handy when there are multiple markets
mrkt_dict = {("AAAA", "EXC1"): market}

# set up the time stamp parser
time_stamp_frmt = "%Y-%m-%d %H:%M:%S.%f"

# we are going to keep a dictionary of event_id to Command so that we can properly create Execution Reports
id_to_cmd = {}

# first we need to parse each line
for line in EXAMPLE_DATA:
    parts = line[:-1].split(',')
    # skip header
    if parts[0] == "Order ID":
        continue

    # Order Id is the unique identifier of the order chain
    chain_id = parts[0]
    # Index is the unique identifier of the event
    event_id = int(parts[1])
    # Need an identifier of the user that placed the order
    user = parts[7]

    # get the event time
    event_time = datetime.strptime(parts[3], time_stamp_frmt)
    # Event objects what the time stamp as a float (seconds.microseconds) so convert to time since epoch
    time_stamp = datetime_to_epoch(event_time)

    # now get the market
    prod_name = parts[4]
    ep_name = parts[5]
    mrkt = mrkt_dict[(prod_name, ep_name)]

    # get the side: not all events contain side so default is None.
    # Buttonwood provides a helper that converts the most common string representations of Buy / Sell to Side objects
    side = Side.get_side(parts[8])

    # get the time in force. Not all events need time in force so the default is None.
    # Note: could have used OrderEventContants.TIME_IN_FORCE_STR_TO_INT here but wanted to show a more extensive use of
    #   of the constants
    if parts[6] == "FAR":
        tif = OrderEventConstants.FAR
    elif parts[6] == "FAK":
        tif = OrderEventConstants.FAK
    elif parts[6] == "FOK":
        tif = OrderEventConstants.FOK
    elif parts[6] == "":
        tif = None
    else:
        raise Exception("Could not convert %s to a known TimeInForce" % parts[6])

    # get event type so we can create the right events
    event_type = parts[2]

    if event_type == "New":  # for event type "New" create a new event
        # get price, using Market's get_price function that will gets a Price object for a string, Decimal, or int
        price = mrkt.get_price(parts[9])
        qty = int(parts[10])
        event = NewOrderCommand(event_id, time_stamp, chain_id, user, market, side, tif, price, qty)
        # add the event to the event id to command dictionary
        id_to_cmd[event_id] = event
    elif event_type == "Mod":  # for event type "Mod" create a cancel replace event
        # get price, using Market's get_price function that will gets a Price object for a string, Decimal, or int
        price = mrkt.get_price(parts[9])
        qty = int(parts[10])
        event = CancelReplaceCommand(event_id, time_stamp, chain_id, user, market, side, price, qty)
        # add the event to the event id to command dictionary
        id_to_cmd[event_id] = event
    elif event_type == "Cancel":  # for event type "Cancel" create a Cancel command event
        # there can be different types of cancels, but in this case we are assuming it is a user requested cancel
        cancel_type = CancelReasons.USER_CANCEL
        event = CancelCommand(event_id, time_stamp, chain_id, user, market, cancel_type)
        # add the event to the event id to command dictionary
        id_to_cmd[event_id] = event
    elif event_type == "Ack":  # for event type "Ack" create an Acknowledgement
        # this example file has no concept of iceberg orders so iceberg_peak is None (which will cause buttonwood to
        #  to treat the entire order qty as an iceberg
        iceberg_peak = None
        # get price, using Market's get_price function that will gets a Price object for a string, Decimal, or int
        price = mrkt.get_price(parts[9])
        qty = int(parts[10])
        # response to command is the command it is acknowledging, get that ID and look it up from our id_to_cmd dict
        response_to_id = int(parts[12])
        response_to_cmd = id_to_cmd[response_to_id]
        event = AcknowledgementReport(event_id, time_stamp, chain_id, user, market, response_to_cmd, price,
                                      qty, iceberg_peak)
    elif event_type == "Cancel Conf":  # for event type "Cancel Conf" create a Cancel report event
        # get the cancel reason
        if parts[15] == "FOK Miss":
            reason = CancelReasons.FOK_CANCEL
        elif parts[15] == "Requested":
            reason = CancelReasons.USER_REQUESTED
        else:
            raise Exception("Could not convert %s to a cancel reason." % parts[15])
        # cancel command is the command that caused the cancel, get that ID and look it up from our id_to_cmd dict
        response_to_id = int(parts[12])
        response_to_cmd = id_to_cmd[response_to_id]
        event = CancelReport(event_id, time_stamp, chain_id, user, market, response_to_cmd, reason)
    elif event_type == "Part Fill":  # if event type "Part Fill" create a Partial Fill event
        # the aggressing command comes from getting the id and looking it up in the id to cmd dict
        aggressing_id = int(parts[13])
        aggressing_cmd = id_to_cmd[aggressing_id]
        # get fill price, using Market's get_price function that will gets a Price object for a string, Decimal, or int
        fill_price = mrkt.get_price(parts[9])
        fill_qty = int(parts[10])
        # get leaves qty from the file
        leaves_qty = int(parts[11])
        # get the match_id from the file
        match_id = parts[14]
        event = PartialFillReport(event_id, time_stamp, chain_id, user, market, aggressing_cmd, fill_qty, fill_price,
                                  side, match_id, leaves_qty)
    elif event_type == "Full Fill":  # if event type "Full Fill" create a Partial Fill event
        # the aggressing command comes from getting the id and looking it up in the id to cmd dict
        aggressing_id = int(parts[13])
        aggressing_cmd = id_to_cmd[aggressing_id]
        # get fill price, using Market's get_price function that will gets a Price object for a string, Decimal, or int
        fill_price = mrkt.get_price(parts[9])
        fill_qty = int(parts[10])
        # full fills don't need/have a leaves qty because nothing is left.
        # get the match_id from the file
        match_id = parts[14]
        event = FullFillReport(event_id, time_stamp, chain_id, user, market, aggressing_cmd, fill_qty, fill_price,
                               side, match_id)
    else:
        raise Exception("Could not convert %s to an Event" % event_type)

