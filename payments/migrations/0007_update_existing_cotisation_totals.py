from decimal import Decimal

from django.db import migrations


def forwards(apps, schema_editor):
    CotisationAnnuelle = apps.get_model("payments", "CotisationAnnuelle")
    CotisationAnnuelle.objects.filter(
        montant_total=Decimal("1000000")
    ).update(
        montant_total=Decimal("1200000")
    )


def backwards(apps, schema_editor):
    CotisationAnnuelle = apps.get_model("payments", "CotisationAnnuelle")
    CotisationAnnuelle.objects.filter(
        montant_total=Decimal("1200000")
    ).update(
        montant_total=Decimal("1000000")
    )


class Migration(migrations.Migration):

    dependencies = [
        ("payments", "0006_alter_cotisationannuelle_montant_total"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
