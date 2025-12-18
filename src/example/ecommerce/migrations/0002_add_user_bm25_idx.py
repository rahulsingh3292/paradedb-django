from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ("ecommerce", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunSQL(
            "create index user_bm25_idx on auth_user "
            "using bm25(id, (username::pdb.ngram(1,2)), email, first_name, last_name, "
            "date_joined, is_active) with (key_field=id)"
        )
    ]
