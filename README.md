# Data pipelines

**Kevin Daniel Castellanos Chan**

I built these pipelines to move data from a source into a shape that can be queried again. Each folder is one stage of that path.

| Project | Decision it forced | Stack |
| --- | --- | --- |
| [SQL analytics](sql-analytics/) | Which rows belong in an operational report, and which should stay out | SQL, SQLite |
| [API requests](api-requests/) | What to keep from a large nested response | Python, requests |
| [MongoDB ETL](mongodb-etl/) | Where the original payload lives, and how a second run avoids duplicates | Python, MongoDB, Docker |
| [Airflow orchestration](airflow-orchestration/) | How a daily job passes data between tasks and what happens if it was paused | Apache Airflow, pandas |

The SQL folder is the questions I want answered from tables that already exist. The API script is the first time the data does not exist locally, so the script has to define the record it will store. MongoDB is where that record is split into a raw layer and a clean layer. Airflow is what runs a job every day and carries the payload from extract to load.

The MongoDB passwords in `docker-compose.yml` belong to that local stack. Override them with `MONGO_HOST`, `MONGO_PORT`, `MONGO_USERNAME`, and `MONGO_PASSWORD`.
