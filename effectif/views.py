from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Joueur


# ── Configuration des sections ────────────────────────────────
SECTIONS = [
    {'label': 'Section Masculine', 'sexe': 'M', 'categories': ['U10', 'U13', 'U15', 'U17+']},
    {'label': 'Section Féminine', 'sexe': 'F', 'categories': ['U12', 'U15']},
]

# ── Mapping slug → données équipe ─────────────────────────────
EQUIPES_CONFIG = {
    'u10-masculin': {
        'categorie': 'U10', 'sexe': 'M',
        'label': 'U10 Masculin',
        'titre_seo': 'U10 Masculin — Formation Football Jeunes | CFLD Aboisso',
        'description': 'Découvrez l\'équipe U10 Masculin du CFLD à Aboisso. Initiation au football, fondamentaux techniques, 2 séances par semaine pour les joueurs de 8 à 10 ans.',
        'presentation': 'La section U10 Masculin du CFLD accueille les jeunes joueurs de 8 à 10 ans dans un cadre bienveillant et structuré. Objectif : découvrir le ballon, développer la coordination, apprendre le plaisir du jeu. 2 séances par semaine encadrées par des éducateurs certifiés.',
        'objectif': 'Aimer le football avant de le maîtriser.',
        'seances': '2 séances / semaine',
        'tranche_age': '8 — 10 ans',
        'niveau': 'Initiation',
        'couleur': '#1ED97A',
        'url_name': 'equipe_u10_masculin',
    },
    'u13-masculin': {
        'categorie': 'U13', 'sexe': 'M',
        'label': 'U13 Masculin',
        'titre_seo': 'U13 Masculin — Pré-Formation Football | CFLD Aboisso',
        'description': 'L\'équipe U13 Masculin du CFLD à Aboisso. Technique intensive, premiers matchs officiels, initiation tactique pour les joueurs de 11 à 13 ans.',
        'presentation': 'La section U13 Masculin du CFLD marque l\'entrée dans la pré-formation. Les jeunes joueurs développent leur technique individuelle, participent à leurs premiers matchs officiels et découvrent les bases de la tactique collective. Encadrement par des éducateurs spécialisés.',
        'objectif': 'Technique et règles du jeu.',
        'seances': '3 séances / semaine',
        'tranche_age': '11 — 13 ans',
        'niveau': 'Pré-formation',
        'couleur': '#1ED97A',
        'url_name': 'equipe_u13_masculin',
    },
    'u15-masculin': {
        'categorie': 'U15', 'sexe': 'M',
        'label': 'U15 Masculin',
        'titre_seo': 'U15 Masculin — Formation Intensive Football | CFLD Aboisso',
        'description': 'Équipe U15 Masculin du CFLD : formation intensive, entraînements bi-quotidiens pour les internes, suivi scolaire, compétitions régionales et nationales.',
        'presentation': 'La section U15 Masculin représente le cœur de la formation au CFLD. Entraînements bi-quotidiens pour les joueurs en internat, suivi scolaire obligatoire, participation aux compétitions régionales et nationales. Formation d\'excellence sur et en dehors du terrain.',
        'objectif': 'Formation intensive — élite.',
        'seances': '5-6 séances / semaine (internat)',
        'tranche_age': '13 — 15 ans',
        'niveau': 'Élite',
        'couleur': '#1ED97A',
        'url_name': 'equipe_u15_masculin',
    },
    'u17-masculin': {
        'categorie': 'U17+', 'sexe': 'M',
        'label': 'U17+ Masculin',
        'titre_seo': 'U17+ Masculin — Pré-Pro Football | CFLD Aboisso',
        'description': 'Équipe U17+ Masculin du CFLD : intégration à l\'équipe première, préparation aux tests professionnels, réseau de clubs partenaires en Europe et en Afrique.',
        'presentation': 'La section U17+ Masculin est la vitrine du CFLD. Les joueurs intègrent l\'équipe première et se préparent aux tests professionnels. Le CFLD dispose d\'un réseau de clubs partenaires en Europe et en Afrique pour faciliter les transitions vers le football professionnel.',
        'objectif': 'Transition vers le football professionnel.',
        'seances': 'Programme professionnel',
        'tranche_age': '15 ans et plus',
        'niveau': 'Pré-professionnel',
        'couleur': '#1ED97A',
        'url_name': 'equipe_u17_masculin',
    },
    'u12-feminin': {
        'categorie': 'U12', 'sexe': 'F',
        'label': 'U12 Féminin',
        'titre_seo': 'U12 Féminin — Football Féminin Jeunes | CFLD Aboisso',
        'description': 'Section féminine U12 du CFLD à Aboisso. Éveil au football féminin, coordination, motricité, 2 séances par semaine dans un cadre bienveillant.',
        'presentation': 'La section U12 Féminin du CFLD accompagne les jeunes joueuses dans leur éveil au football. Développement de la coordination, de la motricité et des habiletés techniques dans un cadre bienveillant et stimulant. 2 séances par semaine encadrées par des éducatrices spécialisées.',
        'objectif': 'Éveil & technique féminine.',
        'seances': '2 séances / semaine',
        'tranche_age': '9 — 12 ans',
        'niveau': 'Initiation féminine',
        'couleur': '#C8102E',
        'url_name': 'equipe_u12_feminin',
    },
    'u15-feminin': {
        'categorie': 'U15', 'sexe': 'F',
        'label': 'U15 Féminin',
        'titre_seo': 'U15 Féminin — Formation Football Féminin | CFLD Aboisso',
        'description': 'Équipe U15 Féminin du CFLD : entraînements réguliers, championnats régionaux féminins, suivi scolaire et préparation physique adaptée.',
        'presentation': 'La section U15 Féminin du CFLD participe activement aux championnats régionaux féminins de Côte d\'Ivoire. Entraînements réguliers, préparation physique adaptée, suivi scolaire et accompagnement personnel. Une formation complète pour les jeunes talents féminins.',
        'objectif': 'Compétition & excellence féminine.',
        'seances': '3-4 séances / semaine',
        'tranche_age': '12 — 15 ans',
        'niveau': 'Formation féminine',
        'couleur': '#C8102E',
        'url_name': 'equipe_u15_feminin',
    },
}


