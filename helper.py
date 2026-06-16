from datetime import datetime, timedelta, timezone
import time

import pytz

IST = pytz.timezone("Asia/Kolkata")


def is_market_open():
    now = datetime.now(IST)

    # Monday-Friday
    if now.weekday() > 4:
        return False

    market_open = now.replace(
        hour=9,
        minute=15,
        second=0,
        microsecond=0
    )

    market_close = now.replace(
        hour=15,
        minute=30,
        second=0,
        microsecond=0
    )

    return market_open <= now <= market_close

def sleep_until_next_interval():
    now = datetime.now(IST)

    next_minute = ((now.minute // 3) + 1) * 3

    if next_minute >= 60:
        target = (
            now.replace(
                minute=0,
                second=0,
                microsecond=0
            ) + timedelta(hours=1)
        )
    else:
        target = now.replace(
            minute=next_minute,
            second=0,
            microsecond=0
        )

    time.sleep((target - now).total_seconds())

def transform_nse_option_chain(data, snapshot_time=None):
    """
    Convert NSE option chain response to a compact format
    suitable for Greeks calculation and MongoDB storage.
    """

    if snapshot_time is None:
        snapshot_time = datetime.now(timezone.utc)

    documents = []

    for record in data["records"]["data"]:

        # Process CE
        ce = record.get("CE")
        if ce and ce.get("identifier"):
            documents.append({
                "ts": snapshot_time,
                "symbol": ce["underlying"],
                "expiry": datetime.strptime(
                    ce["expiryDate"],
                    "%d-%m-%Y"
                ),
                "strike": ce["strikePrice"],
                "type": "CE",

                # Greeks inputs
                "spot": ce["underlyingValue"],
                "ltp": ce["lastPrice"],
                "iv": ce["impliedVolatility"],

                # Market metrics
                "oi": ce["openInterest"],
                "oiChg": ce["changeinOpenInterest"],
                "volume": ce["totalTradedVolume"]
            })

        # Process PE
        pe = record.get("PE")
        if pe and pe.get("identifier"):
            documents.append({
                "ts": snapshot_time,
                "symbol": pe["underlying"],
                "expiry": datetime.strptime(
                    pe["expiryDate"],
                    "%d-%m-%Y"
                ),
                "strike": pe["strikePrice"],
                "type": "PE",

                # Greeks inputs
                "spot": pe["underlyingValue"],
                "ltp": pe["lastPrice"],
                "iv": pe["impliedVolatility"],

                # Market metrics
                "oi": pe["openInterest"],
                "oiChg": pe["changeinOpenInterest"],
                "volume": pe["totalTradedVolume"]
            })

    return documents