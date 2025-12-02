# app.py
from flask import Flask, request, render_template_string, redirect, url_for

app = Flask(__name__)

# ==========================================
# 首页 (爬虫入口)
# ==========================================
@app.route('/')
def index():
    return """
    <h1>Vulnerable Demo Site</h1>
    <ul>
        <li><a href="/product?id=1">Product Page (SQL Injection)</a></li>
        <li><a href="/search?q=test">Search Page (XSS)</a></li>
        <li><a href="/login">Login Page (Weak Password)</a></li>
    </ul>
    """

# ==========================================
# 1. SQL 注入靶点 (模拟布尔盲注 & 报错注入)
# ==========================================
@app.route('/product')
def product():
    product_id = request.args.get('id', '')
    
    # 【模拟报错注入】: 如果有单引号，假装报错
    if "'" in product_id:
        return "Error: You have an error in your SQL syntax...", 500

    # 【模拟布尔盲注】: 
    # 扫描器会发送: id=1 AND 1=1 (真) 和 id=1 AND 1=2 (假)
    
    # 模拟数据库查询逻辑
    # 如果包含 "AND 1=2"，模拟查询失败
    if "AND 1=2" in product_id:
        return "<h1>Product Not Found</h1><p>The product you are looking for does not exist.</p>"
    
    # 如果包含 "AND 1=1" 或者只是 "1"，模拟查询成功
    if "1" in product_id:
        return """
        <h1>iPhone 15 Pro</h1>
        <p>Price: $999</p>
        <p>Description: The best iPhone ever.</p>
        """
    
    return "<h1>Product Not Found</h1>"

# ==========================================
# 2. XSS 靶点 (反射型)
# ==========================================
@app.route('/search')
def search():
    query = request.args.get('q', '')
    # 【漏洞点】: 直接将 query 拼接回 HTML，且使用 |safe 告诉 Flask 不要转义
    template = f"""
    <h1>Search Results</h1>
    <p>You searched for: {query}</p> 
    """
    return template 

# ==========================================
# 3. 弱口令靶点 (模拟 login -> userinfo 转发)
# ==========================================
@app.route('/login', methods=['GET'])
def login():
    return """
    <h1>Login</h1>
    <form action="/userinfo" method="POST">
        Username: <input type="text" name="username"><br>
        Password: <input type="password" name="password"><br>
        <input type="submit" value="Login">
    </form>
    """

@app.route('/userinfo', methods=['POST'])
def userinfo():
    # 获取表单数据
    user = request.form.get('username')
    pwd = request.form.get('password')
    
    # 硬编码的弱口令
    if user == 'admin' and pwd == '123456':
        return "<h1>Login Success!</h1> <a href='/logout'>Logout</a>"
    else:
        return "<h1>Login Failed</h1><p>Invalid credentials.</p>"

if __name__ == '__main__':
    # 启动在 5000 端口
    print("[*] Demo靶场正在运行: http://127.0.0.1:5000")
    app.run(debug=True, port=5000)