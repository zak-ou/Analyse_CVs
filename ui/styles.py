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
            background: linear-gradient(135deg, rgba(255, 255, 255, 0.8) 0%, rgba(255, 255, 255, 0.4) 100%);
            padding: 18px;
            border-radius: 16px;
            border: 1px solid rgba(108, 92, 231, 0.1);
            display: flex;
            align-items: center;
            gap: 15px;
            margin-bottom: 25px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.02);
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }
        .sidebar-profile:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(108, 92, 231, 0.1);
            border-color: rgba(108, 92, 231, 0.3);
        }
        .sidebar-avatar {
            width: 48px;
            height: 48px;
            background: linear-gradient(135deg, #6C5CE7 0%, #a29bfe 100%);
            color: white;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 700;
            font-size: 1.4rem;
            box-shadow: 0 4px 10px rgba(108, 92, 231, 0.3);
        }
        .sidebar-info {
            flex: 1;
            overflow: hidden;
        }
        .sidebar-name {
            font-weight: 700;
            color: #2D3436;
            font-size: 1rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }
        .sidebar-role {
            color: #636E72;
            font-size: 0.8rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-weight: 500;
        }
        
        /* Sidebar Logo Area */
        .sidebar-logo {
            padding: 10px 10px 30px 10px;
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .sidebar-logo-icon {
            font-size: 2rem;
            filter: drop-shadow(0 4px 6px rgba(108, 92, 231, 0.2));
        }
        .sidebar-logo-text {
            font-family: 'Inter', sans-serif;
            font-weight: 800;
            font-size: 1.5rem;
            background: linear-gradient(135deg, #6C5CE7 0%, #a29bfe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            letter-spacing: -1px;
        }
        
        /* Sidebar Footer Bottom Alignment */
        [data-testid="stSidebarUserContent"] {
            display: flex;
            flex-direction: column;
            height: calc(100vh - 20px);
        }
        
        [data-testid="stSidebarUserContent"] > div:first-child {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .sidebar-footer {
            margin-top: auto;
            padding-top: 20px;
            padding-bottom: 10px;
            border-top: 1px solid #E9ECEF;
            background-color: transparent;
        }
        .stButton button[kind="secondary"] {
            border: 1px solid #FF7675 !important;
            color: #FF7675 !important;
            background-color: transparent !important;
        }
        .stButton button[kind="secondary"]:hover {
            background-color: #FFF5F5 !important;
            border-color: #D63031 !important;
            color: #D63031 !important;
        }
        /* --- HIDE STREAMLIT BRANDING --- */
        [data-testid="stAppDeployButton"] {display: none;}
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        div[data-testid="stDecoration"] {display: none;}
        
        /* Ensure the header itself is visible but transparent to show the sidebar toggle */
        header {
            background-color: transparent !important;
        }
        
        /* Style the sidebar toggle button */
        button[data-testid="stBaseButton-headerNoPadding"] {
            color: #6C5CE7 !important;
            background-color: white !important;
            border-radius: 50% !important;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1) !important;
            margin-left: 10px !important;
            margin-top: 10px !important;
        }
        
        </style>
    """, unsafe_allow_html=True)
