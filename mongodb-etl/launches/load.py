"""Upsert SpaceX launches into MongoDB and print a short summary."""

import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "password123")

DATABASE_NAME = "spacex_launches_db"
COLLECTION_NAME = "launches"


def get_mongo_connection():
    """
    Connect to MongoDB and return a MongoClient.
    Return None if the connection fails.
    """
    try:
        uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)
        client.admin.command("ping")
        print("  [LOAD_SPACEX] Connected to MongoDB successfully!")
        return client
    except ConnectionFailure as e:
        print(f"  [LOAD_SPACEX] ERROR: Could not connect to MongoDB — {e}")
        print("  [LOAD_SPACEX] Make sure Docker is running: docker compose up -d")
        return None


def print_spacex_summary(collection):
    """
    Print total records, a success breakdown, and the most common rocket id.
    """
    try:
        total = collection.count_documents({})

        success_breakdown = list(
            collection.aggregate(
                [
                    {"$group": {"_id": "$success_label", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                ]
            )
        )

        top_rocket = list(
            collection.aggregate(
                [
                    {"$group": {"_id": "$rocket_id", "count": {"$sum": 1}}},
                    {"$sort": {"count": -1}},
                    {"$limit": 1},
                ]
            )
        )

        print("  [LOAD_SPACEX] ---- Data Summary ----")
        print(f"  [LOAD_SPACEX] Total launches: {total}")

        if success_breakdown:
            print("  [LOAD_SPACEX] Success breakdown:")
            for row in success_breakdown:
                label = row["_id"] if row["_id"] is not None else "unknown"
                print(f"    - {label}: {row['count']}")

        if top_rocket and top_rocket[0].get("_id"):
            print(f"  [LOAD_SPACEX] Most common rocket_id: {top_rocket[0]['_id']} ({top_rocket[0]['count']} launches)")

        print("  [LOAD_SPACEX] ----------------------")

    except Exception as e:
        print(f"  [LOAD_SPACEX] Summary error (non-fatal): {e}")


def load_spacex_launches(transformed_data):
    """
    Load a list of transformed SpaceX launch dicts into MongoDB using upsert.
    Returns the number of documents upserted in this call.
    """
    if not transformed_data:
        print("  [LOAD_SPACEX] No data to load")
        return 0

    client = get_mongo_connection()
    if client is None:
        return 0

    try:
        db = client[DATABASE_NAME]
        collection = db[COLLECTION_NAME]

        loaded_count = 0

        for doc in transformed_data:
            # Upsert by unique key
            collection.update_one(
                {"launch_id": doc["launch_id"]},
                {"$set": doc},
                upsert=True,
            )
            loaded_count += 1

        total_docs = collection.count_documents({})
        print(f"  [LOAD_SPACEX] Batch upserted: {loaded_count}")
        print(f"  [LOAD_SPACEX] Total documents in '{DATABASE_NAME}.{COLLECTION_NAME}': {total_docs}")

        # Bonus summary (optional but nice)
        print_spacex_summary(collection)

        return loaded_count

    except OperationFailure as e:
        print(f"  [LOAD_SPACEX] Error during load: {e}")
        return 0

    finally:
        try:
            client.close()
            print("  [LOAD_SPACEX] MongoDB connection closed.")
        except Exception:
            pass