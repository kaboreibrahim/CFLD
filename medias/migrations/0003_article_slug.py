import re
from django.db import migrations, models


def _slugify_fr(text):
    text = text.lower()
    replacements = {
        'é': 'e', 'è': 'e', 'ê': 'e', 'ë': 'e',
        'à': 'a', 'â': 'a', 'ä': 'a',
        'î': 'i', 'ï': 'i',
        'ô': 'o', 'ö': 'o',
        'ù': 'u', 'û': 'u', 'ü': 'u',
        'ç': 'c', 'œ': 'oe', 'æ': 'ae',
    }
    for src, dst in replacements.items():
        text = text.replace(src, dst)
    text = re.sub(r'[^a-z0-9\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text).strip('-')
    return text[:80]


def generer_slugs(apps, schema_editor):
    Article = apps.get_model('medias', 'Article')
    seen = set()
    for article in Article.objects.all():
        base = _slugify_fr(article.titre) if article.titre else f'article-{article.pk}'
        if not base:
            base = f'article-{article.pk}'
        slug = base
        n = 1
        while slug in seen:
            slug = f'{base}-{n}'
            n += 1
        seen.add(slug)
        article.slug = slug
        article.save(update_fields=['slug'])


class Migration(migrations.Migration):
    # Non-atomic pour permettre la création d'index entre les étapes
    atomic = False

    dependencies = [
        ('medias', '0002_photo_auteur'),
    ]

    operations = [
        # Étape 1 : ajouter comme CharField simple (sans _like index)
        migrations.AddField(
            model_name='article',
            name='slug',
            field=models.CharField(blank=True, max_length=100, default=''),
            preserve_default=False,
        ),
        # Étape 2 : générer les slugs pour les articles existants
        migrations.RunPython(generer_slugs, migrations.RunPython.noop),
        # Étape 3 : convertir en SlugField unique
        migrations.AlterField(
            model_name='article',
            name='slug',
            field=models.SlugField(
                blank=True,
                max_length=100,
                unique=True,
                help_text='URL SEO-friendly, générée automatiquement depuis le titre',
            ),
        ),
    ]
