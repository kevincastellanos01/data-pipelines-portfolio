"""Load DummyJSON batches into raw and clean MongoDB collections."""

import os
from datetime import datetime, timezone
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure

MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "password123")

DATABASE_NAME = "dummyjson_products_db"

# Dos colecciones (raw y clean) en la misma DB
RAW_COLLECTION = "raw_products"
CLEAN_COLLECTION = "clean_products"


def get_mongo_connection():
    """
    Conecta a MongoDB y regresa un MongoClient.
    Regresa None si falla la conexión.
    """
    try:
        uri = f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@{MONGO_HOST}:{MONGO_PORT}/"
        client = MongoClient(uri, serverSelectionTimeoutMS=5000)

        # Ping para verificar que sí conectó
        client.admin.command("ping")
        print("  [LOAD] Connected to MongoDB successfully!")
        return client

    except ConnectionFailure as e:
        print(f"  [LOAD] ERROR: Could not connect to MongoDB — {e}")
        print("  [LOAD] Check Docker: docker compose up -d")
        return None


def load_raw(extract_payload):
    """
    Guarda el payload crudo (raw) del API en la colección RAW.

    Importante:
    - Guardamos el JSON intacto (raw)
    - Agregamos ingested_at (timestamp)
    - Upsert usando una key del batch para no duplicar el mismo batch

    Return:
      cantidad de batches guardados (normalmente 1 si todo salió bien)
    """
    if not extract_payload or "raw" not in extract_payload:
        print("  [LOAD_RAW] No raw payload to load")
        return 0

    client = get_mongo_connection()
    if client is None:
        return 0

    try:
        db = client[DATABASE_NAME]
        collection = db[RAW_COLLECTION]

        # Timestamp for the raw layer
        ingested_at = datetime.now(timezone.utc).isoformat()

        # Vamos a crear un ID único por batch con skip+limit+source
        meta = extract_payload.get("metadata", {})
        source = meta.get("source", "dummyjson/products")
        skip = meta.get("skip", None)
        limit = meta.get("limit", None)

        batch_id = f"{source}|skip={skip}|limit={limit}"

        raw_doc = {
            "batch_id": batch_id,              # clave única del batch (para upsert)
            "ingested_at": ingested_at,        # requerido (raw load timestamp)
            "metadata": meta,                  # metadata del extract
            "raw": extract_payload["raw"],     # JSON crudo intacto
        }

        # UPSERT: si ya existe ese batch_id, lo actualiza; si no, lo inserta
        collection.update_one(
            {"batch_id": batch_id},
            {"$set": raw_doc},
            upsert=True
        )

        total = collection.count_documents({})
        print(f"  [LOAD_RAW] Upserted 1 batch into '{RAW_COLLECTION}'. Total batches: {total}")

        return 1

    except OperationFailure as e:
        print(f"  [LOAD_RAW] Mongo operation error: {e}")
        return 0

    finally:
        try:
            client.close()
            print("  [LOAD_RAW] MongoDB connection closed.")
        except Exception:
            pass


def load_clean(clean_records):
    """
    Guarda los registros limpios/transformados en la colección CLEAN.

    Importante:
    - clean_records es una lista de dicts (salida de transform.py)
    - Upsert por product_id para NO duplicar productos

    Return:
      cantidad de docs upserted (igual al tamaño del batch)
    """
    if not clean_records:
        print("  [LOAD_CLEAN] No clean records to load")
        return 0

    client = get_mongo_connection()
    if client is None:
        return 0

    try:
        db = client[DATABASE_NAME]
        collection = db[CLEAN_COLLECTION]

        loaded = 0

        for doc in clean_records:
            # Upsert por product_id (key única del producto)
            collection.update_one(
                {"product_id": doc["product_id"]},
                {"$set": doc},
                upsert=True
            )
            loaded += 1

        total = collection.count_documents({})
        print(f"  [LOAD_CLEAN] Batch upserted: {loaded}. Total clean docs: {total}")

        return loaded

    except OperationFailure as e:
        print(f"  [LOAD_CLEAN] Mongo operation error: {e}")
        return 0

    finally:
        try:
            client.close()
            print("  [LOAD_CLEAN] MongoDB connection closed.")
        except Exception:
            pass


# Mini prueba (opcional)
if __name__ == "__main__":
    fake_extract = {
        "metadata": {"source": "dummyjson/products", "skip": 0, "limit": 2},
        "raw": {"products": [{"id": 1}, {"id": 2}], "total": 2, "skip": 0, "limit": 2},
    }

    # Cargar raw (batch)
    load_raw(fake_extract)

    # Cargar clean (2 docs)
    load_clean([
        {"product_id": 1, "title": "Test", "processed_at": "x", "source": "y"},
        {"product_id": 2, "title": "Test2", "processed_at": "x", "source": "y"},
    ])