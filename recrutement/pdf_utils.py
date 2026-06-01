"""
Génération du PDF d'inscription CFLD — Design amélioré.
"""
import os
import io
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils import timezone
from PIL import Image as PILImage

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    BaseDocTemplate, PageTemplate, Frame,
    Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, KeepTogether,
)
from reportlab.platypus.flowables import Flowable

# ── Palette CFLD ──────────────────────────────────────────────
C_VERT       = colors.HexColor('#0D7A45')   # vert principal
C_VERT_DARK  = colors.HexColor('#0B2218')   # vert très foncé (header)
C_VERT_LIGHT = colors.HexColor('#E8F7EF')   # vert très clair (fond section M)
C_ROSE       = colors.HexColor('#C8102E')   # rouge/rose section F
C_ROSE_LIGHT = colors.HexColor('#FFF0F3')   # fond section F
C_GOLD       = colors.HexColor('#D4A843')   # doré accent
C_GRIS       = colors.HexColor('#6B7280')
C_GRIS_CLAIR = colors.HexColor('#F5F5F5')
C_GRIS_LINE  = colors.HexColor('#E5E7EB')
C_NOIR       = colors.HexColor('#111111')
C_BLANC      = colors.white

W, H = A4
MARGIN_L = 1.8 * cm
MARGIN_R = 1.8 * cm
MARGIN_T = 4.2 * cm   # espace pour le header dessiné sur canvas
MARGIN_B = 2.0 * cm
CONTENT_W = W - MARGIN_L - MARGIN_R


# ── Flowable : ligne de séparation colorée ────────────────────
class ColorLine(Flowable):
    def __init__(self, width, color, thickness=0.5, space_before=4, space_after=4):
        super().__init__()
        self.width = width
        self.color = color
        self.thickness = thickness
        self.space_before = space_before
        self.space_after = space_after
        self.height = space_before + thickness + space_after

    def draw(self):
        self.canv.setStrokeColor(self.color)
        self.canv.setLineWidth(self.thickness)
        self.canv.line(0, self.space_after, self.width, self.space_after)


# ── Callbacks canvas ──────────────────────────────────────────
def _draw_header(canvas, doc, candidature, logo_path, section_color):
    """Dessine le bandeau d'en-tête sur le canvas directement."""
    canvas.saveState()
    HEADER_H = 3.2 * cm

    # ── Bande principale verte foncée ─────────────────────────
    canvas.setFillColor(C_VERT_DARK)
    canvas.rect(0, H - HEADER_H, W, HEADER_H, stroke=0, fill=1)

    # ── Accent coloré sur le bord gauche ─────────────────────
    canvas.setFillColor(section_color)
    canvas.rect(0, H - HEADER_H, 0.35 * cm, HEADER_H, stroke=0, fill=1)

    # ── Logo ─────────────────────────────────────────────────
    logo_x = 0.7 * cm
    logo_size = 2.2 * cm
    logo_y = H - HEADER_H + (HEADER_H - logo_size) / 2
    if os.path.exists(logo_path):
        try:
            canvas.drawImage(logo_path, logo_x, logo_y,
                             width=logo_size, height=logo_size,
                             preserveAspectRatio=True, mask='auto')
        except Exception:
            pass

    # ── Titre principal ───────────────────────────────────────
    title_x = logo_x + logo_size + 0.5 * cm
    canvas.setFillColor(C_BLANC)
    canvas.setFont('Helvetica-Bold', 18)
    canvas.drawString(title_x, H - 1.25 * cm, 'DOSSIER D\'INSCRIPTION')

    canvas.setFillColor(colors.HexColor('#A8D5BB'))
    canvas.setFont('Helvetica', 8.5)
    canvas.drawString(title_x, H - 1.9 * cm, 'Centre de Formation Lancine Diomandé  ·  CFLD  ·  Aboisso, Côte d\'Ivoire')
    canvas.drawString(title_x, H - 2.45 * cm, 'Saison 2026 — 2027')

    # ── Boîte référence (droite) ──────────────────────────────
    ref_w = 4.6 * cm
    ref_x = W - ref_w - 0.6 * cm
    ref_y = H - 1.05 * cm
    ref_h = 0.7 * cm
    # fond référence
    canvas.setFillColor(section_color)
    canvas.roundRect(ref_x, ref_y - ref_h, ref_w, ref_h, 3, stroke=0, fill=1)
    canvas.setFillColor(C_BLANC)
    canvas.setFont('Helvetica-Bold', 9)
    ref_text = candidature.reference
    ref_text_w = canvas.stringWidth(ref_text, 'Helvetica-Bold', 9)
    canvas.drawString(ref_x + (ref_w - ref_text_w) / 2, ref_y - ref_h + 0.18 * cm, ref_text)

    # section label
    sec_y = ref_y - ref_h - 0.1 * cm - 0.65 * cm
    sec_label = candidature.section
    canvas.setFillColor(colors.HexColor('#C8E6D7') if section_color == C_VERT else colors.HexColor('#FFCCD5'))
    canvas.roundRect(ref_x, sec_y, ref_w, 0.65 * cm, 3, stroke=0, fill=1)
    canvas.setFillColor(C_VERT_DARK if section_color == C_VERT else C_ROSE)
    canvas.setFont('Helvetica-Bold', 8.5)
    sec_text_w = canvas.stringWidth(sec_label, 'Helvetica-Bold', 8.5)
    canvas.drawString(ref_x + (ref_w - sec_text_w) / 2,
                      sec_y + 0.18 * cm, sec_label)

    # ── Ligne fine sous le header ─────────────────────────────
    canvas.setStrokeColor(section_color)
    canvas.setLineWidth(1.5)
    canvas.line(0, H - HEADER_H - 0.5, W, H - HEADER_H - 0.5)

    canvas.restoreState()


