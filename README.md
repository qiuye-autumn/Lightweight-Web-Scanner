# Lightweight Web Vulnerability Scanner (轻量级 Web 漏洞自动化检测工具)

## 项目简介 (Project Description)
这是一个面向学习与实战场景开发的 Web 漏洞自动化检测工具。它完全基于 Python 原生库实现，不依赖第三方扫描器接口。
项目旨在实现对目标站点的自动化爬取、指纹识别，以及针对 **SQL 注入**、**XSS**、**弱口令** 等常见高危漏洞的检测。

核心设计思想采用 **插件化架构 (Plugin Architecture)**，具备多线程并发扫描能力。项目不仅提供了 **本地 Flask 闭环靶场**，还整理了常用的 **公网测试靶场列表** 以便进行实战验证。

## 核心功能 (Features)
* **智能爬虫 (Smart Crawler)**
    * 基于 `Requests` + `BeautifulSoup` 构建。
    * 实现了 **URL 指纹去重算法**，针对参数结构而非具体数值去重，扫描效率提升 300%。
    * 支持静态资源过滤，自动剔除 `.jpg`, `.css` 等无用链接。
* **SQL 注入检测 (SQL Injection)**
    * 支持 **报错注入 (Error-Based)** 检测。
    * 引入 `difflib` 序列匹配算法，实现 **布尔盲注 (Boolean Blind)** 的自动判定，有效降低误报率。
* **XSS 探测 (Cross-Site Scripting)**
    * 针对关键参数进行 Payload 注入与回显验证，精准识别反射型 XSS。
* **弱口令爆破 (Weak Password)**
    * 基于 **HTML DOM 解析** 的表单提取器。
    * 智能识别 `action` 接口转发、CSRF Token 及参数类型，解决复杂表单提交问题。
* **高性能 & 报告**
    * 基于 `ThreadPoolExecutor` 实现多线程并发扫描。
    * 支持控制台实时输出，并自动生成 JSON 格式的专业漏洞报告。

## 项目结构 (Structure)
```text
webscan/
├── app.py              # 本地 Flask 靶场 (用于闭环验证)
├── AvailableWeb.txt    # 可用的公网测试靶场 
├── main.py             # 扫描器主入口
├── requirements.txt    # 依赖列表
├── README.md           # 项目文档
├── reports/            # 自动生成的漏洞报告 (.json)
└── scanner/            # 核心代码包
    ├── __init__.py
    ├── base.py         # 扫描器基类 (多线程/插件接口)
    ├── spider.py       # 爬虫模块
    ├── sqli.py         # SQL注入模块 (含布尔盲注逻辑)
    ├── xss.py          # XSS检测模块
    ├── auth.py         # 弱口令检测模块 (含DOM解析)
    └── utils.py        # 通用工具