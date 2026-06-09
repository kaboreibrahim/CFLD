"""
Génération des reçus PDF professionnels pour les paiements CFLD.
Utilise ReportLab. Les PDFs incluent : logo, infos bénéficiaire,
montants, échéancier, cachet de validation.
"""
import io
import os
from decimal import Decimal

from django.conf import settings
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image as RLImage, PageTemplate,
    Paragraph, Spacer, Table, TableStyle, HRFlowable,
)

from .services import calculer_echeances, generer_numero_recu

# ── Palette CFLD ──
C_RED       = colors.HexColor("#C8161D")
C_RED_DEEP  = colors.HexColor("#8A0D12")
C_DARK      = colors.HexColor("#130505")
C_INK       = colors.HexColor("#0B0B0B")
C_GRAY      = colors.HexColor("#6B7280")
C_GRAY_LIGHT= colors.HexColor("#F5F5F5")
C_BORDER    = colors.HexColor("#E5E7EB")
C_GREEN     = colors.HexColor("#059669")
C_AMBER     = colors.HexColor("#B45309")
C_WHITE     = colors.white

def _logo_path():
    return os.path.join(settings.BASE_DIR, "assets", "images", "club", "logo.png")

W, H = A4
ML = 1.8 * cm
MR = 1.8 * cm
MT = 3.5 * cm
MB = 2.0 * cm
CW = W - ML - MR  # content width


# ── Styles de texte ──
def _styles():
    return {
        "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=20,
                                textColor=C_WHITE, alignment=TA_LEFT, leading=24),
        "subtitle": ParagraphStyle("subtitle", fontName="Helvetica", fontSize=9,
                                   textColor=colors.HexColor("#FFBCBC"), alignment=TA_LEFT),
        "section": ParagraphStyle("section", fontName="Helvetica-Bold", fontSize=7.5,
                                  textColor=C_GRAY, spaceBefore=10, spaceAfter=4,
                                  letterSpacing=2, leading=10),
        "field_key": ParagraphStyle("field_key", fontName="Helvetica", fontSize=8.5,
                                    textColor=C_GRAY),
        "field_val": ParagraphStyle("field_val", fontName="Helvetica-Bold", fontSize=9.5,
                                    textColor=C_INK),
        "amount_big": ParagraphStyle("amount_big", fontName="Helvetica-Bold", fontSize=22,
                                     textColor=C_RED, alignment=TA_RIGHT),
        "note": ParagraphStyle("note", fontName="Helvetica", fontSize=8,
                               textColor=C_GRAY, alignment=TA_CENTER),
        "stamp": ParagraphStyle("stamp", fontName="Helvetica-Bold", fontSize=8.5,
                                textColor=C_GREEN, alignment=TA_CENTER),
    }


def _draw_header(canvas, doc, numero_recu, titre_doc):
    """Entête rouge avec logo, titre et numéro de reçu."""
    canvas.saveState()
    HEADER_H = 2.8 * cm
    canvas.setFillColor(C_DARK)
    canvas.rect(0, H - HEADER_H, W, HEADER_H, stroke=0, fill=1)
    canvas.setFillColor(C_RED)
    canvas.rect(0, H - HEADER_H, 0.4 * cm, HEADER_H, stroke=0, fill=1)

    # Logo
    logo_p = _logo_path()
    tx = 0.8 * cm
    if os.path.exists(logo_p):
        logo_size = 2.0 * cm
        logo_y = H - HEADER_H + (HEADER_H - logo_size) / 2
        try:
            canvas.drawImage(logo_p, tx, logo_y, width=logo_size, height=logo_size,
                             preserveAspectRatio=True, mask="auto")
            tx += logo_size + 0.5 * cm
        except Exception:
            pass

    # Titre
    canvas.setFillColor(C_WHITE)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawString(tx, H - 1.2 * cm, titre_doc.upper())
    canvas.setFillColor(colors.HexColor("#FFBCBC"))
    canvas.setFont("Helvetica", 8)
    canvas.drawString(tx, H - 1.85 * cm, "Centre de Formation Lancine Diomandé  ·  CFLD  ·  Aboisso, Côte d'Ivoire")

    # Numéro de reçu
    canvas.setFillColor(C_RED)
    rw, rh = 4.5 * cm, 0.7 * cm
    rx = W - rw - 0.6 * cm
    ry = H - 1.15 * cm
    canvas.roundRect(rx, ry - rh, rw, rh, 4, stroke=0, fill=1)
    canvas.setFillColor(C_WHITE)
    canvas.setFont("Helvetica-Bold", 8)
    num_w = canvas.stringWidth(numero_recu, "Helvetica-Bold", 8)
    canvas.drawString(rx + (rw - num_w) / 2, ry - rh + 0.2 * cm, numero_recu)

    canvas.restoreState()