def _draw_footer(canvas, doc, candidature):
    """Dessine le pied de page sur le canvas."""
    canvas.saveState()
    y = MARGIN_B - 0.4 * cm

    # Ligne séparatrice
    canvas.setStrokeColor(C_GRIS_LINE)
    canvas.setLineWidth(0.5)
    canvas.line(MARGIN_L, y + 0.9 * cm, W - MARGIN_R, y + 0.9 * cm)

    date_soumission = candidature.date_soumission
    if timezone.is_aware(date_soumission):
        date_soumission = timezone.localtime(date_soumission)
    date_str = date_soumission.strftime('%d/%m/%Y à %H:%M')

    canvas.setFont('Helvetica', 7)
    canvas.setFillColor(C_GRIS)
    canvas.drawString(MARGIN_L, y + 0.45 * cm, f'Soumis le {date_str}')

    centre = 'CFLD  ·  Aboisso, Côte d\'Ivoire  ·  www.cfld-academie.com'
    cw = canvas.stringWidth(centre, 'Helvetica', 7)
    canvas.drawString((W - cw) / 2, y + 0.45 * cm, centre)

    canvas.setFont('Helvetica-Bold', 7)
    ref = f'Réf. {candidature.reference}'
    rw = canvas.stringWidth(ref, 'Helvetica-Bold', 7)
    canvas.drawString(W - MARGIN_R - rw, y + 0.45 * cm, ref)

    # Numéro de page
    canvas.setFont('Helvetica', 6.5)
    canvas.setFillColor(C_GRIS_LINE)
    canvas.drawRightString(W - MARGIN_R, y, f'Page {doc.page}')

    canvas.restoreState()


# ── Styles ────────────────────────────────────────────────────
def _styles(accent_color):
    lbl = ParagraphStyle('lbl', fontSize=7.5, textColor=C_GRIS,
                         fontName='Helvetica', leading=10)
    val = ParagraphStyle('val', fontSize=10, textColor=C_NOIR,
                         fontName='Helvetica-Bold', leading=13)
    sec = ParagraphStyle('sec', fontSize=7.5, textColor=accent_color,
                         fontName='Helvetica-Bold', leading=10,
                         spaceBefore=2, spaceAfter=2)
    note = ParagraphStyle('note', fontSize=7.5, textColor=C_GRIS,
                          fontName='Helvetica', leading=10, alignment=TA_CENTER)
    return lbl, val, sec, note


def _section_title(text, accent_color):
    """Retourne un bloc titre de section avec barre colorée à gauche."""
    style = ParagraphStyle('st', fontSize=7.5, textColor=accent_color,
                           fontName='Helvetica-Bold', leading=10,
                           leftIndent=7)
    data = [[Paragraph(text.upper(), style)]]
    t = Table(data, colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LINEBEFORE', (0, 0), (0, -1), 3, accent_color),
        ('BACKGROUND', (0, 0), (-1, -1), C_GRIS_CLAIR),
    ]))
    return t


def _fields_grid(pairs, lbl_style, val_style, bg=None):
    """
    Grille de champs en 4 colonnes : label | valeur | label | valeur.
    Chaque pair est (label, valeur).
    """
    LABEL_W = 3.0 * cm
    VALUE_W = (CONTENT_W / 2) - LABEL_W
    col_widths = [LABEL_W, VALUE_W, LABEL_W, VALUE_W]

    rows = []
    for i in range(0, len(pairs), 2):
        l1, v1 = pairs[i]
        l2, v2 = pairs[i + 1] if i + 1 < len(pairs) else ('', '')
        rows.append([
            Paragraph(l1, lbl_style),
            Paragraph(str(v1) if v1 else '—', val_style),
            Paragraph(l2, lbl_style),
            Paragraph(str(v2) if v2 else '—', val_style),
        ])

    t = Table(rows, colWidths=col_widths, repeatRows=0)
    style = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, C_GRIS_LINE),
        # séparateur vertical milieu
        ('LINEBEFORE', (2, 0), (2, -1), 0.3, C_GRIS_LINE),
    ]
    if bg:
        style.append(('BACKGROUND', (0, 0), (-1, -1), bg))
    t.setStyle(TableStyle(style))
    return t


