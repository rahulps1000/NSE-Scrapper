from pymongo import MongoClient, ASCENDING
from pymongo.errors import BulkWriteError
from datetime import datetime
from config import Config


class MongoDB:
    def __init__(self):
        self.client = MongoClient(Config.DB_URI)

        self.db = self.client["NSE"]
        self.option_chain_collection = self.db["option_chain"]

        self._create_indexes()

    def _create_indexes(self):
        """
        Run once during startup.
        """
        self.option_chain_collection.create_index([
            ("symbol", ASCENDING),
            ("expiry", ASCENDING),
            ("strike", ASCENDING),
            ("type", ASCENDING),
            ("ts", ASCENDING)
        ])

        self.option_chain_collection.create_index([
            ("ts", ASCENDING)
        ])

    def insert_snapshot(self, documents):
        """
        Insert all option contracts for a single snapshot.

        documents = [
            {
                "ts": datetime(...),
                "symbol": "NIFTY",
                "expiry": datetime(...),
                "strike": 23000,
                "type": "PE",
                "spot": 23989.15,
                "ltp": 60,
                "iv": 15.41,
                "oi": 371,
                "oiChg": 130,
                "volume": 421
            }
        ]
        """

        if not documents:
            return 0

        try:
            result = self.option_chain_collection.insert_many(
                documents,
                ordered=False
            )

            return len(result.inserted_ids)

        except BulkWriteError as e:
            print(f"Bulk insert failed: {e.details}")
            return 0

    def get_option_history(
        self,
        symbol,
        strike,
        option_type,
        expiry,
        start_time=None,
        end_time=None
    ):
        query = {
            "symbol": symbol,
            "strike": strike,
            "type": option_type,
            "expiry": expiry
        }

        if start_time or end_time:
            query["ts"] = {}

            if start_time:
                query["ts"]["$gte"] = start_time

            if end_time:
                query["ts"]["$lte"] = end_time

        return list(
            self.option_chain_collection.find(
                query,
                {"_id": 0}
            ).sort("ts", 1)
        )

    def get_snapshot(self, timestamp):
        return list(
            self.option_chain_collection.find(
                {"ts": timestamp},
                {"_id": 0}
            )
        )

    def get_latest_snapshot(self, symbol="NIFTY"):
        doc = self.option_chain_collection.find_one(
            {"symbol": symbol},
            sort=[("ts", -1)]
        )

        return doc

    def delete_before(self, date):
        """
        Optional cleanup.
        """
        result = self.option_chain_collection.delete_many(
            {"ts": {"$lt": date}}
        )

        return result.deleted_count

    def close(self):
        self.client.close()