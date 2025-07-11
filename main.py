import configparser
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
from urllib.parse import urljoin
import webbrowser
import markdown2
import time
import os
import urllib3
from urllib3.exceptions import InsecureRequestWarning
import random
import glob
import tkinter as tk
from tkinter import filedialog

# 禁用SSL警告 - 注意：这会降低安全性，仅在开发/测试环境使用
urllib3.disable_warnings(InsecureRequestWarning)

# 常见的用户代理列表，模拟真实浏览器
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36'
]

def get_random_headers():
    """生成随机的HTTP请求头，模拟真实浏览器"""
    return {
        'User-Agent': random.choice(USER_AGENTS),
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0'
    }

def load_config(filename="config.ini"):
    """从 .ini 文件加载配置"""
    config = configparser.ConfigParser()
    # 指定UTF-8编码以正确读取包含中文字符的配置文件
    config.read(filename, encoding='utf-8')
    return config

def format_file_size(size_bytes):
    """将字节数转换为人类可读的格式"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    if i == 0:  # 字节数
        return f"{int(size)} {size_names[i]}"
    else:
        return f"{size:.1f} {size_names[i]}"

def get_js_file_size(url):
    """获取JavaScript文件的大小"""
    try:
        # 使用HEAD请求先尝试获取Content-Length
        response = requests.head(url, timeout=10, verify=False)
        content_length = response.headers.get('content-length')
        if content_length:
            return int(content_length)
        
        # 如果HEAD请求没有返回Content-Length，则使用GET请求
        response = requests.get(url, timeout=10, verify=False)
        response.raise_for_status()
        return len(response.content)
    except Exception as e:
        print(f"获取文件大小时出错 ({url}): {e}")
        return 0

def get_js_urls_from_page(url):
    """从给定的URL中提取所有JavaScript文件的URL，并获取文件大小"""
    try:
        headers = get_random_headers()
        
        # 禁用SSL证书验证，忽略自签证书和过期证书问题，使用随机User-Agent
        response = requests.get(url, timeout=15, verify=False, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        js_files = []
        for script_tag in soup.find_all('script', src=True):
            js_url = script_tag.get('src')
            # 确保js_url是字符串
            if isinstance(js_url, str):
                # 将相对URL转换为绝对URL
                absolute_js_url = urljoin(url, js_url)
                print(f"  正在获取文件大小: {absolute_js_url}")
                file_size = get_js_file_size(absolute_js_url)
                js_files.append({
                    'url': absolute_js_url,
                    'size': file_size,
                    'size_formatted': format_file_size(file_size)
                })
        return js_files
    except requests.RequestException as e:
        print(f"获取页面内容时出错: {e}")
        return []

def get_js_content(url):
    """获取单个JS文件的内容，使用反爬虫措施"""
    try:
        headers = get_random_headers()
        
        # 添加随机延迟，模拟人类行为
        time.sleep(random.uniform(1.0, 3.0))
        
        # 禁用SSL证书验证，忽略自签证书和过期证书问题，使用随机User-Agent
        response = requests.get(url, timeout=15, verify=False, headers=headers)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"下载JS文件时出错 ({url}): {e}")
        return None

def read_local_js_file(file_path):
    """读取本地JS文件内容"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()
    except UnicodeDecodeError:
        # 如果UTF-8解码失败，尝试其他编码
        try:
            with open(file_path, 'r', encoding='gbk') as file:
                return file.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as file:
                    return file.read()
            except Exception as e:
                print(f"读取文件时出错 ({file_path}): {e}")
                return None
    except Exception as e:
        print(f"读取文件时出错 ({file_path}): {e}")
        return None

def get_local_js_files(directory=None):
    """获取本地目录中的JS文件列表"""
    if directory is None:
        directory = os.getcwd()
    
    js_extensions = ['*.js', '*.mjs', '*.jsx']
    js_files = []
    
    for ext in js_extensions:
        pattern = os.path.join(directory, '**', ext)
        files = glob.glob(pattern, recursive=True)
        for file_path in files:
            file_size = os.path.getsize(file_path)
            js_files.append({
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': file_size,
                'size_formatted': format_file_size(file_size)
            })
    
    return js_files

