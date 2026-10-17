# Data Pipelines Portfolio

**Kevin Daniel Castellanos Chan**

Four projects that follow one path through a data pipeline: query a relational database, pull records from an API, land them in a raw store and a clean store, and schedule the job.

| Project | What it shows | Stack |
| --- | --- | --- |
| [SQL analytics](sql-analytics/) | Filters, aggregates, and a ranked product list on the Northwind schema | SQL, SQLite |
| [API requests](api-requests/) | A small extract, transform, and load script against a public REST API | Python, requests |
| [MongoDB ETL](mongodb-etl/) | Paginated ingestion, a raw layer, a clean layer, and upserts | Python, MongoDB, Docker |
| [Airflow orchestration](airflow-orchestration/) | A daily weather DAG, plus a parallel API workflow | Apache Airflow, pandas |

Each folder stands on its own. The next one adds a tool the previous one did not need.

SQL is the analytical layer. The API script is the first ingestion. MongoDB is where raw and cleaned documents live. Airflow is what runs the job on a schedule and passes data between tasks.

Local virtual environments, scheduler logs, and lab notes are not in this repository. The MongoDB passwords in `docker-compose.yml` are defaults for that local stack only.
