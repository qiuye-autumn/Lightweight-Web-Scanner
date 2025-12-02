# scanner/xss.py
import urllib.parse
from .base import BaseScanner
from .utils import safe_get

class XSSScanner(BaseScanner):
    def __init__(self, urls):
        super().__init__(urls)
        # 定义一个特征明显的 payload
        self.payload = "<script>alert('XSS_TEST')</script>"


    def scan_url(self, url):
        """对单个 URL 的所有参数进行测试"""
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        
        if not params:
            return

        # 遍历每个参数
        for key in params.keys():
            # 构造带 payload 的 URL
            # 逻辑：保留其他参数，只修改当前 key 的值为 payload
            new_query = params.copy()
            new_query[key] = [self.payload]
            
            # 重新组装 URL
            query_str = urllib.parse.urlencode(new_query, doseq=True)
            new_url = urllib.parse.urlunparse((
                parsed.scheme, parsed.netloc, parsed.path,
                parsed.params, query_str, parsed.fragment
            ))

            # 发送请求
            resp = safe_get(new_url)
            if resp and self.payload in resp.text:
                print(f"[*] 发现 XSS: {url} (参数: {key})")
                self.results.append({
                    "module": "XSSScanner",
                    "url": url,
                    "type": "Reflected XSS",
                    "param": key,
                    "payload": new_url
                })