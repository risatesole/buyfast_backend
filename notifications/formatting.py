def format_currency_dop(amount):
    return f"RD$ {amount:,.2f}"


def format_pickup_time(dt):
    if dt is None:
        return ""
    return dt.strftime("%d/%m/%Y, %I:%M %p")
