import os
import shutil
from services.ocr_service import OCRService
from services.parser_service import ParserService
from services.scoring_service import ScoringService
from services.report_service import ReportService

class RecruitmentController:
    def __init__(self, upload_dir='data/uploads', report_dir='data/reports'):
        self.upload_dir = upload_dir
        self.report_dir = report_dir
        
        # Ensure directories exist
        os.makedirs(self.upload_dir, exist_ok=True)
        os.makedirs(self.report_dir, exist_ok=True)

        # Initialize Services
        self.ocr_service = OCRService()
        self.parser_service = ParserService()
        self.scoring_service = ScoringService()
        self.report_service = ReportService()

    def process_uploads(self, uploaded_files, required_skills):
        results = []
        
        for uploaded_file in uploaded_files:
            # 1. Save file locally
            file_path = os.path.join(self.upload_dir, uploaded_file.name)
            
            # CRITICAL FIX: Avoid overwriting if source is same as destination
            # This happens when processing files already on disk
            try:
                # Check if uploaded_file has a 'path' attribute (from our custom wrapper)
                if hasattr(uploaded_file, 'path') and os.path.abspath(uploaded_file.path) == os.path.abspath(file_path):
                    print(f"File already in place: {file_path}. Skipping save.")
                else:
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
            except Exception as e:
                 print(f"Warning during file save: {e}")
            
            
            print(f"Processing {uploaded_file.name}...")

            # 2. Extract Text (OCR) - Good for Scans
            ocr_text = self.ocr_service.extract_text(file_path)
            
            # 3. Parse Data
            # Attempt 1: Pyresparser on file (works for native PDFs)
            parsed_data = self.parser_service.parse_resume(file_path)
            
            # Attempt 2: Regex on OCR text (works for scans)
            regex_data = self.parser_service.extract_from_text(ocr_text)

            # 4. Merge Data
            # Prefer parsed_data for complex fields like skills, but fill gaps with regex_data
            
            # IMPROVEMENT: Explicitly check for required skills in the text
            found_additional_skills = self.parser_service.extract_skills_from_text(ocr_text, required_skills)
            
            # Combine detected skills with explicit matches
            # Start with pyresparser skills
            final_skills = set(parsed_data.get('skills', []))
            # Add regex fallback skills (if any logic existed there, currently none, so skipping)
            # Add explicit matches
            final_skills.update(found_additional_skills)
            
            candidate_info = {
                'filename': uploaded_file.name,
                'name': parsed_data.get('name'), 
                'email': parsed_data.get('email') or regex_data.get('email'),
                'mobile_number': parsed_data.get('mobile_number') or regex_data.get('mobile_number'),
                'skills': list(final_skills),
                'degree': parsed_data.get('degree'),
                'raw_text': ocr_text # Store raw text just in case
            }
            
            # If name is missing, maybe fallback to filename?
            if not candidate_info['name']:
                candidate_info['name'] = os.path.splitext(uploaded_file.name)[0]

            # 5. Score
            score = self.scoring_service.calculate_score(candidate_info['skills'], required_skills)
            candidate_info['score'] = score
            
            results.append(candidate_info)

        return results

    def generate_reports(self, results):
        # Helper to generate global CSV
        csv_path = os.path.join(self.report_dir, 'summary_report.csv')
        self.report_service.generate_csv_report(results, csv_path)
        return csv_path
