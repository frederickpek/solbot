def format_number(x, sf=4) -> str:
    if float(x) > 1:
        return f"{float(x):,.2f}"
    x += "10" * sf
    for i, c in enumerate(x):
        if c == "0" or c == ".":
            continue
        return x[: i + sf]
    return "0.0"


def price_percent_change_to_float(price_change: str):
    """For Gecko Terminal"""
    return float(price_change.replace("%", ""))
