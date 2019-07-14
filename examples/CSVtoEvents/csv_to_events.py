
import StringIO

EXAMPLE_DATA = StringIO.StringIO("""
Order ID,Index,Event,Time,Product,Destination,Time In Force,User,Side,Price,Qty,Leaves Qty,Response To Id,Aggressive Event ID,Match ID,,,,,,,,,,
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
91CD454,17,Cancel Conf,2019-05-07 12:12:29.117,AAAA,EXC1,,FirmY,,,,,16,,,,,,,,,,,,
87AB674,18,Cancel,2019-05-07 12:04:23.779,AAAA,EXC1,,FirmA,,,,,,,,,,,,,,,,,
87AB674,19,Cancel Conf,2019-05-07 12:04:23.917,AAAA,EXC1,,FirmA,,,,,18,,,,,,,,,,,,
91CD455,20,New,2019-05-07 12:06:18.411,AAAA,EXC1,FAR,FirmX,B,100.10,40,,,,,,,,,,,,,,
745XY321,21,Full Fill,2019-05-07 12:06:18.429,AAAA,EXC1,,FirmC,S,100.10,35,0,,20,MRT202,,,,,,,,,,
91CD455,22,Part Fill,2019-05-07 12:06:18.429,AAAA,EXC1,,FirmX,B,100.10,35,5,,20,MRT202,,,,,,,,,,
91CD455,23,Ack,2019-05-07 12:06:18.431,AAAA,EXC1,FAR,FirmX,B,100.10,5,,20,,,,,FirmX,B,100.10,35,5,,20,MRT202""")

# first we need to parse each line
for line in EXAMPLE_DATA:
    parts = line.split(',')[:-1]
    # Order Id is the unique identifier of the order chain
    chain_id = parts[0]
    # Index is the unique identifier of the event
    event_id = parts[1]
    # event isi