def _draw_footer(canvas, doc):
    canvas.saveState()
    canvas.setFillColor(C_BORDER)
    canvas.rect(0, 0, W, 0.8 * cm, stroke=0, fill=1)
    canvas.setFillColor(C_GRAY)
    canvas.setFont("Helvetica", 7)
    canvas.drawCentredString(W / 2, 0.27 * cm,
        "Ce reçu est un document officiel du CFLD. Conservez-le pour vos archives.")
    canvas.restoreState()


def _kv_table(data, col_widths=None):
    """Tableau clé-valeur simple."""
    styles_map = _styles()
    rows = []
    for key, val in data:
        rows.append([
            Paragraph(key.upper(), styles_map["field_key"]),
            Paragraph(str(val), styles_map["field_val"]),
        ])
    if not col_widths:
        col_widths = [3.5 * cm, CW - 3.5 * cm]
    t = Table(rows, colWidths=col_widths, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("TOPPADDING",    (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 6),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def _echeancier_table(plan):
    """Tableau de l'échéancier (10 lignes)."""
    styles_map = _styles()
    STATUT_COLORS = {
        "solde":    (C_GREEN, "Soldé ✓"),
        "partiel":  (C_AMBER, "Partiel"),
        "non_paye": (C_GRAY,  "Non payé"),
    }
    rows = [["N°", "Libellé", "Attendu", "Payé", "Restant", "Statut"]]
    for e in plan["echeances"]:
        clr, lbl = STATUT_COLORS.get(e["statut"], (C_GRAY, e["statut"]))
        rows.append([
            str(e["num"]),
            e["label"],
            f"{int(e['montant_attendu']):,} F".replace(",", " "),
            f"{int(e['montant_paye']):,} F".replace(",", " "),
            f"{int(e['montant_restant']):,} F".replace(",", " "),
            Paragraph(f'<font color="{clr.hexval()}">{lbl}</font>', styles_map["field_val"]),
        ])
    cw = [0.8 * cm, 3.2 * cm, 2.8 * cm, 2.8 * cm, 2.8 * cm, 2.6 * cm]
    t = Table(rows, colWidths=cw, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND",   (0, 0), (-1, 0), C_DARK),
        ("TEXTCOLOR",    (0, 0), (-1, 0), C_WHITE),
        ("FONTNAME",     (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",     (0, 0), (-1, 0), 7.5),
        ("BOTTOMPADDING",(0, 0), (-1, 0), 6),
        ("TOPPADDING",   (0, 0), (-1, 0), 6),
        ("FONTSIZE",     (0, 1), (-1, -1), 8),
        ("FONTNAME",     (0, 1), (-1, -1), "Helvetica"),
        ("TOPPADDING",   (0, 1), (-1, -1), 4),
        ("BOTTOMPADDING",(0, 1), (-1, -1), 4),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [C_WHITE, C_GRAY_LIGHT]),
        ("GRID",         (0, 0), (-1, -1), 0.4, C_BORDER),
        ("VALIGN",       (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return t


def _progress_bar_flowable(pct, label=""):
    """Barre de progression simple via un tableau."""
    filled = max(0, min(int(pct), 100))
    empty = 100 - filled
    color = C_GREEN if filled == 100 else (C_AMBER if filled >= 50 else C_RED)
    row = []
    if filled > 0:
        row.append(("", filled / 100 * CW - 0.1 * cm, color))
    if empty > 0:
        row.append(("", empty / 100 * CW - 0.1 * cm, C_BORDER))

    parts = [[p[0] for p in row]]
    widths = [p[1] for p in row]
    if not widths:
        return Spacer(1, 0.3 * cm)
    t = Table(parts, colWidths=widths, rowHeights=[0.35 * cm])
    style_cmds = [
        ("TOPPADDING", (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i, p in enumerate(row):
        style_cmds.append(("BACKGROUND", (i, 0), (i, 0), p[2]))
    t.setStyle(TableStyle(style_cmds))
    return t


# ── REÇU D'INSCRIPTION ──────────────────────────────────────

def generer_recu_inscription(paiement):
    """
    Génère un reçu PDF pour un PaiementInscription.
    Inclut : infos candidat, montant payé, échéancier prévisionnel.
    Retourne un objet bytes (PDF).
    """
    buffer = io.BytesIO()
    numero = generer_numero_recu(paiement)
    s = _styles()

    def header(canvas, doc):
        _draw_header(canvas, doc, numero, "Reçu de paiement — Inscription")

    doc = BaseDocTemplate(
        buffer, pagesize=A4,
        leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
    )
    frame = Frame(ML, MB, CW, H - MT - MB, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=header)])

    story = []

    # ── INFORMATIONS CANDIDAT ──
    story.append(Paragraph("INFORMATIONS DU BÉNÉFICIAIRE", s["section"]))
    story.append(HRFlowable(width=CW, thickness=0.5, color=C_BORDER, spaceAfter=6))

    candidat = paiement.candidature
    kv = [
        ("Référence",   candidat.reference),
        ("Nom complet", candidat.nom_complet),
        ("Catégorie",   candidat.categorie),
        ("Nationalité", candidat.nationalite),
        ("Date de naissance", str(candidat.date_naissance)),
    ]
    story.append(_kv_table(kv))
    story.append(Spacer(1, 0.4 * cm))

    # ── DÉTAILS DU PAIEMENT ──
    story.append(Paragraph("DÉTAILS DU PAIEMENT", s["section"]))
    story.append(HRFlowable(width=CW, thickness=0.5, color=C_BORDER, spaceAfter=6))

    kv2 = [
        ("Date",           str(paiement.date_paiement)),
        ("Mode",           paiement.compte_paiement.get_mode_display() if paiement.compte_paiement else "—"),
        ("Numéro de dépôt", paiement.compte_paiement.numero if paiement.compte_paiement else "—"),
        ("Réf. transaction", paiement.reference_transaction or "—"),
        ("Statut",         paiement.get_statut_validation_display()),
    ]
    story.append(_kv_table(kv2))
    story.append(Spacer(1, 0.3 * cm))

    # Montant en grand
    montant_str = f"{int(paiement.montant):,} FCFA".replace(",", " ")
    amount_data = [["Montant payé", montant_str]]
    at = Table(amount_data, colWidths=[CW * 0.5, CW * 0.5])
    at.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_GRAY_LIGHT),
        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (0, 0), 9),
        ("TEXTCOLOR", (0, 0), (0, 0), C_GRAY),
        ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (1, 0), (1, 0), 18),
        ("TEXTCOLOR", (1, 0), (1, 0), C_RED),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (0, 0), 12),
        ("RIGHTPADDING", (1, 0), (1, 0), 12),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    story.append(at)
    story.append(Spacer(1, 0.5 * cm))

    # ── ÉCHÉANCIER (si cotisation auto-créée) ──
    versement = getattr(paiement, 'versement_cotisation', None)
    if versement:
        cotisation = versement.cotisation
        plan = calculer_echeances(cotisation)
        story.append(Paragraph("ÉCHÉANCIER ANNUEL", s["section"]))
        story.append(HRFlowable(width=CW, thickness=0.5, color=C_BORDER, spaceAfter=6))

        # Progression
        pct = plan["progression_pct"]
        story.append(_progress_bar_flowable(pct))
        story.append(Spacer(1, 0.15 * cm))

        summary_data = [[
            f"Versé : {int(plan['total_verse']):,} F".replace(",", " "),
            f"Restant : {int(plan['total_restant']):,} F".replace(",", " "),
            f"Échéances soldées : {plan['nb_soldes']}/10",
        ]]
        summary_data[0][2] = f"Echeances soldees : {plan['nb_soldes']}/{plan['nb_echeances']}"
        st = Table(summary_data, colWidths=[CW / 3, CW / 3, CW / 3])
        st.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("TEXTCOLOR", (0, 0), (0, 0), C_GREEN),
            ("TEXTCOLOR", (1, 0), (1, 0), C_AMBER),
            ("TEXTCOLOR", (2, 0), (2, 0), C_INK),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(st)
        story.append(Spacer(1, 0.4 * cm))
        story.append(_echeancier_table(plan))
        story.append(Spacer(1, 0.4 * cm))

    # ── CACHET DE VALIDATION ──
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width=CW, thickness=0.5, color=C_BORDER, spaceAfter=8))
    stamp_data = [[
        Paragraph("✓  PAIEMENT VALIDÉ\nCFLD — Centre de Formation Lancine Diomandé", s["stamp"]),
        Paragraph(f"Reçu N° {numero}\nEmis le {paiement.date_paiement}", s["note"]),
    ]]
    stt = Table(stamp_data, colWidths=[CW * 0.55, CW * 0.45])
    stt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F0FDF4")),
        ("BACKGROUND", (1, 0), (1, 0), C_GRAY_LIGHT),
        ("BOX", (0, 0), (0, 0), 1, C_GREEN),
        ("BOX", (1, 0), (1, 0), 0.5, C_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    story.append(stt)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Ce document constitue la preuve officielle de votre paiement auprès du CFLD. "
        "Toute reproduction non autorisée est interdite.",
        s["note"],
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ── REÇU DE VERSEMENT ────────────────────────────────────────

def generer_recu_versement(versement):
    """
    Génère un reçu PDF pour un VersementCotisation.
    Inclut : infos joueur, montant versé, cumul, reste, échéancier.
    """
    buffer = io.BytesIO()
    numero = generer_numero_recu(versement)
    s = _styles()

    def header(canvas, doc):
        _draw_header(canvas, doc, numero, "Reçu de versement — Cotisation annuelle")

    doc = BaseDocTemplate(
        buffer, pagesize=A4,
        leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
    )
    frame = Frame(ML, MB, CW, H - MT - MB, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=header)])

    story = []
    cotisation = versement.cotisation
    joueur = cotisation.joueur
    plan = calculer_echeances(cotisation)

    # ── INFORMATIONS JOUEUR ──
    story.append(Paragraph("INFORMATIONS DU JOUEUR", s["section"]))
    story.append(HRFlowable(width=CW, thickness=0.5, color=C_BORDER, spaceAfter=6))

    kv = [
        ("Nom complet", joueur.nom_complet),
        ("Catégorie",   joueur.categorie),
        ("N° de maillot", str(joueur.numero)),
        ("Année de cotisation", str(cotisation.annee)),
    ]
    story.append(_kv_table(kv))
    story.append(Spacer(1, 0.4 * cm))

    # ── DÉTAILS DU VERSEMENT ──
    story.append(Paragraph("DÉTAILS DU VERSEMENT", s["section"]))
    story.append(HRFlowable(width=CW, thickness=0.5, color=C_BORDER, spaceAfter=6))

    kv2 = [
        ("Type",          versement.get_type_versement_display()),
        ("Date",          str(versement.date_versement)),
        ("Mode de dépôt", versement.compte_paiement.get_mode_display() if versement.compte_paiement else "—"),
        ("Numéro",        versement.compte_paiement.numero if versement.compte_paiement else "—"),
        ("Réf. transaction", versement.reference_transaction or "—"),
        ("Validé par",    str(versement.valide_par) if versement.valide_par else "Administration CFLD"),
    ]
    story.append(_kv_table(kv2))
    story.append(Spacer(1, 0.3 * cm))

    # Montant en grand
    montant_str = f"{int(versement.montant):,} FCFA".replace(",", " ")
    amount_data = [["Montant versé", montant_str]]
    at = Table(amount_data, colWidths=[CW * 0.5, CW * 0.5])
    at.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_GRAY_LIGHT),
        ("FONTNAME", (0, 0), (0, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (0, 0), 9),
        ("TEXTCOLOR", (0, 0), (0, 0), C_GRAY),
        ("FONTNAME", (1, 0), (1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (1, 0), (1, 0), 18),
        ("TEXTCOLOR", (1, 0), (1, 0), C_RED),
        ("ALIGN", (1, 0), (1, 0), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING", (0, 0), (0, 0), 12),
        ("RIGHTPADDING", (1, 0), (1, 0), 12),
    ]))
    story.append(at)
    story.append(Spacer(1, 0.5 * cm))

    # ── SOLDE CUMULATIF ──
    story.append(Paragraph("SOLDE CUMULATIF", s["section"]))
    story.append(HRFlowable(width=CW, thickness=0.5, color=C_BORDER, spaceAfter=6))

    pct = plan["progression_pct"]
    story.append(_progress_bar_flowable(pct))
    story.append(Spacer(1, 0.15 * cm))

    cumul_data = [
        ["Total versé",          f"{int(plan['total_verse']):,} FCFA".replace(",", " ")],
        ["Total attendu",         f"{int(plan['montant_total']):,} FCFA".replace(",", " ")],
        ["Restant à payer",       f"{int(plan['total_restant']):,} FCFA".replace(",", " ")],
        ["Échéances soldées",     f"{plan['nb_soldes']} / {plan['nb_echeances']}"],
        ["Avancement",           f"{pct} %"],
    ]
    ct = Table(cumul_data, colWidths=[3.5 * cm, CW - 3.5 * cm])
    ct.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (0, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 8.5),
        ("FONTNAME", (1, 0), (1, -1), "Helvetica-Bold"),
        ("TEXTCOLOR", (0, 0), (-1, -1), C_INK),
        ("TEXTCOLOR", (1, 2), (1, 2), C_AMBER if plan["total_restant"] > 0 else C_GREEN),
        ("TEXTCOLOR", (1, 0), (1, 0), C_GREEN),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("ROWBACKGROUNDS", (0, 0), (-1, -1), [C_WHITE, C_GRAY_LIGHT]),
    ]))
    story.append(ct)
    story.append(Spacer(1, 0.4 * cm))

    # ── ÉCHÉANCIER ──
    story.append(Paragraph("ÉCHÉANCIER DÉTAILLÉ", s["section"]))
    story.append(HRFlowable(width=CW, thickness=0.5, color=C_BORDER, spaceAfter=6))
    story.append(_echeancier_table(plan))
    story.append(Spacer(1, 0.5 * cm))

    # ── CACHET DE VALIDATION ──
    story.append(HRFlowable(width=CW, thickness=0.5, color=C_BORDER, spaceAfter=8))
    stamp_data = [[
        Paragraph("✓  VERSEMENT VALIDÉ\nCFLD — Centre de Formation Lancine Diomandé", s["stamp"]),
        Paragraph(f"Reçu N° {numero}\nEmis le {versement.date_versement}", s["note"]),
    ]]
    stt = Table(stamp_data, colWidths=[CW * 0.55, CW * 0.45])
    stt.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#F0FDF4")),
        ("BACKGROUND", (1, 0), (1, 0), C_GRAY_LIGHT),
        ("BOX", (0, 0), (0, 0), 1, C_GREEN),
        ("BOX", (1, 0), (1, 0), 0.5, C_BORDER),
        ("TOPPADDING", (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(stt)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Ce document constitue la preuve officielle de votre versement auprès du CFLD. "
        "Toute reproduction non autorisée est interdite.",
        s["note"],
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer


# ── REÇU VISITE MÉDICALE ────────────────────────────────────

def generer_recu_visite_medicale(paiement):
    """
    Génère un reçu PDF pour un PaiementVisiteMedicale validé.
    Inclut : infos candidat, montant payé, mode de dépôt, cachet de validation.
    """
    buffer = io.BytesIO()
    numero = generer_numero_recu(paiement)
    s = _styles()

    def header(canvas, doc):
        _draw_header(canvas, doc, numero, "Reçu de paiement — Visite médicale")

    doc = BaseDocTemplate(
        buffer, pagesize=A4,
        leftMargin=ML, rightMargin=MR, topMargin=MT, bottomMargin=MB,
    )
    frame = Frame(ML, MB, CW, H - MT - MB, id="normal")
    doc.addPageTemplates([PageTemplate(id="main", frames=[frame], onPage=header)])

    story = []
    candidature = paiement.candidature

    # ── INFORMATIONS CANDIDAT ──
    story.append(Paragraph("INFORMATIONS DU CANDIDAT", s["section"]))
    story.append(HRFlowable(width=CW, thickness=0.5, color=C_BORDER, spaceAfter=6))
    kv = [
        ("Référence",       candidature.reference),
        ("Nom complet",     candidature.nom_complet),
        ("Catégorie",       candidature.categorie),
        ("Nationalité",     candidature.nationalite),
        ("Date naissance",  str(candidature.date_naissance)),
    ]
    story.append(_kv_table(kv))
    story.append(Spacer(1, 0.4 * cm))

    # ── DÉTAILS DU PAIEMENT ──
    story.append(Paragraph("DÉTAILS DU PAIEMENT — VISITE MÉDICALE", s["section"]))
    story.append(HRFlowable(width=CW, thickness=0.5, color=C_BORDER, spaceAfter=6))
    kv2 = [
        ("Date",             str(paiement.date_paiement)),
        ("Mode de dépôt",    paiement.compte_paiement.get_mode_display() if paiement.compte_paiement else "—"),
        ("Numéro de dépôt",  paiement.compte_paiement.numero if paiement.compte_paiement else "—"),
        ("Réf. transaction", paiement.reference_transaction or "—"),
        ("Statut",           paiement.get_statut_validation_display()),
    ]
    story.append(_kv_table(kv2))
    story.append(Spacer(1, 0.3 * cm))

    # Montant en grand
    montant_str = f"{int(paiement.montant):,} FCFA".replace(",", " ")
    amount_data = [["Montant payé", montant_str]]
    at = Table(amount_data, colWidths=[CW * 0.5, CW * 0.5])
    at.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_GRAY_LIGHT),
        ("FONTNAME",   (0, 0), (0, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (0, 0), 9),
        ("TEXTCOLOR",  (0, 0), (0, 0), C_GRAY),
        ("FONTNAME",   (1, 0), (1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (1, 0), (1, 0), 18),
        ("TEXTCOLOR",  (1, 0), (1, 0), C_RED),
        ("ALIGN",      (1, 0), (1, 0), "RIGHT"),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",  (0, 0), (0, 0), 12),
        ("RIGHTPADDING", (1, 0), (1, 0), 12),
    ]))
    story.append(at)
    story.append(Spacer(1, 0.5 * cm))

    # ── NOTE INFORMATIVE ──
    info_data = [[
        Paragraph(
            "<b>Objet :</b> Ce reçu atteste du paiement des frais de visite médicale "            "obligatoire pour l'intégration au Centre de Formation Lancine Diomandé (CFLD). "            "Ce document doit être présenté lors de la convocation.",
            ParagraphStyle("info", fontName="Helvetica", fontSize=8.5, textColor=C_INK,
                           leading=13, leftIndent=0),
        )
    ]]
    info_t = Table(info_data, colWidths=[CW])
    info_t.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), colors.HexColor("#FEF3C7")),
        ("BOX",           (0, 0), (-1, -1), 0.5, colors.HexColor("#F59E0B")),
        ("TOPPADDING",    (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LEFTPADDING",   (0, 0), (-1, -1), 12),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 12),
        ("ROUNDEDCORNERS", [6, 6, 6, 6]),
    ]))
    story.append(info_t)
    story.append(Spacer(1, 0.5 * cm))

    # ── CACHET DE VALIDATION ──
    story.append(HRFlowable(width=CW, thickness=0.5, color=C_BORDER, spaceAfter=8))
    stamp_data = [[
        Paragraph("✓  VISITE MEDICALE PAYEE\nCFLD — Centre de Formation Lancine Diomande", s["stamp"]),
        Paragraph(f"Reçu N° {numero}\nEmis le {paiement.date_paiement}", s["note"]),
    ]]
    stt = Table(stamp_data, colWidths=[CW * 0.55, CW * 0.45])
    stt.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (0, 0), colors.HexColor("#F0FDF4")),
        ("BACKGROUND",    (1, 0), (1, 0), C_GRAY_LIGHT),
        ("BOX",           (0, 0), (0, 0), 1, C_GREEN),
        ("BOX",           (1, 0), (1, 0), 0.5, C_BORDER),
        ("TOPPADDING",    (0, 0), (-1, -1), 12),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(stt)
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "Ce document constitue la preuve officielle du paiement de votre visite medicale aupres du CFLD.",
        s["note"],
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer
