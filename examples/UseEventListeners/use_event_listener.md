# Use EventListener

EventListeners are a basic way of creating metrics based off of the events (and their event chains. Buttonwood comes with a few pre-built EventListeners and you can very easily create your own as well.

This example shows how to push order events through an EventHandler and to EventListeners. 

The EventHandler takes each event it is given, in order, and:
1. builds order event chains
2. hands them off to event listeners that are registered
3. hands them off to books that are registered

This example:
1. Creates an EventHandler
2. Registers EventListeners
3. Pushes events through the EventHandler
4. Gets some data from the registered EventListeners to show that the listener saw and dealt with the events

It uses two of the already built EventListeners:
1. buttonwood.MarketMetrics.EventListeners.OrderEventCountListener
2. buttonwood.MarketMetrics.EventListeners.VolumeTrackingListener
