import sys
import os
import json
from pathlib import Path

# 强制设置标准输出为 UTF-8，解决 Windows 乱码问题
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        # 兼容旧版本 Python
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

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
        print("Usage: python chat.py \"Your prompt here\" [model_name] [media_path]")
        return

    prompt = sys.argv[1]
    # Try to find file path in args
    media_paths = []
    # Collect all existing file paths from arguments
    for arg in sys.argv[2:]:
        if os.path.exists(arg):
            media_paths.append(arg)
            
    # Set model if it was provided and isn't a file path
    model = None
    if len(sys.argv) > 2 and not os.path.exists(sys.argv[2]):
        model = sys.argv[2]
    
    client = AntigravityClient()
    
    messages = [{"role": "user", "content": prompt}]
    
    print(f"[*] Asking {model or client.config.get('default_chat_model')}...")
    
    response = client.chat_completion(messages, model=model, file_paths=media_paths)
    
    if not response or response.status_code != 200:
        if response:
            print(f"[-] AI Request failed ({response.status_code}): {response.text}")
        return

    full_content = ""
    print("\nStarting response stream:\n" + "-"*30)
    
    # Simple SSE parser
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
                    full_content += content
            except:
                pass
                
    print("\n" + "-"*30 + "\n[Done]")

if __name__ == "__main__":
    main()