def effectif(request):
    poste = request.GET.get('poste', 'all')
    sexe = request.GET.get('sexe', 'all')
    categorie = request.GET.get('categorie', 'all')

    joueurs_qs = Joueur.objects.filter(actif=True)

    if poste in ('GK', 'DEF', 'MIL', 'ATT'):
        joueurs_qs = joueurs_qs.filter(poste=poste)
    if sexe in ('M', 'F'):
        joueurs_qs = joueurs_qs.filter(sexe=sexe)
    if categorie in ('U10', 'U12', 'U13', 'U15', 'U17+'):
        joueurs_qs = joueurs_qs.filter(categorie=categorie)

    counts = {
        'all': Joueur.objects.filter(actif=True).count(),
        'GK':  Joueur.objects.filter(actif=True, poste='GK').count(),
        'DEF': Joueur.objects.filter(actif=True, poste='DEF').count(),
        'MIL': Joueur.objects.filter(actif=True, poste='MIL').count(),
        'ATT': Joueur.objects.filter(actif=True, poste='ATT').count(),
    }

    sections_data = []
    for section in SECTIONS:
        equipes = []
        for cat in section['categories']:
            slug = _make_slug(cat, section['sexe'])
            qs = Joueur.objects.filter(actif=True, sexe=section['sexe'], categorie=cat)
            equipes.append({
                'label': f"{cat} {section['label'].split()[-1]}",
                'categorie': cat,
                'sexe': section['sexe'],
                'slug': slug,
                'joueurs': qs,
                'count': qs.count(),
            })
        sections_data.append({
            'label': section['label'],
            'sexe': section['sexe'],
            'equipes': equipes,
            'total': sum(e['count'] for e in equipes),
        })

    return render(request, 'effectif/effectif.html', {
        'joueurs': joueurs_qs,
        'poste_actif': poste,
        'sexe_actif': sexe,
        'categorie_actif': categorie,
        'counts': counts,
        'sections_data': sections_data,
        'equipes_config': EQUIPES_CONFIG,
        'vue': request.GET.get('vue', 'sections'),
    })


def equipe_detail(request, equipe_slug):
    config = EQUIPES_CONFIG.get(equipe_slug)
    if not config:
        raise Http404('Équipe introuvable')

    joueurs = Joueur.objects.filter(
        actif=True,
        sexe=config['sexe'],
        categorie=config['categorie'],
    )

    # Articles liés à la catégorie ou à l'académie
    from medias.models import Article
    articles = Article.objects.filter(
        publie=True,
        categorie__in=['academie', 'joueur'],
    ).order_by('-date_publication')[:4]

    # Photos récentes
    from medias.models import Photo
    photos = Photo.objects.filter(afficher=True)[:8]

    # Autres équipes pour navigation
    autres_equipes = {k: v for k, v in EQUIPES_CONFIG.items() if k != equipe_slug}

    return render(request, 'effectif/equipe_detail.html', {
        'config': config,
        'equipe_slug': equipe_slug,
        'joueurs': joueurs,
        'articles': articles,
        'photos': photos,
        'autres_equipes': autres_equipes,
    })


def _make_slug(categorie, sexe):
    """Génère le slug URL à partir de la catégorie et du sexe."""
    cat = categorie.lower().replace('+', '')
    sexe_label = 'masculin' if sexe == 'M' else 'feminin'
    return f"{cat}-{sexe_label}"
