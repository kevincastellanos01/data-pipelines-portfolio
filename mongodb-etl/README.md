# MongoDB ETL

Two pipelines read a public API and upsert into MongoDB. They share one local database from Docker Compose, and they use different databases so a product run cannot overwrite a launch run.

| Pipeline | Source | Database |
| --- | --- | --- |
| [products](products/) | [DummyJSON Products](https://dummyjson.com/products) | `dummyjson_products_db` |
| [launches](launches/) | [SpaceX API v4](https://github.com/r-spacex/SpaceX-API) `/launches/query` | `spacex_launches_db` |

## Why there is a raw layer and a clean layer

The products pipeline stores every page twice.

`raw_products` keeps the API JSON as it arrived, plus `ingested_at` and a `batch_id` built from source, skip, and limit. If a price rule or a stock label changes, I can rebuild the clean collection from this layer without calling DummyJSON again. The `batch_id` upsert means the same page updates in place. A second run does not append another copy of page one.

`clean_products` is one document per product. Text is trimmed and cased, `final_price` applies the discount, and `stock_status` is `out_of_stock`, `low` (10 or fewer), or `in_stock`. `processed_at` and `source` record when that rule ran and where the row came from. The upsert key is `product_id`. Rerunning the job refreshes the product. It does not create a second document for the same id.

A failed page is skipped. One timeout should not throw away the pages that already loaded.

## Why launches are a single collection

SpaceX launches are already one entity per document, so I did not split them into raw and clean. The transform is the contract:

- `date_utc` becomes `launch_date`, `launch_year`, and `launch_month`, which are the fields a count-by-month query needs.
- `success` can be true, false, or null, and `upcoming` is separate. `success_label` collapses that into `upcoming`, `success`, `failure`, or `unknown`, which is what the summary aggregation groups on.
- Cores and payloads stay as ids, with `core_count` and `payload_count` stored beside them.
- Webcast, article, Wikipedia, and patch URLs are flattened. Filtering a nested `links.patch.small` from the shell is slower to write than filtering `patch_small`.

The upsert key is `launch_id`. After the load, the script prints how many flights fall into each `success_label` and which `rocket_id` appears most often. That check tells me the load matches the labels I just derived.

Pages come from `POST /launches/query`, newest first. The default run requests two pages of 25.

## Run

```bash
docker compose up -d
pip install -r requirements.txt

cd products && python main.py
cd ../launches && python main.py
```

Mongo Express is at [http://localhost:8081](http://localhost:8081). The web login is `admin` / `admin123`. The database login is `admin` / `password123`. Both are for this local Compose file.

```bash
docker compose down
```

`docker compose down -v` deletes the data volume.
