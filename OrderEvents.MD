# Order Events

## Overview
Order Events (found in in `MarketPy.MarketObjects.Events.OrderEvents.py` are events used to send information to and from a matching engine / trading venue / market center / etc. These event objects contain enough information to maintain state, track behavior, and perform analysis of a market and individual users. 

## Extensibility
The fields built into OrderEvent objects follow the 80/20 rule: they should be good enough for 80% of someone's needs. However, there will be data that different markets or users want to track that is not already built as fields in the objects. For example, there are many more FIX fields that there are fields in OrderEvent objects.

There are two ways to extend the data carried in these objects:
1. other_key_values: a dictionary of data you can use to pass values through the system so that they are available in listeners, event processors, etc.
2. Extend the class: this is a more intensive way to do it but makes sense if using MarketPy as a foundation for custom applications where you want to ensure certain values not only get passed through but are used in different areas of the application.
