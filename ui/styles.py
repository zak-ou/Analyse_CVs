import streamlit as st

def load_css():
    st.markdown("""
        <style>
        /* Import Inter Font */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
        }

        /* --- BUTTONS --- */
        .stButton button {
            border-radius: 8px !important;
            border: none !important;
            font-weight: 600 !important;
            padding: 0.6rem 1.2rem !important;
            transition: all 0.3s ease !important;
            /* Primary color logic handled by config, but forcing shape/shadow here */
            box-shadow: 0 4px 6px rgba(108, 92, 231, 0.1);
        }
        .stButton button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(108, 92, 231, 0.25);
        }

        /* --- INPUTS --- */
        /* Target generic input containers */
        div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div, div[data-baseweb="select"] > div {
            border-radius: 8px !important;
            border: 1px solid #E0E0E0 !important;
            background-color: white !important;
        }
        div[data-baseweb="input"] > div:focus-within, div[data-baseweb="textarea"] > div:focus-within {
            border-color: #6C5CE7 !important;
            box-shadow: 0 0 0 2px rgba(108, 92, 231, 0.1) !important;
        }

        /* --- CUSTOM CARD CLASS --- */
        .card {
            background-color: white;
            padding: 24px;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.03);
            border: 1px solid #F0F2F5;
            margin-bottom: 24px;
            transition: transform 0.2s ease-in-out, border-color 0.2s;
        }
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 8px 30px rgba(0, 0, 0, 0.06);
            border-color: #6C5CE7;
        }
        
        .card h3 {
            margin-top: 0;
            color: #2D3436;
            font-size: 1.25rem;
            margin-bottom: 0.5rem;
        }
        
        .card-meta {
            color: #636E72;
            font-size: 0.9rem;
            margin-bottom: 1rem;
            display: flex;
            gap: 15px;
            align-items: center;
        }

        .skill-tag {
            background-color: #EEF2FF;
            color: #6C5CE7;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 500;
            display: inline-block;
            margin-top: 10px;
        }

        /* --- HEADINGS --- */
        h1, h2, h3 {
            color: #2D3436;
            font-weight: 700 !important;
            letter-spacing: -0.5px;
        }
        
        /* Sidebar styling tweak */
        [data-testid="stSidebar"] {
            background-color: #F8F9FA;
            border-right: 1px solid #E9ECEF;
        }
        
        /* Sidebar User Profile Card */
        .sidebar-profile {
            background-color: white;
            padding: 15px;
            border-radius: 12px;
            border: 1px solid #E0E0E0;
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.03);
        }
        .sidebar-avatar {
            width: 40px;
            height: 40px;
            background-color: #EEF2FF;
            color: #6C5CE7;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 1.2rem;
        }
        
        /* Navigation Tabs (Radio Button Hack) */
        div[class*="stRadio"] > label {
            background-color: transparent;
            padding: 10px 15px;
            border-radius: 8px;
            transition: all 0.2s;
            margin-bottom: 5px;
            border: 1px solid transparent;
            cursor: pointer;
        }
        div[class*="stRadio"] > label:hover {
            background-color: white;
            border-color: #E0E0E0;
            transform: translateX(3px);
        }
        /* Active State Hack - Highlight the radio that is checked (Streamlit implementation dependent, this is a best effort UI improvement) */
        div[role="radiogroup"] label[data-baseweb="radio"] > div:first-child {
            /* Hiding the actual circle choice */
            /* display: none; */ 
        }

        </style>
    """, unsafe_allow_html=True)
