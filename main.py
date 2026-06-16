import time
import traceback

from datetime import datetime

from nse import fetch_option_chain
from helper import transform_nse_option_chain, is_market_open, IST, sleep_until_next_interval
from mongodb import MongoDB


def run():
    print("Starting application...",flush=True)
    mongo = MongoDB()
    print("MongoDB connected",flush=True)

    while True:
        try:
            now = datetime.now(IST)

            if is_market_open():
                print(f"[{now}] Fetching option chain...",flush=True)

                data = fetch_option_chain(
                    "NIFTY",
                    "14-Jul-2026"
                )

                transformed_data = transform_nse_option_chain(
                    data,
                    snapshot_time=now
                )

                inserted_count = mongo.insert_snapshot(
                    transformed_data
                )

                print(f"[{now}] Inserted {inserted_count} records",flush=True)

            else:
                print(f"[{now}] Market closed",flush=True)

        except Exception:
            traceback.print_exc()
            print(f"[{now}] An error occurred - {traceback.format_exc()}",flush=True)

        sleep_until_next_interval()


if __name__ == "__main__":
    run()