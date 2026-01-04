import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        # Placeholder credentials - in prod, use env vars
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "recrutenset@gmail.com" 
        self.password = "ukij ojev tikg fddj" 

    def _send_email(self, receiver_email, subject, body):
        """Helper to send real email or simulate if credentials fail."""
        if not self.password or not self.sender_email:
            print("----------------------------------------------------------------")
            print(f"[SIMULATION EMAIL] To: {receiver_email} | Subject: {subject}")
            print(body)
            print("----------------------------------------------------------------")
            return True

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.sender_email, self.password)
            server.send_message(msg)
            server.quit()
            print(f"✅ Email envoyé avec succès à {receiver_email}")
            return True
        except Exception as e:
            print(f"❌ Erreur d'envoi d'email à {receiver_email}: {e}")
            # Fallback to simulation print just so we see what was supposed to happen
            print("----------------------------------------------------------------")
            print(f"[FALLBACK SIMULATION] To: {receiver_email} | Subject: {subject}")
            print(body)
            print("----------------------------------------------------------------")
            return False

    def send_acceptance_email(self, candidate_email, candidate_name, job_title):
        """Sends an acceptance email to the candidate."""
        subject = f"Félicitations ! Vous avez été sélectionné pour le poste : {job_title}"
        body = f"""
Bonjour {candidate_name},

Nous avons le plaisir de vous informer que votre candidature pour le poste de "{job_title}" a été retenue !

L'équipe de recrutement vous contactera prochainement pour la suite du processus.

Cordialement,
L'équipe Recrutement
        """
        return self._send_email(candidate_email, subject, body)

    def send_refusal_email(self, candidate_email, candidate_name, job_title):
        """Sends a refusal email to the candidate."""
        subject = f"Mise à jour concernant votre candidature : {job_title}"
        body = f"""
Bonjour {candidate_name},

Nous vous remercions de l'intérêt que vous avez porté à notre offre pour le poste de "{job_title}".

Malgré la qualité de votre profil, nous avons décidé de poursuivre avec d'autres candidats dont les compétences correspondent plus étroitement à nos besoins actuels.

Nous conserverons votre CV dans notre base de données pour d'éventuelles opportunités futures.

Nous vous souhaitons pleine réussite dans vos recherches.

Cordialement,
L'équipe Recrutement
        """
        return self._send_email(candidate_email, subject, body)

    def send_confirmation_email(self, candidate_email, candidate_name, job_title):
        """Sends a confirmation email when a candidate applies."""
        subject = f"Confirmation de candidature : {job_title}"
        body = f"""
Bonjour {candidate_name},

Nous vous confirmons avoir bien reçu votre candidature pour le poste de "{job_title}".
Votre profil va être analysé dès la clôture de l'offre.

Vous pouvez suivre l'état de votre candidature dans votre espace candidat.

Cordialement,
L'équipe Recrutement
        """
        return self._send_email(candidate_email, subject, body)

    def send_offer_closed_email_to_recruiter(self, recruiter_email, recruiter_name, job_title, stats):
        """Sends a notification to the recruiter when an offer expires with detailed stats."""
        subject = f"Clôture de votre offre : {job_title}"
        body = f"""
Bonjour {recruiter_name},

Le délai de candidature pour votre offre "{job_title}" est arrivé à son terme.

📊 Statistiques finales :
- Nombre total de candidatures : {stats['total']}
- Candidats sélectionnés : {stats['accepted']}
- Candidats refusés : {stats['refused']}
- Score moyen de l'offre : {stats['avg_score']:.1f}/100

Le système a procédé à l'analyse et à la sélection automatique des meilleurs profils. 
Vous pouvez consulter le rapport détaillé et télécharger le CSV dans votre tableau de bord des statistiques.

Cordialement,
L'équipe RecrutIQ
        """
        return self._send_email(recruiter_email, subject, body)
