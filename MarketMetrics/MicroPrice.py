
def size_weighted_midpoint(bid_price, bid_qty, ask_price, ask_qty):
    bid_plus_ask_qty = bid_qty + ask_qty
    if bid_plus_ask_qty == 0:
        return None
    return ((bid_qty * ask_price) + (ask_qty * bid_price)) / bid_plus_ask_qty


def size_weighted_midpoint_from_price_levels(bid_price_level, ask_price_level, include_hidden=False):
    if bid_price_level is None or ask_price_level is None:
        return None
    bid_qty = bid_price_level.visible_qty()
    ask_qty = ask_price_level.visible_qty()
    if include_hidden:
        bid_qty += bid_qty + bid_price_level.hidden_qty()
        ask_qty += ask_qty + ask_price_level.hidden_qty()
    return size_weighted_midpoint(bid_price_level.price(), bid_qty, ask_price_level.price(), ask_qty)
