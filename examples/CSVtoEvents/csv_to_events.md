# CSV to Events

This example:
1. Reads a "csv" (a `StringIO` representation of a CSV of events data)
2. Parses each line in the csv and creates the necessary order events (both commands and execution reports)
3. Prints out the `to_json()` of each of the order events

1 and 2 above are all the logic you really care about for learning the creation of order events. It can be found in the `get_events()` function.

Some of this code is reused in other examples, so this example is a great starting point.

