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


def human_readable_format(x: float) -> str:
    """specific to dex screener"""
    x0 = x
    try:
        if x < 1:
            # 0 <= x < 1 and x < 0 case all g
            return str(x)
        suffixes = ["", "k", "M", "B", "T"]
        for i in range(len(suffixes)):
            if x >= 1000:
                x /= 1000
                continue
            x: str = str(float(x)) + "000"
            x = x[:3] if x.find(".") == 3 else x[:4]
            return x + suffixes[i]
        return ">1e15"  # can never be <-1e15
    except:
        pass
    return f"{x0:,}"
