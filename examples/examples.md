# Introduction

The `examples` folder contains a series of examples to help you get started with Buttonwood. Buttonwood is a collection of the components you need to rapidly build, test, and analyze markets/market structures/etc. It is meant to be flexible. It is object oriented so you can extend it as you wish. Thus, these examples are not intended to be comprehensive. Rather, they are intended to be a helpful guide to working with Buttonwood and understanding how its components go together.

The examples below are listed in order that it is best to go through them. They are designed so your knowledge of / experience with Buttonwood grows from example to example. In some cases examples are even dependent on the code from previous examples.

# Examples

## CSV to Events
Folder: `CSVtoEvents`

To analyze markets you need to start with the market's most important data objects: Order Events. Your source might be a database or flat files or a web service. And most likely they won't be in the same format as what are used here. But this example should help you see how take raw data and create order events.

## How to Use Event Listeners
Folder: 'UseEventListeners'

Once you are creating Event objects, you will probably want to do some evaluation of those events. This can help with looking at market dynamics, user metrics, general order statistics, anomaly detection, risk calculations, compliance monitoring, strategy back testing, etc. etc.

Event Listeners contain functions that get called each time an Event is processed. You can then perform discrete functionality on each event in the order they are processed. This example shows you what you need to do to set the necessary plumbing and make use of Event Listeners.

