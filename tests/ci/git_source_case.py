"""Real repository source used by the Git-environment learning experiment."""


def total_by_customer(purchases):
    totals = {}
    for purchase in purchases:
        customer = purchase["buyer"]
        totals[customer] = totals.get(customer, 0) + purchase["price"]
    return totals
