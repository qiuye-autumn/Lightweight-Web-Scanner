# scanner/spider.py
from collections import deque
from urllib.parse import urljoin, urlparse, urldefrag
from bs4 import BeautifulSoup
from .utils import safe_get, get_url_fingerprint, is_static_resource

VALID_SCHEMES = ("http", "https")

class Spider:
    def __init__(self, base_url, max_pages=30):
        self.base = base_url.rstrip("/")
        self.max_pages = max_pages
        parsed = urlparse(self.base)
        self.domain = parsed.netloc.lower()

        # self.visited_urls 用于防止爬虫死循环 
        self.visited_urls = set() 
        # self.scanned_fingerprints 用于控制结果集 
        self.scanned_fingerprints = set() 

    def _normalize(self, url):
        """去掉 fragment、结尾斜杠等"""
        url, _ = urldefrag(url)
        return url.rstrip("/")

    def _is_valid(self, url):
        """判断是否为同域 http(s) 链接"""
        parsed = urlparse(url)
        if parsed.scheme.lower() not in VALID_SCHEMES:
            return False
        if parsed.netloc.lower() != self.domain:
            return False
        return True

    def _extract_links(self, url, html):
        """解析页面中的链接"""
        # 增加容错，防止 html 为 None
        if not html: return []
        
        soup = BeautifulSoup(html, "lxml")
        links = []
        for a in soup.find_all("a", href=True):
            href = a['href'].strip()
            if href.lower().startswith(("javascript:", "mailto:", "tel:", "#")):
                continue
            try:
                new_url = urljoin(url, href)
                new_url = self._normalize(new_url)
            except:
                continue
            
            if self._is_valid(new_url):
                links.append(new_url)
        return links

    def run(self):
        print("[*] 开始深度爬取…")

        queue = deque([self.base])
        result = []

        while queue and len(result) < self.max_pages:
            url = queue.popleft()

            # 1. 基础去重 
            if url in self.visited_urls:
                continue
            self.visited_urls.add(url)

            # 如果是图片、CSS等，直接跳过，不爬也不存
            if is_static_resource(url):
                # print(f"[-] 跳过静态资源: {url}")
                continue
            
            # 计算这个 URL 的指纹
            fp = get_url_fingerprint(url)
            
            # 如果这个结构（指纹）已经记录在案，就不加入 result 列表
            # 注意：虽然不加入 result，但我们可能还是需要爬取它以发现新链接(深度优先 vs 广度优先的取舍)
            
            is_new_structure = False
            if fp not in self.scanned_fingerprints:
                self.scanned_fingerprints.add(fp)
                result.append(url) # 只有新结构的 URL 才会被当作扫描目标
                is_new_structure = True
                print(f"  [+] 发现新结构: {url}")
            else:
                # print(f"  [.] 结构重复: {url}")
                pass

            # 发送请求
            resp = safe_get(url)
            if not resp:
                continue

            # 提取新链接加入队列
            links = self._extract_links(url, resp.text)
            for link in links:
                if link not in self.visited_urls:
                    queue.append(link)

        print(f"[+] 爬取完成，共扫描 {len(self.visited_urls)} 个链接，筛选出 {len(result)} 个不同结构的页面")
        return result