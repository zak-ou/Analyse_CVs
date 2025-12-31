# Automated Recruitment System

A modular, robust, and well-documented Python application for automated recruitment.

## Features
- **OCR Integration**: Extracts text from scanned PDFs and images using EasyOCR.
- **NLP Extraction**: parsing of candidate details using pyresparser and Regex.
- **Scoring System**: Ranks candidates based on skill matching.
- **Reporting**: Generates CSV and PDF reports.
- **UI**: Modern interface built with Streamlit.

## Architecture
The system follows a strict Layered Architecture:
- `services`: Business logic (OCR, Parser, Scoring, Reporting).
- `app_logic`: Orchestration (Controller).
- `ui`: Presentation (Streamlit).

## Installation
```bash
pip install -r requirements.txt
```

## Running the App
```bash
python main.py
```
