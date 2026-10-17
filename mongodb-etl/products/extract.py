"""Fetch one page of products from DummyJSON without modifying the payload."""

import time
import requests
from datetime import datetime, timezone

# Endpoint base del API (no necesita token)
BASE_URL = "https://dummyjson.com/products"


def extract_products_batch(skip=0, limit=20, delay_seconds=1.0, timeout=15):
    """
    Extrae UN batch de productos desde DummyJSON.

    Params:
      skip  -> desde qué producto empezar (paginación)
      limit -> cuántos productos traer en este batch
      delay_seconds -> pause between requests
      timeout -> para que no se quede colgado

    Return:
      dict con:
        - metadata: info del batch
        - raw: el JSON completo del API (SIN modificar)
      o None si falla.
    """
    try:
        # 1) Armamos los parámetros de paginación
        params = {"limit": limit, "skip": skip}

        # 2) Hacemos la request al API
        print(f"  [EXTRACT] GET {BASE_URL} | skip={skip} limit={limit}")
        resp = requests.get(BASE_URL, params=params, timeout=timeout)
        resp.raise_for_status()  # si hay error HTTP, aquí truena

        # 3) Convertimos la respuesta a JSON (tal cual lo manda el API)
        raw_json = resp.json()

        # 4) Short pause so the client does not hammer the API
        time.sleep(delay_seconds)

        # 5) Agregamos metadata útil para el pipeline (sin tocar los datos)
        fetched_at = datetime.now(timezone.utc).isoformat()

        return {
            "metadata": {
                "source": "dummyjson/products",
                "endpoint": BASE_URL,
                "fetched_at": fetched_at,
                "skip": skip,
                "limit": limit,
                # Estos campos vienen del API normalmente:
                "total": raw_json.get("total"),
                "count": len(raw_json.get("products", [])),
            },
            # raw = el JSON completo intacto (esto es lo que luego guardamos en RAW)
            "raw": raw_json,
        }

    except requests.RequestException as e:
        # Si falla internet, el API, o hay timeout, caemos aquí
        print(f"  [EXTRACT] ERROR: {e}")
        return None


# Local check for this module. The full pipeline runs from main.py.
if __name__ == "__main__":
    b1 = extract_products_batch(skip=0, limit=5)
    b2 = extract_products_batch(skip=5, limit=5)

    print("Batch1 count:", 0 if not b1 else b1["metadata"]["count"])
    print("Batch2 count:", 0 if not b2 else b2["metadata"]["count"])