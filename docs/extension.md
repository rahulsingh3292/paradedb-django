## ParadeDB / PGSearch Extensions

ParadeDB allows you to create PostgreSQL extensions directly from Django migrations using the `ParadeDbExtension`.

### Usage

```python
from django.db import migrations
from paradedb.extension import ParadeDbExtension

class Migration(migrations.Migration):

    dependencies = [
        # your migration dependencies here
    ]

    operations = [
        ParadeDbExtension(),  # Creates the "pg_search" extension by default
    ]
```

> Make sure that the PostgreSQL server allows creating extensions and that your database user has sufficient privileges.

---
