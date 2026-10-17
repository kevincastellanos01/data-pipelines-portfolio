"""Clean product records and add derived price, stock, and metadata fields."""

from datetime import datetime, timezone


def _clean_text(text):
    """
    Helper simple para limpiar texto:
    - convierte None a ""
    - quita espacios al inicio/fin
    - colapsa espacios dobles dentro del texto
    """
    if text is None:
        return ""
    # strip() quita espacios al inicio/fin
    # split() separa por espacios y luego join() los vuelve a unir con 1 espacio
    return " ".join(str(text).strip().split())


def transform_products(extract_payload):
    """
    Recibe lo que regresa extract.py, algo así:
    {
      "metadata": {...},
      "raw": { "products": [...], "total": ..., "skip": ..., "limit": ... }
    }

    Devuelve una lista de diccionarios LIMPIOS listos para cargar a "clean".
    """
    if not extract_payload or "raw" not in extract_payload:
        print("  [TRANSFORM] No payload to transform")
        return []

    raw_json = extract_payload["raw"]
    products = raw_json.get("products", [])

    if not products:
        print("  [TRANSFORM] No products in this batch")
        return []

    # Metadata requerida
    processed_at = datetime.now(timezone.utc).isoformat()
    source = extract_payload.get("metadata", {}).get("source", "dummyjson/products")

    transformed = []

    for p in products:
        # --- Campos originales del API ---
        product_id = p.get("id")  # clave única del producto (nos servirá para upsert)
        title = p.get("title")
        brand = p.get("brand")
        category = p.get("category")
        description = p.get("description")
        price = p.get("price")  # normalmente int/float
        discount_percentage = p.get("discountPercentage")  # normalmente float
        rating = p.get("rating")
        stock = p.get("stock")

        # -------------------------------
        # 1) LIMPIAR / ESTANDARIZAR CAMPOS
        # -------------------------------
        # Limpieza básica de texto
        title_clean = _clean_text(title).title()        # "iphone 9" -> "Iphone 9"
        brand_clean = _clean_text(brand).title()        # estandarizamos brand
        category_clean = _clean_text(category).lower()  # categoría en minúsculas
        description_clean = _clean_text(description)

        # --------------------------------
        # 2) CAMPOS DERIVADOS (CALCULADOS)
        # --------------------------------
        # Ejemplo: precio final con descuento
        # Nota: discountPercentage viene como porcentaje, ej. 12.96
        final_price = None
        if price is not None and discount_percentage is not None:
            try:
                final_price = round(float(price) * (1 - (float(discount_percentage) / 100)), 2)
            except (ValueError, TypeError):
                final_price = None

        # Ejemplo: etiqueta de inventario (stock)
        stock_status = "unknown"
        if isinstance(stock, (int, float)):
            if stock == 0:
                stock_status = "out_of_stock"
            elif stock <= 10:
                stock_status = "low"
            else:
                stock_status = "in_stock"

        # Otro derivado sencillo: tamaño de descripción
        description_length = len(description_clean)

        # --------------------------------
        # 3) METADATA (processed_at + source)
        # --------------------------------
        clean_doc = {
            # clave para upsert
            "product_id": product_id,

            # campos limpios
            "title": title_clean,
            "brand": brand_clean,
            "category": category_clean,
            "description": description_clean,

            # números
            "price": price,
            "discount_percentage": discount_percentage,
            "final_price": final_price,  # derivado
            "rating": rating,
            "stock": stock,
            "stock_status": stock_status,  # derivado
            "description_length": description_length,  # derivado

            # metadata requerida
            "processed_at": processed_at,
            "source": source,
        }

        transformed.append(clean_doc)

    print(f"  [TRANSFORM] Transformed records: {len(transformed)}")
    return transformed


# Mini prueba rápida (opcional)
if __name__ == "__main__":
    # Simulamos un payload como el de extract.py
    sample = {
        "metadata": {"source": "dummyjson/products"},
        "raw": {
            "products": [
                {
                    "id": 1,
                    "title": "  iphone   9 ",
                    "brand": " apple ",
                    "category": "SMARTPHONES",
                    "description": "  A phone   with  great camera  ",
                    "price": 549,
                    "discountPercentage": 12.96,
                    "rating": 4.69,
                    "stock": 5,
                }
            ]
        },
    }

    out = transform_products(sample)
    print(out[0])