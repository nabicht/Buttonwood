# Order Events

## Overview
Order Events (found in in `Buttonwood.MarketObjects.Events.OrderEvents.py` are events used to send information to and from a matching engine / trading venue / market center / etc. These event objects contain enough information to maintain state, track behavior, and perform analysis of a market and individual users. 

## Types of OrderEvent Objects
There are two primary types of OrderEvent objects:
1. Commands: messages sent by a user to a market center "commanding" that an action be taken on their behalf.
2. Execution Reports: an report of what resulted from the execution of a command.

### Commands
Commands are a events that a market user sends to market center to request (or "command") that an action be applied to a market on their behalf.

The commands are:
- New Order
- Cancel Replace
- Cancel Request

A __New Order__ is a new expression of risk (exposure) in the market. It is the first event in an OrderEventChain.

A __Cancel Replace__ is modification of risk (exposure) in the market, whether it be price, quantity, or both. A "Modification" (the adjustment down in quantity of an order) is often a synonym or sub-type of a Cancel Replace. In Buttonwood, a Cancel Replace is considered good enough to also represent a Modify command so Modify does not exist.

A __Cancel Request__ is the command that requests the removal of risk from the market. The request can be made by the user who initiated the OrderEventChain with a New Order or by the market center. Note that in some markets centers other "super users", such as head traders, risk managers, firm princples, etcs, can also submit Cancel Requests.

### Execution Reports


## Extensibility
The fields built into OrderEvent objects follow the 80/20 rule: they should be good enough for 80% of someone's needs. However, there will be data that different markets or users want to track that is not already built as fields in the objects. For example, there are many more FIX fields that there are fields in OrderEvent objects.

There are two ways to extend the data carried in these objects:
1. other_key_values: a dictionary of data you can use to pass values through the system so that they are available in listeners, event processors, etc.
2. Extend the class: this is a more intensive way to do it but makes sense if using Buttonwood as a foundation for custom applications where you want to ensure certain values not only get passed through but are used in different areas of the application.
