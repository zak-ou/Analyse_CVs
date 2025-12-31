import nltk
import ssl
import sys
import subprocess

def install_spacy_model():
    print("Checking/Installing Spacy model 'en_core_web_sm'...")
    try:
        import spacy
        # Try to load it to see if it exists
        if not spacy.util.is_package("en_core_web_sm"):
            print("Downloading en_core_web_sm...")
            subprocess.check_call([sys.executable, "-m", "spacy", "download", "en_core_web_sm"])
        else:
            print("en_core_web_sm is already installed.")
    except Exception as e:
        print(f"Error checking spacy model: {e}")

def download_nltk_data():
    print("Downloading NLTK data...")
    try:
        _create_unverified_https_context = ssl._create_unverified_context
    except AttributeError:
        pass
    else:
        ssl._create_default_https_context = _create_unverified_https_context

    required_packages = ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'universal_tagset']
    
    for package in required_packages:
        try:
            print(f"Downloading {package}...")
            nltk.download(package)
            print(f"Successfully downloaded {package}")
        except Exception as e:
            print(f"Failed to download {package}: {e}")

if __name__ == "__main__":
    print("Starting environment setup...")
    download_nltk_data()
    install_spacy_model()
    print("Setup complete. You can now run 'python main.py'")
