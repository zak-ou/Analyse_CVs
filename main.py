import os
import sys

def main():
    """
    Entry point to run the Streamlit application.
    """
    print("Starting Recruitment System...")
    
    # Get absolute path to the streamlit app
    current_dir = os.path.dirname(os.path.abspath(__file__))
    app_path = os.path.join(current_dir, "app.py")
    
    print(f"Running Streamlit app from: {app_path}")
    
    # Run Streamlit
    # -m streamlit run is safer than os.system("streamlit run ...")
    cmd = f"{sys.executable} -m streamlit run \"{app_path}\""
    os.system(cmd)

if __name__ == "__main__":
    main()