def select_files_with_gui():
    """使用GUI选择文件"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    file_paths = filedialog.askopenfilenames(
        title="选择JS文件",
        filetypes=[
            ("JavaScript files", "*.js"),
            ("Module JavaScript files", "*.mjs"),
            ("JSX files", "*.jsx"),
            ("All files", "*.*")
        ]
    )
    
    root.destroy()
    
    if file_paths:
        js_files = []
        for file_path in file_paths:
            file_size = os.path.getsize(file_path)
            js_files.append({
                'path': file_path,
                'name': os.path.basename(file_path),
                'size': file_size,
                'size_formatted': format_file_size(file_size)
            })
        return js_files
    return []

def select_directory_with_gui():
    """使用GUI选择目录"""
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    directory = filedialog.askdirectory(title="选择包含JS文件的目录")
    
    root.destroy()
    
    if directory:
        return get_local_js_files(directory)
    return []

def chunk_string(string, length):
    """将字符串按指定长度分割"""
    return (string[0+i:length+i] for i in range(0, len(string), length))

def analyze_js_with_gemini(config, js_code):
    """使用Gemini API分析JavaScript代码，支持分块"""
    proxy_set = False
    try:
        # 为gRPC设置代理 (google-generativeai 使用 gRPC)
        if config.has_section('Proxy') and config.get('Proxy', 'type', fallback=''):
            proxy_type = config.get('Proxy', 'type')
            host = config.get('Proxy', 'host')
            port = config.get('Proxy', 'port')
            # grpcio 库会识别 'https_proxy' (全小写) 环境变量
            proxy_url = f"{proxy_type}://{host}:{port}"
            os.environ['https_proxy'] = proxy_url
            proxy_set = True
        
        # 禁用gRPC的SSL验证以忽略证书问题
        os.environ['GRPC_SSL_CIPHER_SUITES'] = 'HIGH+ECDSA'
        os.environ['PYTHONHTTPSVERIFY'] = '0'

        # 配置Gemini
        api_key = config.get('Gemini', 'api_key')
        model_name = config.get('Gemini', 'model')
        max_chunk_size = config.getint('Gemini', 'max_chunk_size', fallback=15000)
        prompt_template = config.get('Prompt', 'custom_prompt')
        chunk_prompt_template = config.get('Prompt', 'chunk_prompt')

        if not api_key or api_key == "YOUR_GEMINI_API_KEY":
            print("错误: 请在 config.ini 文件中配置您的Gemini API key。")
            return None

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(model_name)
        
        # 检查是否需要分块
        if len(js_code) <= max_chunk_size:
            # 不分块
            prompt = prompt_template.format(js_code=js_code)
            response = model.generate_content(prompt)
            return response.text
        else:
            # 分块处理
            print(f"  代码过长 ({len(js_code)} 字符)，将分块发送...")
            chunks = list(chunk_string(js_code, max_chunk_size))
            full_analysis = []
            
            # 处理第一块
            print(f"  正在分析第 1/{len(chunks)} 块...")
            first_prompt = prompt_template.format(js_code=chunks[0])
            response = model.generate_content(first_prompt)
            full_analysis.append(response.text)
            
            # 处理后续块
            for i, chunk in enumerate(chunks[1:], start=2):
                print(f"  正在分析第 {i}/{len(chunks)} 块...")
                next_prompt = chunk_prompt_template.format(js_code=chunk)
                response = model.generate_content(next_prompt)
                full_analysis.append(response.text)
            
            # 对所有分块结果进行最终总结
            print("  所有分块分析完成，正在进行最终总结...")
            summary_prompt_template = config.get('Prompt', 'summary_prompt')
            combined_reports = "\n\n--- 单独报告分割线 ---\n\n".join(full_analysis)
            summary_prompt = summary_prompt_template.format(analysis_reports=combined_reports)
            
            summary_response = model.generate_content(summary_prompt)
            return summary_response.text

    except Exception as e:
        print(f"调用Gemini API时出错: {e}")
        return None
    finally:
        # 清理环境变量，以免影响其他可能的网络调用
        if proxy_set:
            if 'https_proxy' in os.environ:
                del os.environ['https_proxy']
        # 清理SSL相关环境变量
        if 'GRPC_SSL_CIPHER_SUITES' in os.environ:
            del os.environ['GRPC_SSL_CIPHER_SUITES']
        if 'PYTHONHTTPSVERIFY' in os.environ:
            del os.environ['PYTHONHTTPSVERIFY']

def main():
    """主函数"""
    config = load_config()
    
    print("请选择分析模式:")
    print("1. 从网站URL提取JS文件")
    print("2. 选择本地JS文件")
    print("3. 选择本地目录扫描JS文件")
    print("4. 当前目录扫描JS文件")
    
    while True:
        choice = input("\n请输入选择 (1-4): ").strip()
        if choice in ['1', '2', '3', '4']:
            break
        print("无效选择，请输入1、2、3或4")
    
    js_files = []
    
    if choice == '1':
        # 原有的网站URL模式
        target_url = input("请输入要分析的网站URL: ")
        print(f"\n[1] 正在从 {target_url} 提取JS文件链接...")
        js_files = get_js_urls_from_page(target_url)
        source_type = "url"
        
    elif choice == '2':
        # 使用GUI选择文件
        print("\n[1] 正在打开文件选择对话框...")
        js_files = select_files_with_gui()
        source_type = "local"
        
    elif choice == '3':
        # 使用GUI选择目录
        print("\n[1] 正在打开目录选择对话框...")
        js_files = select_directory_with_gui()
        source_type = "local"
        
    elif choice == '4':
        # 当前目录扫描
        print(f"\n[1] 正在扫描当前目录: {os.getcwd()}")
        js_files = get_local_js_files()
        source_type = "local"
    
    if not js_files:
        print("未能找到任何JS文件。")
        return
    
    print(f"找到 {len(js_files)} 个JS文件:")
    for i, js_file in enumerate(js_files, 1):
        if source_type == "url":
            print(f"  {i}. {js_file['url']} [{js_file['size_formatted']}]")
        else:
            print(f"  {i}. {js_file['name']} [{js_file['size_formatted']}]")
            print(f"      路径: {js_file['path']}")

    # 让用户选择要分析的文件
    while True:
        choice = input("\n请输入要分析的JS文件编号 (用逗号分隔, 或输入 'all' 分析全部): ").strip().lower()
        if choice == 'all':
            selected_indices = range(len(js_files))
            break
        else:
            try:
                selected_indices = [int(i.strip()) - 1 for i in choice.split(',')]
                if all(0 <= i < len(js_files) for i in selected_indices):
                    break
                else:
                    print("错误: 输入的编号超出范围，请重新输入。")
            except ValueError:
                print("错误: 输入无效，请输入数字编号。")

    # 分析选定的文件
    for index in selected_indices:
        js_file = js_files[index]
        
        if source_type == "url":
            js_url = js_file['url']
            print(f"\n[2] 正在分析选定的文件: {js_url} [{js_file['size_formatted']}]")
            js_content = get_js_content(js_url)
            file_name = js_url.split('/')[-1] or 'unknown.js'
        else:
            js_path = js_file['path']
            file_name = js_file['name']
            print(f"\n[2] 正在分析选定的文件: {file_name} [{js_file['size_formatted']}]")
            print(f"    文件路径: {js_path}")
            js_content = read_local_js_file(js_path)
        
        if js_content:
            print("[3] 已获取JS代码，正在发送到Gemini进行分析...")
            analysis_result = analyze_js_with_gemini(config, js_content)
            if analysis_result:
                print("[4] 分析完成，正在生成HTML报告...")
                html_content = markdown2.markdown(analysis_result, extras=["fenced-code-blocks", "tables"])
                
                # 添加一些CSS样式
                html_template = f"""
               <!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JS代码安全分析报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, "Noto Sans", sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}

        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: #fff;
            border-radius: 20px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
            animation: fadeIn 0.8s ease-out;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(30px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        .header {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 40px;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        .header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="75" cy="75" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="50" cy="10" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="10" cy="60" r="1" fill="rgba(255,255,255,0.1)"/><circle cx="90" cy="40" r="1" fill="rgba(255,255,255,0.1)"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
            opacity: 0.3;
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 700;
            position: relative;
            z-index: 1;
        }}

        .header .subtitle {{
            font-size: 1.2em;
            opacity: 0.9;
            position: relative;
            z-index: 1;
        }}

        .content {{
            padding: 40px;
        }}

        .file-info {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 30px;
            border-radius: 15px;
            margin-bottom: 30px;
            border-left: 5px solid #3498db;
            position: relative;
            overflow: hidden;
        }}

        .file-info::before {{
            content: '📄';
            position: absolute;
            top: 20px;
            right: 20px;
            font-size: 3em;
            opacity: 0.1;
        }}

        .file-info h3 {{
            color: #2c3e50;
            margin-bottom: 20px;
            font-size: 1.5em;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .file-info h3::before {{
            content: '🔍';
            font-size: 1.2em;
        }}

        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}

        .info-item {{
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            transition: transform 0.3s ease;
        }}

        .info-item:hover {{
            transform: translateY(-2px);
        }}

        .info-item strong {{
            color: #2c3e50;
            display: block;
            margin-bottom: 5px;
            font-weight: 600;
        }}

        .info-item span {{
            color: #666;
            font-size: 0.95em;
        }}

        h1, h2, h3, h4, h5, h6 {{
            color: #2c3e50;
            margin-bottom: 15px;
            font-weight: 600;
        }}

        h1 {{ font-size: 2.2em; border-bottom: 3px solid #3498db; padding-bottom: 10px; }}
        h2 {{ font-size: 1.8em; margin-top: 40px; position: relative; }}
        h3 {{ font-size: 1.4em; margin-top: 30px; }}

        h2::before {{
            content: '';
            position: absolute;
            left: -20px;
            top: 50%;
            transform: translateY(-50%);
            width: 4px;
            height: 20px;
            background: linear-gradient(135deg, #3498db, #2c3e50);
            border-radius: 2px;
        }}

        p {{
            margin-bottom: 15px;
            text-align: justify;
        }}

        code {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 4px 8px;
            border-radius: 6px;
            font-family: "Fira Code", "Courier New", Courier, monospace;
            font-size: 0.9em;
            color: #e74c3c;
            border: 1px solid #dee2e6;
        }}

        pre {{
            background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
            color: #ecf0f1;
            padding: 25px;
            border-radius: 12px;
            overflow-x: auto;
            margin: 20px 0;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            position: relative;
            border: 1px solid #34495e;
        }}

        pre::before {{
            content: '';
            position: absolute;
            top: 15px;
            left: 20px;
            width: 12px;
            height: 12px;
            background: #e74c3c;
            border-radius: 50%;
            box-shadow: 24px 0 0 #f39c12, 48px 0 0 #27ae60;
        }}

        pre code {{
            background: transparent;
            padding: 0;
            border: none;
            color: inherit;
            font-size: 0.9em;
            line-height: 1.6;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
            background: white;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }}

        th, td {{
            padding: 15px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}

        th {{
            background: linear-gradient(135deg, #3498db 0%, #2c3e50 100%);
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.9em;
            letter-spacing: 0.5px;
        }}

        tr:nth-child(even) {{
            background: #f8f9fa;
        }}

        tr:hover {{
            background: #e3f2fd;
            transition: background 0.3s ease;
        }}

        .alert {{
            padding: 20px;
            margin: 20px 0;
            border-radius: 10px;
            border-left: 5px solid;
            position: relative;
            overflow: hidden;
        }}

        .alert::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            opacity: 0.05;
            background: repeating-linear-gradient(
                45deg,
                transparent,
                transparent 10px,
                currentColor 10px,
                currentColor 20px
            );
        }}

        .alert-danger {{
            background: #fff5f5;
            border-left-color: #e74c3c;
            color: #c0392b;
        }}

        .alert-warning {{
            background: #fefcf3;
            border-left-color: #f39c12;
            color: #d68910;
        }}

        .alert-info {{
            background: #f0f8ff;
            border-left-color: #3498db;
            color: #2980b9;
        }}

        .alert-success {{
            background: #f0fff4;
            border-left-color: #27ae60;
            color: #229954;
        }}

        blockquote {{
            background: #f8f9fa;
            border-left: 4px solid #3498db;
            padding: 20px;
            margin: 20px 0;
            border-radius: 0 10px 10px 0;
            font-style: italic;
            position: relative;
        }}

        blockquote::before {{
            content: '"';
            font-size: 4em;
            color: #3498db;
            position: absolute;
            top: -10px;
            left: 10px;
            opacity: 0.3;
        }}

        ul, ol {{
            margin: 15px 0;
            padding-left: 30px;
        }}

        li {{
            margin-bottom: 8px;
            position: relative;
        }}

        ul li::marker {{
            content: '▶ ';
            color: #3498db;
        }}

        .footer {{
            background: linear-gradient(135deg, #2c3e50 0%, #3498db 100%);
            color: white;
            padding: 30px;
            text-align: center;
            margin-top: 40px;
        }}

        .footer p {{
            margin: 0;
            opacity: 0.9;
        }}

        .badge {{
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin: 2px;
        }}

        .badge-danger {{ background: #e74c3c; color: white; }}
        .badge-warning {{ background: #f39c12; color: white; }}
        .badge-info {{ background: #3498db; color: white; }}
        .badge-success {{ background: #27ae60; color: white; }}

        .progress-bar {{
            background: #e9ecef;
            border-radius: 10px;
            height: 20px;
            overflow: hidden;
            margin: 10px 0;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #3498db, #2c3e50);
            border-radius: 10px;
            transition: width 0.8s ease;
        }}

        @media (max-width: 768px) {{
            .container {{
                margin: 10px;
                border-radius: 15px;
            }}
            
            .header, .content {{
                padding: 20px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
            
            .info-grid {{
                grid-template-columns: 1fr;
            }}
            
            pre {{
                padding: 15px;
                font-size: 0.8em;
            }}
        }}

        /* 滚动条样式 */
        ::-webkit-scrollbar {{
            width: 8px;
            height: 8px;
        }}

        ::-webkit-scrollbar-track {{
            background: #f1f1f1;
            border-radius: 10px;
        }}

        ::-webkit-scrollbar-thumb {{
            background: linear-gradient(135deg, #3498db, #2c3e50);
            border-radius: 10px;
        }}

        ::-webkit-scrollbar-thumb:hover {{
            background: linear-gradient(135deg, #2980b9, #34495e);
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔒 JS代码安全分析报告</h1>
            <div class="subtitle">专业的JavaScript代码安全检测与分析</div>
        </div>
        
        <div class="content">
            <div class="file-info">
                <h3>📋 分析文件信息</h3>
                <div class="info-grid">
                    <div class="info-item">
                        <strong>📄 文件名称</strong>
                        <span>{file_name}</span>
                    </div>
                    <div class="info-item">
                        <strong>📊 文件大小</strong>
                        <span>{js_file['size_formatted']}</span>
                    </div>
                    <div class="info-item">
                        <strong>🔗 文件路径</strong>
                        <span>{"" if source_type == "url" else js_file['path']}</span>
                    </div>
                    <div class="info-item">
                        <strong>🌐 文件URL</strong>
                        <span>{js_file['url'] if source_type == "url" else "本地文件"}</span>
                    </div>
                    <div class="info-item">
                        <strong>⏰ 分析时间</strong>
                        <span>{time.strftime('%Y-%m-%d %H:%M:%S')}</span>
                    </div>
                </div>
            </div>
            
            <hr style="border: none; height: 2px; background: linear-gradient(90deg, #3498db, #2c3e50); margin: 40px 0; border-radius: 1px;">
            
            {html_content}
        </div>
        
        <div class="footer">
            <p>🚀 由 JavaScript 安全分析工具生成 | 📧 如发现漏洞请帮忙点个⭐</p>
        </div>
    </div>
</body>
</html>

                """
                
                # 创建reports目录（如果不存在）
                if not os.path.exists('reports'):
                    os.makedirs('reports')
                
                # 生成安全的文件名
                safe_filename = "".join(c for c in file_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
                report_filename = os.path.join('reports', f"report_{safe_filename}_{int(time.time())}.html")
                
                with open(report_filename, "w", encoding="utf-8") as f:
                    f.write(html_template)
                
                print(f"[5] 报告已生成: {report_filename}")
                
                # 询问是否打开报告
                open_report = input("是否在浏览器中打开报告? (y/n): ").strip().lower()
                if open_report in ['y', 'yes', '是']:
                    webbrowser.open(report_filename)
                
                print("--- 分析结束 ---\n")
            else:
                print("未能获取分析结果。")
        else:
            print("未能获取JS内容，跳过分析。")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序已被用户中断。")
    except Exception as e:
        print(f"\n程序运行时发生错误: {e}")
        import traceback
        traceback.print_exc()
