# scanner/auth.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from .base import BaseScanner

class WeakPwdScanner(BaseScanner):
    def __init__(self, urls):
        super().__init__(urls)
        # 关键词用于初筛，只对包含这些词的 URL 进行深度表单解析
        self.login_keywords = ['login', 'sign', 'admin', 'manage']
        
        # 弱口令字典
        self.usernames = ['admin', 'test', 'root']
        self.passwords = ['123456', 'test', '12345678', 'password', 'admin123']

    def _parse_form(self, html, base_url):
        """
        核心逻辑：解析 HTML 中的所有表单，提取关键信息
        返回一个列表，每个元素包含：action URL, method, inputs字典
        """
        soup = BeautifulSoup(html, 'lxml')
        forms = soup.find_all('form')
        extracted_forms = []

        for form in forms:
            # 1. 获取提交地址 (Action)
            action = form.get('action')
            if action:
                # 处理相对路径，如 action="userinfo.php" -> http://site.com/userinfo.php
                target_url = urljoin(base_url, action)
            else:
                # 如果 action 为空，通常提交给自己
                target_url = base_url

            # 2. 获取提交方式 (Method)
            method = form.get('method', 'get').lower()

            # 3. 提取所有 input 标签
            inputs = []
            for input_tag in form.find_all('input'):
                input_name = input_tag.get('name')
                input_type = input_tag.get('type', 'text').lower()
                input_value = input_tag.get('value', '')
                
                if not input_name:
                    continue
                
                inputs.append({
                    "name": input_name,
                    "type": input_type,
                    "value": input_value
                })
            
            extracted_forms.append({
                "target_url": target_url,
                "method": method,
                "inputs": inputs
            })
            
        return extracted_forms

    def scan_url(self, url):
        # 初筛 
        if not any(k in url.lower() for k in self.login_keywords):
            return

        # 1. 获取页面内容
        try:
            # 允许重定向，用于最终的登录页 HTML
            res = requests.get(url, timeout=5, verify=False)
        except:
            return

        # 2. 解析表单
        forms = self._parse_form(res.text, url)
        if not forms:
            return

        # 3. 对每一个发现的表单进行爆破
        for form in forms:
            self._crack_form(form, url)

    def _crack_form(self, form, original_url):
        """
        针对单个表单进行字典攻击
        """
        target_url = form['target_url']
        method = form['method']
        inputs = form['inputs']

        # 寻找账号和密码字段
        user_field = None
        pass_field = None
        other_fields = {}

        for inp in inputs:
            # 智能识别：如果是 password 类型，肯定是密码框
            if inp['type'] == 'password':
                pass_field = inp['name']
            # 智能识别：如果名字里带 user/email/login，可能是账号框
            elif not user_field and any(x in inp['name'].lower() for x in ['user', 'name', 'email', 'login', 'id']):
                user_field = inp['name']
            else:
                # 其他字段（如 hidden token, submit button），保持默认值
                other_fields[inp['name']] = inp['value']

        # 如果找不到关键字段，就没法爆破
        if not user_field or not pass_field:
            return

        # print(f"[*] 发现登录表单: {original_url} -> 提交至 {target_url} (账号字段: {user_field}, 密码字段: {pass_field})")

        # 开始字典攻击
        for user in self.usernames:
            for pwd in self.passwords:
                # 构造 Payload
                data = other_fields.copy()
                data[user_field] = user
                data[pass_field] = pwd

                try:
                    if method == 'post':
                        # 禁止自动跳转，以便检测 302
                        resp = requests.post(target_url, data=data, timeout=5, allow_redirects=False, verify=False)
                    else:
                        resp = requests.get(target_url, params=data, timeout=5, allow_redirects=False, verify=False)

                    # 判定逻辑
                    # 1. 状态码 302/301 跳转
                    # 2. 响应包里有 "logout", "success", "dashboard" 等词
                    success_keywords = ["logout", "sign out", "log out", "注销", "退出"]
                    
                    is_success = False
                    if resp.status_code in [302, 301]:
                        # 检查跳转地址，有些网站失败也会跳转到 error.php，需要注意
                        # 这里简单判定：只要跳转了，就值得警报
                        is_success = True
                    elif any(k in resp.text.lower() for k in success_keywords):
                        is_success = True

                    if is_success:
                        print(f"[*] 发现弱口令: {original_url}")
                        print(f"    [+] 提交地址: {target_url}")
                        print(f"    [+] 账号: {user}")
                        print(f"    [+] 密码: {pwd}")

                        self.results.append({
                            "module": "WeakPwdScanner",
                            "url": original_url,
                            "type": "Weak Password",
                            "target_url": target_url,
                            "account": user,
                            "password": pwd
                        })
                        return # 爆破成功一个即可
                        

                except Exception as e:
                    pass