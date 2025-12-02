# scanner/utils.py
import requests
from urllib.parse import urlparse, parse_qs
import os

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}

def safe_get(url, timeout=5):
    try:
        # verify=False 会有警告，这里暂时忽略，实际工程中可以suppress warnings
        r = requests.get(url, headers=headers, timeout=timeout, verify=False)
        return r
    except Exception as e:
        # print(f"[-] 请求失败: {e}") # 调试时可以打开
        return None

def is_static_resource(url):
    """
    判断 URL 是否为静态资源（图片、CSS、JS 等）
    静态资源通常不需要进行 SQL 注入扫描
    """
    try:
        parsed = urlparse(url)
        path = parsed.path.lower()
        # 常见静态资源后缀
        extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', 
                      '.css', '.js', '.ico', '.woff', '.woff2', '.ttf', '.eot',
                      '.pdf', '.doc', '.docx', '.zip', '.rar', '.tar.gz')
        return path.endswith(extensions)
    except:
        return False

def get_url_fingerprint(url):
    """
    生成 URL 指纹，用于去重。
    逻辑：只看 域名 + 路径 + 参数名（忽略参数值）
    """
    try:
        parsed = urlparse(url)
        # 1. 基础部分：域名 + 路径
        base = f"{parsed.netloc}{parsed.path}"
        
        # 2. 参数部分：提取参数名并排序
        query = parse_qs(parsed.query) # 结果如 {'id': ['1'], 'cat': ['2']}
        sorted_params = sorted(query.keys()) # 结果如 ['cat', 'id']
        params_str = "&".join(sorted_params)
        
        # 3. 拼接
        if params_str:
            return f"{base}?{params_str}"
        return base
    except:
        return url
