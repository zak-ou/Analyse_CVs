import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class EmailService:
    def __init__(self):
        # Placeholder credentials - in prod, use env vars
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587
        self.sender_email = "recrutement@example.com" 
        self.password = "your_password" 

    def send_acceptance_email(self, candidate_email, candidate_name, job_title):
        """
        Sends an acceptance email to the candidate.
        For protype, this will just simulate the sending by printing to console.
        """
        subject = f"Félicitations ! Vous avez été sélectionné pour le poste : {job_title}"
        
        body = f"""
        Bonjour {candidate_name},
        
        Nous avons le plaisir de vous informer que votre candidature pour le poste de "{job_title}" a été retenue !
        
        L'équipe de recrutement vous contactera prochainement pour la suite du processus.
        
        Cordialement,
        L'équipe Recrutement
        """
        
        print("----------------------------------------------------------------")
        print(f"[SIMULATION EMAIL] To: {candidate_email}")
        print(f"Subject: {subject}")
        print(body)
        print("----------------------------------------------------------------")
        
        # Real implementation would be:
        # try:
        #     msg = MIMEMultipart()
        #     msg['From'] = self.sender_email
        #     msg['To'] = candidate_email
        #     msg['Subject'] = subject
        #     msg.attach(MIMEText(body, 'plain'))
        #     
        #     server = smtplib.SMTP(self.smtp_server, self.smtp_port)
        #     server.starttls()
        #     server.login(self.sender_email, self.password)
        #     text = msg.as_string()
        #     server.sendmail(self.sender_email, candidate_email, text)
        #     server.quit()
        #     return True
        # except Exception as e:
        #     print(f"Failed to send email: {e}")
        #     return False

        return True
