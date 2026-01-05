"""
Service de génération de CV au format PDF.
Génère un CV professionnel identique en style au document CVEcole.pdf.
"""

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor
import os

class CVGenerator:
    """Générateur de CV au format PDF professionnel."""
    
    def __init__(self):
        self.page_width, self.page_height = A4
        self.margin_left = 25 * mm
        self.margin_right = 25 * mm
        self.margin_top = 20 * mm
        self.margin_bottom = 20 * mm
        
        # Colors
        self.color_primary = HexColor('#2D3436')
        self.color_secondary = HexColor('#636E72')
        self.color_accent = HexColor('#0984E3')
        
        # Font sizes
        self.font_header = 14
        self.font_section = 11
        self.font_normal = 10
        self.font_small = 9
        
    def _draw_header(self, c, coordonnees):
        """Dessine l'en-tête du CV avec les coordonnées."""
        y = self.page_height - self.margin_top
        
        # Nom complet en majuscules et gras
        nom_complet = coordonnees.get('nom_complet', '').upper()
        c.setFont("Helvetica-Bold", self.font_header)
        c.setFillColor(self.color_primary)
        c.drawString(self.margin_left, y, nom_complet)
        y -= 18
        
        # Email | Téléphone | Ville, Région
        c.setFont("Helvetica", self.font_small)
        c.setFillColor(self.color_secondary)
        contact_line = f"{coordonnees.get('email', '')} | {coordonnees.get('telephone', '')} | {coordonnees.get('ville_region', '')}"
        c.drawString(self.margin_left, y, contact_line)
        y -= 20
        
        return y
    
    def _draw_section_title(self, c, y, title):
        """Dessine un titre de section en majuscules et gras."""
        c.setFont("Helvetica-Bold", self.font_section)
        c.setFillColor(self.color_primary)
        c.drawString(self.margin_left, y, title.upper())
        y -= 3
        
        # Ligne de séparation
        c.setStrokeColor(self.color_secondary)
        c.setLineWidth(0.5)
        c.line(self.margin_left, y, self.page_width - self.margin_right, y)
        y -= 12
        
        return y
    
    def _draw_text_block(self, c, y, text, font="Helvetica", size=10, color=None, indent=0):
        """Dessine un bloc de texte avec gestion du retour à la ligne."""
        if color is None:
            color = self.color_primary
        
        c.setFont(font, size)
        c.setFillColor(color)
        
        max_width = self.page_width - self.margin_left - self.margin_right - indent
        words = text.split(' ')
        line = ""
        
        for word in words:
            test_line = line + word + " "
            if c.stringWidth(test_line, font, size) < max_width:
                line = test_line
            else:
                if line:
                    c.drawString(self.margin_left + indent, y, line.strip())
                    y -= size + 3
                line = word + " "
        
        if line:
            c.drawString(self.margin_left + indent, y, line.strip())
            y -= size + 3
        
        return y
    
    def _draw_profil(self, c, y, profil_text):
        """Dessine la section PROFIL."""
        y = self._draw_section_title(c, y, "PROFIL")
        
        if profil_text:
            y = self._draw_text_block(c, y, profil_text, size=self.font_small, color=self.color_secondary)
        
        y -= 15
        return y
    
    def _draw_education(self, c, y, education_list):
        """Dessine la section EDUCATION."""
        y = self._draw_section_title(c, y, "EDUCATION")
        
        for edu in education_list:
            # Établissement - Diplôme (en gras)
            c.setFont("Helvetica-Bold", self.font_normal)
            c.setFillColor(self.color_primary)
            etablissement_line = f"{edu.get('etablissement', '')} – {edu.get('diplome', '')}"
            c.drawString(self.margin_left, y, etablissement_line)
            y -= 12
            
            # Période
            c.setFont("Helvetica", self.font_small)
            c.setFillColor(self.color_secondary)
            c.drawString(self.margin_left, y, edu.get('periode', ''))
            y -= 12
            
            # Détails (bullet points)
            if edu.get('details'):
                details_lines = edu['details'].split('\n')
                for detail in details_lines:
                    if detail.strip():
                        c.setFont("Helvetica", self.font_small)
                        c.setFillColor(self.color_secondary)
                        c.drawString(self.margin_left + 10, y, f"• {detail.strip()}")
                        y -= 11
            
            y -= 8
        
        y -= 7
        return y
    
    def _draw_experience(self, c, y, experience_list):
        """Dessine la section EXPERIENCES."""
        y = self._draw_section_title(c, y, "EXPERIENCES")
        
        for exp in experience_list:
            # Entreprise (en gras)
            c.setFont("Helvetica-Bold", self.font_normal)
            c.setFillColor(self.color_primary)
            c.drawString(self.margin_left, y, exp.get('entreprise', ''))
            y -= 12
            
            # Période
            c.setFont("Helvetica", self.font_small)
            c.setFillColor(self.color_secondary)
            c.drawString(self.margin_left, y, exp.get('periode', ''))
            y -= 12
            
            # Titre mission
            c.setFont("Helvetica-Bold", self.font_small)
            c.setFillColor(self.color_primary)
            c.drawString(self.margin_left, y, exp.get('titre_mission', ''))
            y -= 12
            
            # Réalisations (bullet points)
            if exp.get('realisations'):
                realisations_lines = exp['realisations'].split('\n')
                for real in realisations_lines:
                    if real.strip():
                        c.setFont("Helvetica", self.font_small)
                        c.setFillColor(self.color_secondary)
                        c.drawString(self.margin_left + 10, y, f"• {real.strip()}")
                        y -= 11
            
            y -= 8
        
        y -= 7
        return y
    
    def _draw_skills(self, c, y, skills_data):
        """Dessine la section SKILLS."""
        y = self._draw_section_title(c, y, "SKILLS")
        
        if skills_data:
            # Technical Skills
            c.setFont("Helvetica-Bold", self.font_normal)
            c.setFillColor(self.color_primary)
            c.drawString(self.margin_left, y, "Technical Skills")
            y -= 12
            
            c.setFont("Helvetica", self.font_small)
            c.setFillColor(self.color_secondary)
            
            if skills_data.get('languages'):
                c.drawString(self.margin_left + 10, y, f"• Languages: {skills_data['languages']}")
                y -= 11
            
            if skills_data.get('technologies'):
                c.drawString(self.margin_left + 10, y, f"• Technologies/Frameworks: {skills_data['technologies']}")
                y -= 11
            
            if skills_data.get('databases'):
                c.drawString(self.margin_left + 10, y, f"• Database Management: {skills_data['databases']}")
                y -= 11
            
            if skills_data.get('tools'):
                c.drawString(self.margin_left + 10, y, f"• Developer Tools: {skills_data['tools']}")
                y -= 11
            
            if skills_data.get('networking'):
                c.drawString(self.margin_left + 10, y, f"• Networking Fundamentals: {skills_data['networking']}")
                y -= 11
            
            y -= 5
            
            # Soft Skills
            if skills_data.get('soft_skills'):
                c.setFont("Helvetica-Bold", self.font_normal)
                c.setFillColor(self.color_primary)
                c.drawString(self.margin_left, y, "Soft Skills")
                y -= 12
                
                soft_skills_list = skills_data['soft_skills'].split(',')
                for skill in soft_skills_list:
                    if skill.strip():
                        c.setFont("Helvetica", self.font_small)
                        c.setFillColor(self.color_secondary)
                        c.drawString(self.margin_left + 10, y, f"• {skill.strip()}")
                        y -= 11
        
        y -= 10
        return y
    
    def _draw_langues(self, c, y, langues_list):
        """Dessine la section LANGUES."""
        y = self._draw_section_title(c, y, "LANGUES")
        
        for langue in langues_list:
            c.setFont("Helvetica", self.font_small)
            c.setFillColor(self.color_secondary)
            langue_line = f"{langue.get('langue', '')} – {langue.get('niveau', '')}"
            c.drawString(self.margin_left, y, langue_line)
            y -= 11
        
        y -= 10
        return y
    
    def generate_pdf(self, cv_data, output_path):
        """
        Génère le PDF du CV.
        
        Args:
            cv_data: Dict avec les clés: coordonnees, education, experience, skills, langues
            output_path: Chemin où sauvegarder le PDF
        
        Returns:
            True si succès, False sinon
        """
        try:
            # Créer le répertoire si nécessaire
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            c = canvas.Canvas(output_path, pagesize=A4)
            
            coordonnees = cv_data.get('coordonnees', {})
            profil = coordonnees.get('profil', '')
            education = cv_data.get('education', [])
            experience = cv_data.get('experience', [])
            skills = cv_data.get('skills', {})
            langues = cv_data.get('langues', [])
            
            # Dessiner chaque section
            y = self._draw_header(c, coordonnees)
            
            if profil:
                y = self._draw_profil(c, y, profil)
            
            if education:
                y = self._draw_education(c, y, education)
            
            if experience:
                y = self._draw_experience(c, y, experience)
            
            if skills:
                y = self._draw_skills(c, y, skills)
            
            if langues:
                y = self._draw_langues(c, y, langues)
            
            c.save()
            return True
            
        except Exception as e:
            print(f"Error generating PDF: {e}")
            return False


