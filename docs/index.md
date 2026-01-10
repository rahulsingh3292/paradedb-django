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
- Full-text search backed by ParadeDB’s **BM25** index
- Rich expressions and lookups:
  - `Match`
  - `Range`
  - `Term`
  - `Boolean`
  - Range queries and more
- Aggregations
- Extension support for ParadeDB `pg_search`
- Support for **V2 syntax**
- Custom ParadeDB operators for `JSONField`
  (see [JsonOp Expression](./expressions.md#jsonop))
- And more...

---

## Supported Versions

- **>= 0.19.11**
- **0.20+**

---

## Install on Ubuntu

```bash
sudo apt-get install -y libicu70
curl -L "https://github.com/paradedb/paradedb/releases/download/v0.19.6/postgresql-17-pg-search_0.19.6-1PARADEDB-noble_amd64.deb" -o /tmp/pg_search.deb
sudo apt-get install -y /tmp/*.deb
```

### Configure PostgreSQL

Edit `postgresql.conf`

```bash
shared_preload_libraries = 'pg_search'
```

Restart PostgreSQL and create the extension:

```sql
CREATE EXTENSION IF NOT EXISTS pg_search;
```

> ⚠ Facing issues or need more details?
> See ParadeDB installation:
>
> * [Manual Installation](https://docs.paradedb.com/deploy/self-hosted/extension)
> * [Docker Setup](https://docs.paradedb.com/deploy/self-hosted/docker)

---

## Install Python Package

Make sure the `pg_search` extension from ParadeDB is installed in your PostgreSQL database.

If not installed, see:
[Installation Guide](https://docs.paradedb.com/documentation/getting-started/install)

```bash
pip install paradedb-django
```

---

## Add to `INSTALLED_APPS`

```python
INSTALLED_APPS = [
    ...,
    'paradedb',
]
```

---

## You're Ready 🚀

You can now start using ParadeDB features inside Django.

---

## 📚 Learn More
* [Getting Started](./getting-started.md)
* [Expressions](./expressions.md)
* [Indexes](./index.md)
* [Aggregations](./aggregations.md)
* [Lookups](./lookups.md)

---
