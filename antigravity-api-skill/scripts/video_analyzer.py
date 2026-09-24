import sys
import os
import json
from pathlib import Path

# 自动寻找库文件路径
current_dir = Path(__file__).parent
libs_path = current_dir.parent / "libs"
sys.path.append(str(libs_path))

try:
    from api_client import AntigravityClient
except ImportError:
    print("[-] 错误: 找不到 libs 模块，请检查目录结构。")
    sys.exit(1)

def analyze_video(video_path, custom_prompt=None):
    if not os.path.exists(video_path):
        print(f"[-] 错误: 找不到视频文件 {video_path}")
        return

    # 1. 实例化客户端 (自动从 config.json 获取端口和 key)
    client = AntigravityClient()
    
    # 2. 默认的高精度分析提示词
    default_prompt = (
        "请拆解视频的镜头。分析每一个镜头的开始时间、持续秒数、以及内容描述（包含景别、动作）。\n"
        "请严格按照以下 JSON 数组格式输出，不要包含 Markdown 代码块标记或任何其他多余文本：\n"
        "[\n"
        "  {\"start\": \"HH:MM:SS\", \"duration\": 5, \"text\": \"分镜分析描述\"},\n"
        "  ...\n"
        "]\n"
    )
    prompt = custom_prompt or default_prompt
    
    # 3. 指定最适合视频分析的模型
    # 优先使用 gemini-3-flash
    model = "gemini-3-flash"
    
    print(f"[*] 正在分析视频: {os.path.basename(video_path)}", file=sys.stderr)
    print(f"[*] 正在请求模型: {model} (连接地址: {client.base_url})", file=sys.stderr)
    
    messages = [{"role": "user", "content": prompt}]
    
    # 获取响应流
    try:
        response = client.chat_completion(messages, model=model, file_paths=[video_path])
    except Exception as e:
        print(f"[-] 连接服务失败: {e}", file=sys.stderr)
        return
    
    if not response or response.status_code != 200:
        if response:
            print(f"[-] API 请求失败 ({response.status_code}): {response.text}", file=sys.stderr)
        else:
            print("[-] 未能收到有效响应，请确认服务是否开启。", file=sys.stderr)
        return

    # 4. 获取完整 JSON 响应
    full_content = ""
    for line in response.iter_lines():
        if not line: continue
        line_str = line.decode('utf-8')
        if line_str.startswith("data: "):
            data_str = line_str[6:]
            if data_str.strip() == "[DONE]": break
            try:
                data = json.loads(data_str)
                content = data.get("choices", [{}])[0].get("delta", {}).get("content", "")
                if content:
                    full_content += content
            except: pass
    
    # 清理 Markdown 代码块包裹
    clean_json = full_content.strip()
    if clean_json.startswith("```"):
        clean_json = clean_json.split("\n", 1)[1]
    if clean_json.endswith("```"):
        clean_json = clean_json.rsplit("\n", 1)[0]
    
    print(clean_json.strip())

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python video_analyzer.py \"视频绝对路径\" [可选自定义提示词]")
    else:
        # 处理可能的双引号包裹
        path = sys.argv[1].strip('"').strip("'")
        p = sys.argv[2] if len(sys.argv) > 2 else None
        analyze_video(path, p)
