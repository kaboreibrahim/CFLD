from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('medias', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='photo',
            name='auteur',
            field=models.CharField(blank=True, max_length=100, verbose_name='Auteur / Photographe'),
        ),
    ]
