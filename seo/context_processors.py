from .models import SEOPage


def seo(request):
    """
    Injecte les données SEO de la page courante dans le contexte.
    La page est identifiée via request.resolver_match.url_name.
    """
    seo_data = None
    try:
        url_name = request.resolver_match.url_name if request.resolver_match else None
        if url_name:
            seo_data = SEOPage.objects.filter(page_id=url_name).first()
    except Exception:
        pass
    return {'seo_page': seo_data}
