import sys
import os
import base64
import requests
import mimetypes
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
    if len(sys.argv) < 3:
        print("Usage: python test_video_upload.py \"Prompt\" \"Video Path\"")
        return

    prompt = sys.argv[1]
    video_path = sys.argv[2]
    
    if not os.path.exists(video_path):
        print(f"[-] Video file not found: {video_path}")
        return

    print(f"[*] Reading video file: {video_path}...")
    try:
        video_data = open(video_path, "rb").read()
        b64_video = base64.b64encode(video_data).decode("utf-8")
        
        # Simple mime guessing, default to mp4
        mime_type, _ = mimetypes.guess_type(video_path)
        mime_type = mime_type or "video/mp4"
        
        print(f"[*] Video size: {len(video_data)/1024/1024:.2f} MB")
        print(f"[*] MIME type: {mime_type}")
    except Exception as e:
        print(f"[-] Failed to read video: {e}")
        return

    client = AntigravityClient()
    
    # Constructing payload with video (Google/Gemini style or OpenAI Vision style experiment)
    # Gemini 1.5 Pro/Flash supports video input. The structure usually is a list of parts.
    # For OpenAI compatibility layers, it might be treated as an image_url with video mime type, 
    # or a specific 'video_url' block depending on the backend implementation.
    # We will try the standard "image_url" block first but with video mime type, 
    # as some adapters use this for all media.
    
    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url", # Trying image_url first as a generic media container
                    "image_url": {"url": f"data:{mime_type};base64,{b64_video}"}
                }
            ]
        }
    ]
    
    # We use a chat model that is likely to support multimodal (Gemini 1.5 Pro / Flash)
    model = "gemini-3-flash" 
    
    print(f"[*] Sending Video Chat Request to {model}...")
    
    # We use chat_completion method but manually override the payload if needed within the method, 
    # or just call it directly since we constructed the messages.
    
    try:
        # Re-using the client logic but injecting our multimodal message
        response = client.chat_completion(messages, model=model)
        
        if response:
            print("\n" + "="*30)
            print(f"Status Code: {response.status_code}")
            # Stream the response
            for line in response.iter_lines():
                if not line: continue
                line_str = line.decode('utf-8')
                if line_str.startswith("data: "):
                    data_str = line_str[6:]
                    if data_str.strip() == "[DONE]":
                        break
                    try:
                        data = json.loads(data_str)
                        delta = data.get("choices", [{}])[0].get("delta", {})
                        content = delta.get("content", "")
                        if content:
                            print(content, end="", flush=True)
                    except:
                        pass
            print("\n" + "="*30)
        else:
            print("[-] No response received")
            
    except Exception as e:
        print(f"[-] Request failed: {e}")

if __name__ == "__main__":
    import json
    main()