def generate_candidate_cv(candidat_id, candidat_nom):
    """
    Génère le CV d'un candidat à partir des données en BDD.
    
    Args:
        candidat_id: ID du candidat
        candidat_nom: Nom du candidat pour le nom du fichier
    
    Returns:
        Chemin du fichier PDF généré, ou None si erreur
    """
    import database as db
    
    # Récupérer les données
    cv_data_raw = db.get_complete_cv_data(candidat_id)
    
    # Convertir les données en format dict simple
    cv_data = {
        'coordonnees': dict(cv_data_raw['coordonnees']) if cv_data_raw['coordonnees'] else {},
        'education': [dict(e) for e in cv_data_raw['education']],
        'experience': [dict(e) for e in cv_data_raw['experience']],
        'skills': dict(cv_data_raw['skills']) if cv_data_raw['skills'] else {},
        'langues': [dict(l) for l in cv_data_raw['langues']]
    }
    
    # Vérifier qu'il y a des données
    if not cv_data['coordonnees']:
        return None
    
    # Générer le PDF
    generator = CVGenerator()
    
    # Créer le nom du fichier
    nom_fichier = f"CV_{candidat_nom.replace(' ', '_')}.pdf"
    output_dir = "data/generated_cvs"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, nom_fichier)
    
    success = generator.generate_pdf(cv_data, output_path)
    
    if success:
        return output_path
    else:
        return None
