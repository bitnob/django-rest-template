"""
To understand why this file is here, please read:

http://cookiecutter-django.readthedocs.io/en/latest/faq.html#why-is-there-a-django-contrib-sites-directory-in-cookiecutter-django
"""

from django.db import migrations
from django.conf import settings


def update_site_forward(apps, schema_editor):
    """Set site domain and name."""
    Site = apps.get_model("sites", "Site")
    Site.objects.update_or_create(
        id=settings.SITE_ID,
        defaults={
            "domain": "Antcorp.ng",
            "name": "Antcorp",
        },
    )

    Site.objects.update_or_create(
        id=2,
        defaults={
            "domain": "localhost:8000",
            "name": "Antcorp",
        },
    )


#

def update_site_backward(apps, schema_editor):
    """Revert site domain and name to default."""
    Site = apps.get_model("sites", "Site")
    Site.objects.update_or_create(
        id=settings.SITE_ID, defaults={"domain": "exampl.ecom", "name": "Antcorp"}
    )


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [migrations.RunPython(update_site_forward, update_site_backward)]


