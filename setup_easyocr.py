import os
import urllib.request
import sys
import time

def download_file(url, dest_path):
    print(f"Downloading {url}...")
    try:
        urllib.request.urlretrieve(url, dest_path)
        print(f"Successfully downloaded to {dest_path}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        # Simple retry
        print("Retrying in 3 seconds...")
        time.sleep(3)
        try:
            urllib.request.urlretrieve(url, dest_path)
            print(f"Successfully downloaded to {dest_path}")
        except Exception as e2:
            print(f"Failed to download {url}: {e2}")

def setup_easyocr():
    # easyocr default model directory
    # On Windows: C:\Users\Username\.EasyOCR\model
    user_home = os.path.expanduser('~')
    model_dir = os.path.join(user_home, '.EasyOCR', 'model')
    
    if not os.path.exists(model_dir):
        print(f"Creating directory: {model_dir}")
        os.makedirs(model_dir, exist_ok=True)
    else:
        print(f"Directory exists: {model_dir}")

    # Official EasyOCR model URLs
    models = {
        'craft_mlt_25k.pth': 'https://github.com/JaidedAI/EasyOCR/releases/download/pre-v1.1.6/craft_mlt_25k.pth',
        'english_g2.pth': 'https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/english_g2.pth',
        'latin_g2.pth': 'https://github.com/JaidedAI/EasyOCR/releases/download/v1.3/latin_g2.pth' 
    }

    for filename, url in models.items():
        dest_path = os.path.join(model_dir, filename)
        if os.path.exists(dest_path):
            print(f"Model {filename} already exists. Skipping.")
            # Verify size is not 0 (broken download) via simple check
            if os.path.getsize(dest_path) < 1000:
                 print(f"File {filename} seems corrupted (too small). Re-downloading.")
                 download_file(url, dest_path)
        else:
            download_file(url, dest_path)

if __name__ == "__main__":
    setup_easyocr()
    print("EasyOCR model setup complete.")
