"""Orchestrate the products pipeline: extract, load raw, transform, load clean."""

import time
from datetime import datetime

from extract import extract_products_batch
from transform import transform_products
from load import load_raw, load_clean


def run_etl(total_batches=2, limit=20):
    """Run the pipeline in pages. A failed page is skipped.

    total_batches: number of pages to process
    limit: products requested per page
    """
    print("=" * 60)
    print("   DUMMYJSON PRODUCTS ETL (RAW + CLEAN)")
    print("=" * 60)

    start_time = time.time()

    # Contadores para el resumen final
    total_raw_batches_loaded = 0
    total_clean_docs_loaded = 0
    total_extracted_products = 0

    print(f"   Start time : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Batches    : {total_batches}")
    print(f"   Batch size : {limit}")
    print("=" * 60)

    # Vamos a correr mínimo 2 batches
    for batch_num in range(1, total_batches + 1):
        # skip sirve para paginar: batch1 -> 0, batch2 -> limit, batch3 -> 2*limit, etc.
        skip = (batch_num - 1) * limit

        print(f"\n{'─' * 60}")
        print(f"   BATCH {batch_num}/{total_batches} | skip={skip} limit={limit}")
        print(f"{'─' * 60}")

        batch_t0 = time.time()

        # 1) EXTRACT
        extract_payload = extract_products_batch(skip=skip, limit=limit, delay_seconds=1.0)
        if extract_payload is None:
            print("  [PIPELINE] Skipping batch (extract failed)")
            continue

        extracted_count = extract_payload.get("metadata", {}).get("count", 0)
        total_extracted_products += extracted_count
        print(f"  [PIPELINE] Extracted products: {extracted_count}")

        # 2) LOAD RAW (guardar JSON crudo)
        raw_loaded = load_raw(extract_payload)
        total_raw_batches_loaded += raw_loaded

        # 3) TRANSFORM (limpieza + campos derivados + metadata)
        clean_records = transform_products(extract_payload)
        if not clean_records:
            print("  [PIPELINE] Skipping clean load (no transformed records)")
            continue

        # 4) LOAD CLEAN (guardar data limpia)
        clean_loaded = load_clean(clean_records)
        total_clean_docs_loaded += clean_loaded

        batch_dt = time.time() - batch_t0
        print(f"  [PIPELINE] Batch {batch_num} finished in {batch_dt:.2f}s")

    total_dt = time.time() - start_time

    # Resumen final
    print(f"\n{'=' * 60}")
    print("   PIPELINE COMPLETE")
    print(f"{'=' * 60}")
    print(f"   Total products extracted   : {total_extracted_products}")
    print(f"   Raw batches loaded         : {total_raw_batches_loaded}")
    print(f"   Clean documents upserted   : {total_clean_docs_loaded}")
    print(f"   Total time                 : {total_dt:.2f}s")
    print(f"{'=' * 60}")
    print("   Mongo Express: http://localhost:8081")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    run_etl(total_batches=2, limit=20)