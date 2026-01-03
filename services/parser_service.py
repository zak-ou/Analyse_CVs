import re
import os
import nltk

# Ensure NLTK data is available BEFORE importing pyresparser
# pyresparser tries to load stopwords immediately on import
try:
    nltk.data.find('tokenizers/punkt')
    nltk.data.find('corpora/stopwords')
except LookupError:
    print("Downloading required NLTK data...")
    nltk.download('punkt')
    nltk.download('stopwords')
    nltk.download('averaged_perceptron_tagger')
    nltk.download('universal_tagset')

# from pyresparser import ResumeParser
# Pyresparser disabled due to Spacy compatibility issues

class ParserService:
    _nlp_cache = None

    def __init__(self):
        self.email_regex = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        self.phone_regex = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        # Load Spacy Model directly for custom extraction
        if ParserService._nlp_cache is None:
            try:
                import spacy
                if not spacy.util.is_package("en_core_web_sm"):
                    print("Downloading spacy model...")
                    os.system("python -m spacy download en_core_web_sm")
                ParserService._nlp_cache = spacy.load("en_core_web_sm")
                print("Spacy 'en_core_web_sm' loaded successfully.")
            except Exception as e:
                print(f"Warning: Could not load Spacy model: {e}")
                ParserService._nlp_cache = None
        
        self.nlp = ParserService._nlp_cache

    def parse_resume(self, file_path):
        """
        Legacy wrapper. Now mostly returns empty to defer to text-based extraction
        or tries pyresparser but fails gracefully.
        """
        try:
            # Try pyresparser but don't panic if it fails
            # data = ResumeParser(file_path).get_extracted_data()
            # if data: return data
            pass
        except:
            pass
        return {} # Fallback to empty dict

    def extract_from_text(self, text):
        """
        Extracts structured info from raw text using Regex and Spacy NER.
        """
        data = {
            'email': self._extract_email(text),
            'mobile_number': self._extract_phone(text),
            'text': text,
            'name': self._extract_name_spacy(text) # New Spacy Name Extraction
        }
        return data

    def _extract_name_spacy(self, text):
        if not self.nlp:
            return None
        
        doc = self.nlp(text[:500]) # Analyze first 500 chars for name
        for ent in doc.ents:
            if ent.label_ == "PERSON":
                return ent.text
        return None

    def extract_skills_from_text(self, text, candidate_skills_list=None):
        """
        Scans the raw text for specific skills.
        Useful to verify if required skills are present even if not detected by NLP.
        """
        found_skills = []
        if not text or not candidate_skills_list:
            return found_skills
            
        text_lower = text.lower()
        for skill in candidate_skills_list:
            # Simple keyword matching, ensuring word boundaries
            # Escape skill for regex special chars
            skill_escaped = re.escape(skill.lower())
            # \b matches word boundary
            if re.search(r'\b' + skill_escaped + r'\b', text_lower):
                found_skills.append(skill)
        
        return found_skills

    def _extract_email(self, text):
        match = re.search(self.email_regex, text)
        return match.group(0) if match else None

    def _extract_phone(self, text):
        # Basic regex for phone, can be improved
        match = re.search(self.phone_regex, text)
        return match.group(0) if match else None
