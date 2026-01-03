# 📄 Documentation Technique Approfondie - RecrutIQ

## 1. Vision et Objectifs
**RecrutIQ** est une plateforme SaaS de recrutement intelligent. Elle vise à résoudre le problème du tri massif de CV en utilisant des technologies d'extraction de texte (OCR) et d'analyse sémantique (NLP). L'objectif est de fournir aux recruteurs un classement objectif des candidats basé sur l'adéquation réelle entre leurs compétences et les besoins du poste.

---

## 2. Architecture Système

L'application suit une architecture de type **MVC (Modèle-Vue-Contrôleur)** simplifiée et adaptée à Streamlit :

### A. Modèle (Données) : `database.py`
Le système utilise **SQLite** pour la persistance. Le schéma est conçu pour gérer plusieurs rôles (Candidats vs Recruteurs) :
- **Table `candidats`** : Nom, Prénom, Email (Unique), Mot de passe (Hachage SHA-256), Diplôme, Téléphone.
- **Table `recruteurs`** : Nom, Prénom, Email, Domaine d'expertise, Mot de passe.
- **Table `offres`** : Gère la durée de vie d'un poste (Titre, Description, Compétences requises, Date limite, Nombre de postes ouverts).
- **Table `postulations`** : Table de liaison contenant les résultats d'analyse (Score, JSON des compétences extraites, Statut final).

### B. Vue (Interface) : `ui/`
- **Authentification (`auth.py`)** : Système de login/inscription avec gestion de session.
- **Espace Candidat (`candidate_space.py`)** : Interface de dépôt de CV avec feedback visuel sur le statut.
- **Espace Recruteur (`recruiter_space.py`)** : Tableau de bord de management avec graphiques analytiques (Radar Chart, Bar Charts).

### C. Contrôleur (Logique) : `app_logic/` et `services/`
- **`controller.py`** : Orchestrateur central qui coordonne les services OCR, Parser et Scoring.
- **`automation.py`** : Moteur d'automatisation asynchrone.

---

## 3. Détails des Services Techniques

### 🧠 Le Moteur d'Analyse (Parsing & NLP)
Le processus d'analyse d'un CV suit trois étapes critiques :

1.  **Pipeline OCR Hybride (`OCRService`)** :
    *   **Phase 1 (Natif)** : Le système tente d'extraire le texte directement du PDF (Digital PDF). C'est rapide et précis à 100%.
    *   **Phase 2 (Fallback OCR)** : Si le PDF est un scan ou une image, le système utilise `pdf2image` (via Poppler) pour transformer les pages en images, puis `EasyOCR` pour lire le texte.
2.  **Extraction Sémantique (`ParserService`)** :
    *   Utilise des expressions régulières (Regex) pour les champs structurés (Email, Téléphone).
    *   Utilise **SpaCy** (modèle `en_core_web_sm`) pour extraire les noms propres et entités.
    *   Effectue un "Keyword Matching" intelligent basé sur une liste de compétences dynamiques.
3.  **Algorithme de Scoring (`ScoringService`)** :
    *   Le score est calculé par l'intersection des ensembles de compétences (Jaccard-like similarity).
    *   $\text{Score} = \left( \frac{\text{Compétences Trouvées}}{\text{Compétences Requises}} \right) \times 100$.

### ⚙️ Automatisation en Arrière-plan (Background Worker)
Le fichier `automation.py` implémente un **Worker Thread** (Multi-threading) :
- **Fréquence** : Vérifie l'état de la base de données toutes les 60 secondes.
- **Action** : 
    1. Identifie les offres dont la `date_limite` est dépassée.
    2. Analyse automatiquement les CV qui n'ont pas encore été traités.
    3. Classe les candidats.
    4. Attribue les statuts `Accepted` (pour les N meilleurs) et `Refused` pour les autres.
    5. Déclenche le service d'e-mails.

### 📧 Service de Notification (`EmailService`)
Utilise le protocole **SMTP** via Gmail pour envoyer des communications professionnelles :
- **Candidats** : Confirmation de réception, Notification d'acceptation, Lettre de refus polie.
- **Recruteurs** : Résumé statistique après clôture de l'offre (Score moyen, nombre de candidats).

---

## 4. Sécurité et Performance
*   **Hachage** : Les mots de passe ne sont jamais stockés en clair. Ils passent par `hashlib.sha256`.
*   **Caching** : Streamlit `@st.cache_resource` est utilisé pour charger les modèles lourds (EasyOCR, SpaCy) une seule fois en mémoire au démarrage.
*   **Mode Simulation** : Le service d'e-mail intègre un mode "Simulation" qui imprime les emails dans la console si les identifiants SMTP ne sont pas configurés, évitant ainsi de bloquer le workflow de test.

---

## 5. Guide de Maintenance
*   **Base de données** : Pour inspecter manuellement les données, vous pouvez utiliser `inspect_db.py`.
*   **Modèles IA** : Pour ajouter une langue (ex: Espagnol), modifiez la liste de langues dans `ocr_service.py`.
*   **Dépendances** : Assurez-vous que l'outil système `Poppler` est installé pour la conversion PDF vers Image.

---
*Fin de la documentation technique détaillée - RecrutIQ v1.0*
