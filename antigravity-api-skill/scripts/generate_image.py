import sys
import os
import time
import base64
import re
import requests
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
    if len(sys.argv) < 2:
        print("Usage: python generate_image.py \"Prompt\" [size] [image_path]")
        return

    prompt = sys.argv[1]
    size_arg = sys.argv[2] if len(sys.argv) > 2 else "1024x1024"
    image_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    ratio_map = {
        "16:9": "1280x720",
        "9:16": "720x1280", 
        "1:1": "1024x1024"
    }
    
    target_size = ratio_map.get(size_arg, size_arg)
    
    client = AntigravityClient()
    res = client.generate_image(prompt, size=target_size, image_path=image_path)
    
    if res and "choices" in res:
        content = res["choices"][0].get("message", {}).get("content", "")
        print(f"[*] Response content received (Length: {len(content)})")
        
        save_dir = Path(os.getcwd()) / "generated_assets"
        save_dir.mkdir(parents=True, exist_ok=True)
        saved_any = False

        # 1. Look for plain URLs
        urls = re.findall(r"http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+", content)
        if urls:
            for i, url in enumerate(urls):
                try:
                    print(f"[*] Downloading image from {url}...")
                    img_resp = requests.get(url, timeout=30)
                    if img_resp.status_code == 200:
                        fname = f"antigravity_{int(time.time())}_url_{i}.png"
                        save_path = save_dir / fname
                        save_path.write_bytes(img_resp.content)
                        print(f"[+] Image saved: {save_path}")
                        saved_any = True
                except Exception as e:
                    print(f"[-] Download failed: {e}")

        # 2. Look for Base64 Data (common in Markdown or raw)
        # Pattern: data:image/png;base64,xxxx or just long base64 string inside parentheses
        b64_matches = re.findall(r"data:image\/[a-zA-Z]+;base64,([a-zA-Z0-9+/=]+)", content)
        if not b64_matches:
            # Try to find base64-like blobs in Markdown image syntax ![alt](data:...)
            b64_matches = re.findall(r"base64,([a-zA-Z0-9+/=]{100,})", content)

        if b64_matches:
            for i, b64_str in enumerate(b64_matches):
                try:
                    print(f"[*] Decoding Base64 image {i}...")
                    img_data = base64.b64decode(b64_str)
                    fname = f"antigravity_{int(time.time())}_b64_{i}.png"
                    save_path = save_dir / fname
                    save_path.write_bytes(img_data)
                    print(f"[+] Image saved: {save_path}")
                    saved_any = True
                except Exception as e:
                    print(f"[-] Base64 decode failed: {e}")

        if not saved_any:
            print("[-] No image URL or Base64 data found in response")
            if len(content) > 200:
                print(f"[*] Content snippet: {content[:200]}...")
    else:
        print("[-] Generation failed")

if __name__ == "__main__":
    main()
