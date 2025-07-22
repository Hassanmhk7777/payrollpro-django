"""
Générateur de bulletins de paie PDF simplifié avec ReportLab uniquement
Version améliorée avec intégration des absences
"""
from io import BytesIO
from django.http import HttpResponse
from datetime import datetime

try:
    from reportlab.pdfgen import canvas
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.colors import black, blue, red, green
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False


class BulletinPDFGenerator:
    """
    Générateur de bulletins de paie en PDF avec ReportLab
    """
    
    def __init__(self):
        self.company_name = "PayrollPro - Système de Paie"
        self.company_address = "Votre Adresse d'Entreprise"
        self.company_city = "Casablanca, Maroc"
        self.company_phone = "Tél: +212 5XX XX XX XX"
    
    def ajouter_section_absences(self, bulletin, story, styles):
        """
        Ajoute une section sur les absences dans le bulletin PDF
        Compatible avec votre structure SimpleDocTemplate
        """
        from .calculs import CalculateurPaie
        
        # Récupérer les informations d'absences
        calculateur = CalculateurPaie()
        absences_info = calculateur.calculer_absences(
            bulletin.employe, 
            bulletin.mois, 
            bulletin.annee
        )
        
        if absences_info['jours_deduits'] > 0:
            # Style pour la section absences
            section_style = ParagraphStyle(
                'AbsencesSectionStyle',
                parent=styles['Heading2'],
                fontSize=12,
                spaceBefore=15,
                spaceAfter=10,
                textColor=colors.darkorange
            )
            
            # Titre de la section
            story.append(Paragraph("ABSENCES ET DÉDUCTIONS", section_style))
            
            # Table des absences détaillées
            absences_data = [
                ['Type d\'absence', 'Du', 'Au', 'Jours', 'Motif']
            ]
            
            for detail in absences_info['absences_details']:
                motif_court = detail['motif'][:30] + "..." if len(detail['motif']) > 30 else detail['motif']
                absences_data.append([
                    detail['type'],
                    detail['debut'].strftime('%d/%m/%Y'),
                    detail['fin'].strftime('%d/%m/%Y'),
                    str(detail['jours']),
                    motif_court if motif_court else "—"
                ])
            
            # Ligne de total
            absences_data.append([
                'TOTAL JOURS DÉDUITS',
                '',
                '',
                str(absences_info['jours_deduits']),
                f"{absences_info['deduction_montant']:,.2f} DH"
            ])
            
            absences_table = Table(absences_data, colWidths=[4*cm, 2.5*cm, 2.5*cm, 1.5*cm, 3.5*cm])
            absences_table.setStyle(TableStyle([
                # En-tête
                ('BACKGROUND', (0, 0), (-1, 0), colors.orange),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                
                # Corps du tableau
                ('FONTNAME', (0, 1), (-1, -2), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -2), 9),
                ('ALIGN', (0, 1), (0, -2), 'LEFT'),  # Colonne type à gauche
                ('ALIGN', (4, 1), (4, -2), 'LEFT'),  # Colonne motif à gauche
                
                # Ligne de total
                ('BACKGROUND', (0, -1), (-1, -1), colors.lightyellow),
                ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, -1), (-1, -1), 10),
                
                # Bordures
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            
            story.append(absences_table)
            story.append(Spacer(1, 15))
            
            # Note explicative
            note_style = ParagraphStyle(
                'NoteStyle',
                parent=styles['Normal'],
                fontSize=9,
                textColor=colors.darkred,
                leftIndent=20
            )
            story.append(Paragraph(
                f"<b>Note :</b> Les absences sans solde sont déduites sur la base de {absences_info['salaire_journalier']:,.2f} DH par jour ouvrable.",
                note_style
            ))
            story.append(Spacer(1, 10))
    
    def generer_pdf_simple(self, bulletin):
        """
        Génère un PDF simple avec ReportLab - VERSION AMÉLIORÉE AVEC ABSENCES
        """
        if not REPORTLAB_AVAILABLE:
            return None
            
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=A4)
        styles = getSampleStyleSheet()
        story = []
        
        # Style personnalisé pour le titre
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=16,
            spaceAfter=20,
            textColor=colors.blue,
            alignment=1  # Centré
        )
        
        # Style pour les sections
        section_style = ParagraphStyle(
            'SectionStyle',
            parent=styles['Heading2'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=10,
            textColor=colors.darkblue
        )
        
        # En-tête du document
        story.append(Paragraph(self.company_name, title_style))
        story.append(Paragraph("BULLETIN DE PAIE", title_style))
        story.append(Paragraph(f"Période: {bulletin.periode_formatted()}", styles['Normal']))
        story.append(Paragraph(f"Date d'édition: {datetime.now().strftime('%d/%m/%Y')}", styles['Normal']))
        story.append(Spacer(1, 20))
        
        # Informations employé
        story.append(Paragraph("INFORMATIONS EMPLOYÉ", section_style))
        
        emp_data = [
            ['Nom et Prénom:', bulletin.employe.nom_complet()],
            ['Matricule:', bulletin.employe.matricule],
            ['Fonction:', bulletin.employe.fonction],
            ['Date d\'embauche:', bulletin.employe.date_embauche.strftime('%d/%m/%Y')],
            ['CIN:', bulletin.employe.cin],
            ['Situation familiale:', bulletin.employe.get_situation_familiale_display()],
            ['Enfants à charge:', str(bulletin.employe.nombre_enfants)]
        ]
        
        emp_table = Table(emp_data, colWidths=[4*cm, 8*cm])
        emp_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (0, -1), colors.lightblue),
            ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
            ('FONTNAME', (1, 0), (1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(emp_table)
        story.append(Spacer(1, 20))
        
        # **NOUVEAU : Section des absences si présentes**
        self.ajouter_section_absences(bulletin, story, styles)
        
        # Tableau des gains
        story.append(Paragraph("ÉLÉMENTS DE GAIN", section_style))
        
        gains_data = [
            ['Désignation', 'Base', 'Montant (DH)'],
            ['Salaire de base', f'{bulletin.heures_travaillees} heures', f'{bulletin.salaire_base:,.2f}'],
        ]
        
        if bulletin.total_primes > 0:
            gains_data.append(['Primes diverses', '-', f'{bulletin.total_primes:,.2f}'])
        
        if bulletin.heures_supplementaires > 0:
            gains_data.append(['Heures supplémentaires', '-', f'{bulletin.heures_supplementaires:,.2f}'])
        
        # **NOUVEAU : Afficher la déduction d'absences**
        from .calculs import CalculateurPaie
        calculateur = CalculateurPaie()
        absences_info = calculateur.calculer_absences(bulletin.employe, bulletin.mois, bulletin.annee)
        
        if absences_info['deduction_montant'] > 0:
            gains_data.append(['Déduction absences sans solde', f'{absences_info["jours_deduits"]} jour(s)', f'-{absences_info["deduction_montant"]:,.2f}'])
            
        gains_data.append(['TOTAL BRUT IMPOSABLE', '', f'{bulletin.salaire_brut_imposable:,.2f}'])
        
        gains_table = Table(gains_data, colWidths=[6*cm, 4*cm, 4*cm])
        gains_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.green),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightgreen),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            
            # **NOUVEAU : Style spécial pour la ligne de déduction**
            ('TEXTCOLOR', (2, -2), (2, -2), colors.red),  # Montant en rouge si c'est une déduction
        ]))
        story.append(gains_table)
        story.append(Spacer(1, 15))
        
        # Tableau des retenues
        story.append(Paragraph("RETENUES ET COTISATIONS", section_style))
        
        retenues_data = [
            ['Désignation', 'Base', 'Taux', 'Montant (DH)'],
            ['CNSS (Salarié)', f'{min(bulletin.salaire_brut_imposable, 6000):,.2f}', '4.48%', f'{bulletin.cotisation_cnss:,.2f}'],
            ['AMO (Salarié)', f'{bulletin.salaire_brut_imposable:,.2f}', '2.26%', f'{bulletin.cotisation_amo:,.2f}'],
            ['CIMR', f'{bulletin.salaire_brut_imposable:,.2f}', '6.00%', f'{bulletin.cotisation_cimr:,.2f}'],
            ['Impôt sur le Revenu', 'Base imposable', 'Barème', f'{bulletin.impot_revenu:,.2f}'],
        ]
        
        if bulletin.total_retenues > 0:
            retenues_data.append(['Autres retenues', '-', '-', f'{bulletin.total_retenues:,.2f}'])
        
        if bulletin.total_avances > 0:
            retenues_data.append(['Avances sur salaire', '-', '-', f'{bulletin.total_avances:,.2f}'])
        
        total_retenues = (bulletin.cotisation_cnss + bulletin.cotisation_amo + 
                         bulletin.cotisation_cimr + bulletin.impot_revenu + 
                         bulletin.total_retenues + bulletin.total_avances)
        
        retenues_data.append(['TOTAL RETENUES', '', '', f'{total_retenues:,.2f}'])
        
        retenues_table = Table(retenues_data, colWidths=[5*cm, 3*cm, 2*cm, 4*cm])
        retenues_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.red),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, -1), (-1, -1), colors.lightcoral),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        story.append(retenues_table)
        story.append(Spacer(1, 20))
        
        # NET À PAYER (encadré)
        net_style = ParagraphStyle(
            'NetStyle',
            parent=styles['Heading1'],
            fontSize=16,
            textColor=colors.darkgreen,
            alignment=1,
            spaceBefore=20,
            spaceAfter=20
        )
        story.append(Paragraph(f"<b>NET À PAYER : {bulletin.net_a_payer:,.2f} DH</b>", net_style))
        
        # Récapitulatif final
        story.append(Spacer(1, 15))
        story.append(Paragraph("RÉCAPITULATIF", section_style))
        
        recap_data = [
            ['Salaire Brut Imposable', f'{bulletin.salaire_brut_imposable:,.2f} DH'],
            ['Total Cotisations Sociales', f'{bulletin.cotisation_cnss + bulletin.cotisation_amo + bulletin.cotisation_cimr:,.2f} DH'],
            ['Impôt sur le Revenu', f'{bulletin.impot_revenu:,.2f} DH'],
        ]
        
        # **NOUVEAU : Ajouter les déductions d'absences dans le récapitulatif**
        if absences_info['deduction_montant'] > 0:
            recap_data.append(['Déductions Absences', f'{absences_info["deduction_montant"]:,.2f} DH'])
        
        recap_data.append(['NET À PAYER', f'{bulletin.net_a_payer:,.2f} DH'])
        
        recap_table = Table(recap_data, colWidths=[8*cm, 4*cm])
        recap_table.setStyle(TableStyle([
            ('BACKGROUND', (0, -1), (-1, -1), colors.darkgreen),
            ('TEXTCOLOR', (0, -1), (-1, -1), colors.white),
            ('FONTNAME', (0, -1), (-1, -1), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ]))
        story.append(recap_table)
        
        # Pied de page
        story.append(Spacer(1, 30))
        footer_style = ParagraphStyle(
            'FooterStyle',
            parent=styles['Normal'],
            fontSize=8,
            textColor=colors.grey,
            alignment=1
        )
        story.append(Paragraph("Ce bulletin de paie est conforme à la législation marocaine en vigueur.", footer_style))
        story.append(Paragraph(f"Généré automatiquement le {datetime.now().strftime('%d/%m/%Y à %H:%M')} par PayrollPro", footer_style))
        story.append(Paragraph("Document confidentiel - À conserver précieusement", footer_style))
        
        doc.build(story)
        buffer.seek(0)
        return buffer
    
    def generer_pdf(self, bulletin):
        """
        Point d'entrée principal pour générer un PDF
        """
        return self.generer_pdf_simple(bulletin)
    
    def reponse_http_pdf(self, bulletin):
        """
        Retourne une réponse HTTP avec le PDF
        """
        pdf_file = self.generer_pdf(bulletin)
        
        if not pdf_file:
            return None
        
        response = HttpResponse(pdf_file.read(), content_type='application/pdf')
        filename = f"bulletin_paie_{bulletin.employe.matricule}_{bulletin.mois:02d}_{bulletin.annee}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response