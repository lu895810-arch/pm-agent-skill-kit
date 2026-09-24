import sys
from pathlib import Path

# Add libs to path
current_dir = Path(__file__).parent
libs_path = current_dir.parent / "libs"
sys.path.append(str(libs_path))

try:
    from api_client import AntigravityClient
except ImportError:
    print("[-] Error: libs module not found")
    sys.exit(1)

def main():
    client = AntigravityClient()
    print("[*] Fetching available models...")
    
    models = client.get_models()
    
    if not models:
        print("[-] No models found or request failed.")
        return

    print(f"\n[+] Found {len(models)} models:\n")
    
    # Categorize models for better readability
    chat_models = []
    image_models = []
    other_models = []
    
    for m in models:
        mid = m['id'] if isinstance(m, dict) else str(m)
        if "image" in mid or "paint" in mid:
            image_models.append(mid)
        elif "claude" in mid or "gpt" in mid or "gemini" in mid:
            chat_models.append(mid)
        else:
            other_models.append(mid)
            
    if chat_models:
        print("--- Chat / Text Models ---")
        for m in sorted(chat_models):
            print(f"  {m}")
        print("")
        
    if image_models:
        print("--- Image / Vision Models ---")
        for m in sorted(image_models):
            print(f"  {m}")
        print("")

    if other_models:
        print("--- Other Models ---")
        for m in sorted(other_models):
            print(f"  {m}")

if __name__ == "__main__":
    main()
