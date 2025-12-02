# scanner/base.py
import concurrent.futures

class BaseScanner:
    def __init__(self, urls, max_threads=10):
        """
        初始化扫描器
        :param urls: 经过爬虫去重后的 URL 列表
        """
        self.urls = urls
        self.max_threads = max_threads
        self.results = []

    def run(self):
        print(f"\n[+] 开始运行 {self.__class__.__name__} (线程数: {self.max_threads})...")
        
        # 使用线程池并发执行
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_threads) as executor:
            # 提交所有任务到线程池
            futures = [executor.submit(self.scan_url, url) for url in self.urls]
            
            # 等待所有任务完成
            concurrent.futures.wait(futures)
        
    def scan_url(self, url):
        raise NotImplementedError("子类必须实现 scan_url(url) 方法")