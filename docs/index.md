<p align="center">
  <img src="assets/logo.png" width="500" alt="logo" />
</p>

<p align="center">
  <strong>Bring the full power of ParadeDB into Django.</strong>
</p>

<p align="center">
  Build sophisticated, composable search queries effortlessly, and leverage
  advanced indexing, search, and ranking at blazing speed — all inside PostgreSQL.
</p>

<h1></h1>

---

## Features
- Full-text search backed by ParadeDB’s BM25 index
- Rich expression and lookups: `Match`, `Range`, `Term`,  `Boolean`, range queries, and more
-  Aggregation
-  Extension for ParadeDB `pg_search`
- Support V2 Syntax
- And More ...

---

## Supported Version

- > 0.19.11 - 0.20+

----

## Install on ubuntu

``` bash
sudo apt-get install -y libicu70
curl -L "https://github.com/paradedb/paradedb/releases/download/v0.19.6/postgresql-17-pg-search_0.19.6-1PARADEDB-noble_amd64.deb" -o /tmp/pg_search.deb
sudo apt-get install -y /tmp/*.deb
```
in the `postgresql.conf`
``` bash
shared_preload_libraries = 'pg_search'
```
create the extension
``` bash
CREATE EXTENSION IF NOT EXISTS pg_search;
```

> * Facing Issues or need more detail, see ParadeDb installation [Manually](https://docs.paradedb.com/deploy/self-hosted/extension) or via [Docker](https://docs.paradedb.com/deploy/self-hosted/docker)

---


##  Install
Make sure the `pg_search` extension from ParadeDB is installed in your PostgreSQL database.
If it is not installed, see the [**Installation**](https://docs.paradedb.com/documentation/getting-started/install) section below. <br>

```bash
pip install paradedb-django
```

## Add to **installed_apps**
```bash
INSTALLED_APPS = [
    ...,
    'paradedb'
]
```

---
