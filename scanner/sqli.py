# scanner/sqli.py
import urllib.parse
from .utils import safe_get
import difflib
from .base import BaseScanner

class SQLiScanner(BaseScanner):
    def __init__(self, urls):
        # 调用父类的初始化方法
        super().__init__(urls)

        # 定义 SQL 错误关键字，用于报错注入检测
        self.error_keywords = [
            "SQL syntax", "mysql_fetch", "check the manual", "You have an error in your SQL",
            "Warning: mysql_", "unclosed quotation mark", "Microsoft OLE DB Provider for ODBC Drivers"
        ]

    def _get_params(self, url):
        """解析 URL 中的参数，返回字典"""
        parsed = urllib.parse.urlparse(url)
        params = urllib.parse.parse_qs(parsed.query)
        return params

    def _construct_url(self, url, param_key, new_value):
        """辅助函数：替换 URL 中的某个参数值"""
        parsed = urllib.parse.urlparse(url)
        query_dict = urllib.parse.parse_qs(parsed.query)
        
        # 替换参数值 (注意 parse_qs 返回的是列表)
        query_dict[param_key] = [new_value]
        
        # 重新组合 URL
        new_query = urllib.parse.urlencode(query_dict, doseq=True)
        new_url = urllib.parse.urlunparse((
            parsed.scheme, parsed.netloc, parsed.path,
            parsed.params, new_query, parsed.fragment
        ))
        return new_url

    def _check_similarity(self, text1, text2):
        """计算两个页面文本的相似度 (0.0 - 1.0)"""
        # 如果任何一个页面为空，直接返回 0
        if not text1 or not text2:
            return 0.0
        # quick_ratio 效率很高，适合扫描器
        return difflib.SequenceMatcher(None, text1, text2).quick_ratio()

    def scan_boolean(self, url, param_key, original_val, original_html):
        """
        布尔盲注检测逻辑
        """
        # 构造 True Payload (逻辑真)
        # 注意：这里简化处理，假设是数字型注入。如果是字符型可能需要 ' AND '1'='1
        val_true = f"{original_val} AND 1=1"
        url_true = self._construct_url(url, param_key, val_true)
        resp_true = safe_get(url_true)

        # 构造 False Payload (逻辑假)
        val_false = f"{original_val} AND 1=2"
        url_false = self._construct_url(url, param_key, val_false)
        resp_false = safe_get(url_false)

        if not resp_true or not resp_false:
            return False

        # 计算相似度
        # 1. True 页面应该和原始页面很像 (比如相似度 > 0.95)
        sim_true = self._check_similarity(original_html, resp_true.text)
        
        # 2. False 页面应该和原始页面差别较大 (比如相似度 < 0.90)
        sim_false = self._check_similarity(original_html, resp_false.text)

        # 判定: 真页面像原图，且假页面不像原图
        if sim_true > 0.95 and sim_false < 0.90:
            return f"Boolean Blind SQLi (Key: {param_key})"
        
        return False

    def scan_error(self, url, param_key, original_val):
        """
        报错注入检测逻辑
        """
        # 简单的加单引号测试
        val_err = f"{original_val}'"
        url_err = self._construct_url(url, param_key, val_err)
        resp = safe_get(url_err)
        
        if resp:
            for keyword in self.error_keywords:
                if keyword in resp.text:
                    return f"Error-Based SQLi (Key: {param_key})"
        return False

    def scan_url(self, url):
        params = self._get_params(url)
        if not params: return
            
        # 请求原始页面
        resp_orig = safe_get(url)
        if not resp_orig: return
        original_html = resp_orig.text

        # 遍历参数测试
        for param_key in params.keys():
            original_val = params[param_key][0]

            # 1. 测布尔
            vuln_bool = self.scan_boolean(url, param_key, original_val, original_html)
            if vuln_bool:
                print(f"[!] {vuln_bool} -> {url}")
                self.results.append({
                    "module": "SQLiScanner",
                    "url": url,
                    "type": vuln_bool,
                    "param": param_key,
                    "payload_hint": f"AND 1=2"
                })
                continue 

            # 2. 测报错
            vuln_err = self.scan_error(url, param_key, original_val)
            if vuln_err:
                print(f"[!] {vuln_err} -> {url}")
                self.results.append({
                    "module": "SQLiScanner",
                    "url": url,
                    "type": vuln_err,
                    "param": param_key,
                    "payload_hint": f"'"
                })