def _fields_single(pairs, lbl_style, val_style, bg=None):
    """
    Grille de champs en 2 colonnes : label | valeur (une par ligne).
    Utilisé quand il y a peu de champs.
    """
    LABEL_W = 3.5 * cm
    VALUE_W = CONTENT_W - LABEL_W
    rows = []
    for l, v in pairs:
        rows.append([
            Paragraph(l, lbl_style),
            Paragraph(str(v) if v else '—', val_style),
        ])
    t = Table(rows, colWidths=[LABEL_W, VALUE_W])
    style = [
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
        ('LEFTPADDING', (0, 0), (-1, -1), 4),
        ('RIGHTPADDING', (0, 0), (-1, -1), 4),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, C_GRIS_LINE),
    ]
    if bg:
        style.append(('BACKGROUND', (0, 0), (-1, -1), bg))
    t.setStyle(TableStyle(style))
    return t


def generer_pdf_inscription(candidature):
    """
    Génère le PDF d'inscription, le sauvegarde et met à jour
    candidature.pdf_inscription.
    """
    buffer = io.BytesIO()

    logo_path = os.path.join(settings.BASE_DIR, 'assets', 'images', 'club', 'logo.png')
    accent = C_ROSE if candidature.sexe == 'F' else C_VERT
    bg_light = C_ROSE_LIGHT if candidature.sexe == 'F' else C_VERT_LIGHT

    # ── Callbacks canvas ──────────────────────────────────────
    def on_page(canvas, doc):
        _draw_header(canvas, doc, candidature, logo_path, accent)
        _draw_footer(canvas, doc, candidature)

    # ── Document avec frame ───────────────────────────────────
    frame = Frame(MARGIN_L, MARGIN_B, CONTENT_W, H - MARGIN_T - MARGIN_B,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    template = PageTemplate(id='main', frames=[frame], onPage=on_page)
    doc = BaseDocTemplate(
        buffer,
        pagesize=A4,
        pageTemplates=[template],
        title=f'Inscription CFLD — {candidature.reference}',
        author='CFLD — Centre de Formation Lancine Diomandé',
    )

    lbl, val, sec, note = _styles(accent)
    story = []

    # ════════════════════════════════════════════════════════════
    # SECTION 1 — IDENTITÉ + PHOTO
    # ════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.2 * cm))
    story.append(_section_title('Identité du joueur', accent))
    story.append(Spacer(1, 0.15 * cm))

    # Photo joueur — compressée pour alléger le PDF
    photo_cell_content = Spacer(3.2 * cm, 4.2 * cm)
    if candidature.photo:
        photo_path = os.path.join(settings.MEDIA_ROOT, str(candidature.photo))
        if os.path.exists(photo_path):
            try:
                photo_buf = io.BytesIO()
                with PILImage.open(photo_path) as img:
                    # Convertir en RGB si nécessaire (RGBA, P…)
                    if img.mode not in ('RGB', 'L'):
                        img = img.convert('RGB')
                    # Redimensionner à max 300×400px (suffisant pour le PDF)
                    img.thumbnail((300, 400), PILImage.LANCZOS)
                    img.save(photo_buf, format='JPEG', quality=75, optimize=True)
                photo_buf.seek(0)
                photo_cell_content = Image(photo_buf, width=3.2 * cm, height=4.0 * cm)
            except Exception:
                pass

    photo_wrap = Table([[photo_cell_content]], colWidths=[3.4 * cm])
    photo_wrap.setStyle(TableStyle([
        ('BOX', (0, 0), (-1, -1), 0.75, C_GRIS_LINE),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('BACKGROUND', (0, 0), (-1, -1), C_GRIS_CLAIR),
    ]))

    # Tableau identité — 2 colonnes label/valeur sur 4 lignes
    FIELDS_W = CONTENT_W - 3.6 * cm
    id_lbl_w = 3.2 * cm
    id_val_w = (FIELDS_W - id_lbl_w) / 2

    id_data = [
        [Paragraph('Nom', lbl), Paragraph(candidature.nom.upper(), val),
         Paragraph('Prénom', lbl), Paragraph(candidature.prenom, val)],
        [Paragraph('Date de naissance', lbl),
         Paragraph(candidature.date_naissance.strftime('%d / %m / %Y') if candidature.date_naissance else '—', val),
         Paragraph('Âge', lbl),
         Paragraph(f'{candidature.age} ans', val)],
        [Paragraph('Sexe', lbl), Paragraph(candidature.get_sexe_display(), val),
         Paragraph('Catégorie', lbl), Paragraph(candidature.categorie, val)],
        [Paragraph('Nationalité', lbl), Paragraph(candidature.nationalite, val),
         Paragraph('Adresse', lbl), Paragraph(candidature.adresse or '—', val)],
    ]
    id_fields = Table(id_data, colWidths=[id_lbl_w, id_val_w, id_lbl_w, id_val_w])
    id_fields.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 5),
        ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('LINEBELOW', (0, 0), (-1, -2), 0.3, C_GRIS_LINE),
        ('LINEBEFORE', (2, 0), (2, -1), 0.3, C_GRIS_LINE),
        ('BACKGROUND', (0, 0), (-1, -1), bg_light),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [C_BLANC, bg_light]),
    ]))

    identity_table = Table(
        [[photo_wrap, id_fields]],
        colWidths=[3.6 * cm, FIELDS_W],
    )
    identity_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (1, 0), (1, 0), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 0),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(identity_table)

    # ════════════════════════════════════════════════════════════
    # SECTION 2 — PROFIL SPORTIF
    # ════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.35 * cm))
    story.append(_section_title('Profil sportif', accent))
    story.append(Spacer(1, 0.15 * cm))
    sport_pairs = [
        ('Poste', candidature.get_poste_display()),
        ('Pied fort', candidature.pied_fort),
        ('Numéro préféré', str(candidature.numero_prefere) if candidature.numero_prefere else '—'),
        ('Club précédent', candidature.ancien_club or 'Aucun'),
    ]
    story.append(_fields_grid(sport_pairs, lbl, val))

    # ════════════════════════════════════════════════════════════
    # SECTION 3 — COORDONNÉES
    # ════════════════════════════════════════════════════════════
    story.append(Spacer(1, 0.35 * cm))
    story.append(_section_title('Coordonnées du joueur', accent))
    story.append(Spacer(1, 0.15 * cm))
    coord_pairs = [
        ('Téléphone WhatsApp', candidature.telephone_whatsapp),
        ('Adresse email', candidature.email),
    ]
    story.append(_fields_grid(coord_pairs, lbl, val))

    # ════════════════════════════════════════════════════════════
    # SECTION 4 — PARENT / TUTEUR LÉGAL
    # ════════════════════════════════════════════════════════════
    if any([candidature.nom_parent, candidature.telephone_parent, candidature.email_parent]):
        story.append(Spacer(1, 0.35 * cm))
        story.append(_section_title('Parent / Tuteur légal', accent))
        story.append(Spacer(1, 0.15 * cm))
        parent_pairs = [
            ('Nom complet', candidature.nom_parent or '—'),
            ('Téléphone', candidature.telephone_parent or '—'),
            ('Email', candidature.email_parent or '—'),
        ]
        if len(parent_pairs) % 2 != 0:
            parent_pairs.append(('', ''))
        story.append(_fields_grid(parent_pairs, lbl, val, bg=bg_light))

    # ════════════════════════════════════════════════════════════
    # SECTION 5 — INFOS COMPLÉMENTAIRES
    # ════════════════════════════════════════════════════════════
    extras = []
    if candidature.info_scolaire:
        extras.append(('École / Établissement', candidature.info_scolaire))
    if candidature.contact_urgence:
        extras.append(('Contact d\'urgence', candidature.contact_urgence))
    if extras:
        story.append(Spacer(1, 0.35 * cm))
        story.append(_section_title('Informations complémentaires', accent))
        story.append(Spacer(1, 0.15 * cm))
        if len(extras) % 2 != 0:
            extras.append(('', ''))
        story.append(_fields_grid(extras, lbl, val))

    # ════════════════════════════════════════════════════════════
    # ENCADRÉ DE STATUT (si accepté)
    # ════════════════════════════════════════════════════════════
    if candidature.statut == 'accepted':
        story.append(Spacer(1, 0.5 * cm))
        status_text = Paragraph(
            f'✓  INSCRIPTION VALIDÉE — Section {candidature.section}',
            ParagraphStyle('ok', fontSize=10, textColor=C_BLANC,
                           fontName='Helvetica-Bold', alignment=TA_CENTER, leading=14)
        )
        status_box = Table([[status_text]], colWidths=[CONTENT_W])
        status_box.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), accent),
            ('TOPPADDING', (0, 0), (-1, -1), 10),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
            ('ROUNDEDCORNERS', [4, 4, 4, 4]),
        ]))
        story.append(status_box)

    # Build
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    filename = f'inscription_{candidature.reference}.pdf'
    candidature.pdf_inscription.save(filename, ContentFile(pdf_bytes), save=True)
    return candidature.pdf_inscription.name
