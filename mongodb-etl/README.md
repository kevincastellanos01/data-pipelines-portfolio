# MongoDB ETL

Two batch pipelines that read a public API and upsert documents into MongoDB. Both use the same local database started with Docker Compose.

| Pipeline | Source | Database | Pattern |
| --- | --- | --- | --- |
| [products](products/) | [DummyJSON Products](https://dummyjson.com/products) | `dummyjson_products_db` | Extract, load raw, transform, load clean |
| [launches](launches/) | [SpaceX API v4](https://github.com/r-spacex/SpaceX-API) `/launches/query` | `spacex_launches_db` | Extract, transform, load |

## Products

DummyJSON is paginated with `limit` and `skip`. Each page is stored twice:

- `raw_products` keeps the API payload, plus `ingested_at` and a `batch_id`.
- `clean_products` keeps one document per product.

The clean step standardizes text, computes `final_price` from the discount, labels stock as `out_of_stock`, `low`, or `in_stock`, and stamps `processed_at` and `source`. Upserts use `product_id`, so a second run updates the same products instead of duplicating them. A failed page is skipped and the rest of the run continues.

## Launches

SpaceX pages come from a `POST` to `/launches/query`. The transform parses `date_utc`, derives year and month, counts cores and payloads, and labels each flight as `upcoming`, `success`, `failure`, or `unknown`. Links are flattened so the document is easy to query. Upserts use `launch_id`. After the load, the script prints a success breakdown and the most common rocket id.

## Run

From this folder:

```bash
docker compose up -d
pip install -r requirements.txt

cd products && python main.py
cd ../launches && python main.py
```

Mongo Express is at [http://localhost:8081](http://localhost:8081). The web login is `admin` / `admin123`. The database login is `admin` / `password123`.

These values are for the local Compose stack. Override the Python connection with `MONGO_HOST`, `MONGO_PORT`, `MONGO_USERNAME`, and `MONGO_PASSWORD`.

```bash
docker compose down
```

`docker compose down -v` also deletes the data volume.
