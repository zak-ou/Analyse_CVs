import pandas as pd
from fpdf import FPDF
import os

class ReportService:
    def generate_csv_report(self, candidates_data, output_path):
        """
        Generates a CSV report from a list of candidate dictionaries.
        """
        df = pd.DataFrame(candidates_data)
        # Reorder columns to make it readable
        cols = ['name', 'email', 'mobile_number', 'score', 'skills', 'degree', 'filename']
        # Filter for keys that actually exist in the data
        existing_cols = [c for c in cols if c in df.columns]
        # specific reordering if possible, otherwise just dump
        if existing_cols:
            df = df[existing_cols + [c for c in df.columns if c not in existing_cols]]
            
        df.to_csv(output_path, index=False)
        return output_path

    def generate_pdf_report(self, candidate_data, output_path):
        """
        Generates a detailed PDF report for a single candidate.
        """
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        pdf.set_font("Arial", 'B', 16)
        pdf.cell(200, 10, txt=f"Recruitment Report: {candidate_data.get('name', 'Unknown')}", ln=True, align='C')
        pdf.ln(10)

        pdf.set_font("Arial", size=12)
        
        # Details
        pdf.cell(200, 10, txt=f"Filename: {candidate_data.get('filename', 'N/A')}", ln=True)
        pdf.cell(200, 10, txt=f"Email: {candidate_data.get('email', 'N/A')}", ln=True)
        pdf.cell(200, 10, txt=f"Phone: {candidate_data.get('mobile_number', 'N/A')}", ln=True)
        pdf.cell(200, 10, txt=f"Score: {candidate_data.get('score', 0)}/100", ln=True)
        
        pdf.ln(10)
        pdf.set_font("Arial", 'B', 14)
        pdf.cell(200, 10, txt="Matched Skills:", ln=True)
        pdf.set_font("Arial", size=12)
        
        skills = candidate_data.get('skills', [])
        if isinstance(skills, list):
            skills_str = ", ".join(skills)
        else:
            skills_str = str(skills)
            
        # Multi-cell for wrapping text
        pdf.multi_cell(0, 10, txt=skills_str)

        pdf.output(output_path)
        return output_path
