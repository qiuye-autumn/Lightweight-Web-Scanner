# main.py
import sys
import json
import time
import os

# 1. 获取 main.py 文件所在的绝对路径
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 确保能找到 scanner 包
sys.path.append(BASE_DIR)

from scanner.spider import Spider
from scanner.sqli import SQLiScanner
from scanner.xss import XSSScanner
from scanner.auth import WeakPwdScanner

def main():
    target = input("请输入扫描目标网站: ")
    if not target.startswith("http"):
        target = "http://" + target

    print(f"[+] 开始扫描: {target}")

    # --- 爬虫阶段 ---
    spider = Spider(target)
    urls = spider.run()

    print(f"[+] 爬取结束，准备进行漏洞扫描 (共 {len(urls)} 个目标)")

    # --- 漏洞扫描阶段 ---
    scanners = [
        SQLiScanner(urls),
        XSSScanner(urls),
        WeakPwdScanner(urls),
    ]

    all_findings = []

    # --- 统一调度 ---
    for scanner in scanners:
        name = scanner.__class__.__name__
        print(f"\n[+] 正在运行模块: {name}")
        try:
            scanner.run()
            # 收集结果
            if hasattr(scanner, 'results'):
                all_findings.extend(scanner.results)
        except Exception as e:
            print(f"[-] 模块 {name} 运行出错: {e}")

    # --- 生成报告 (路径修复版) ---
    print("\n" + "="*30)
    print(f"[+] 扫描完成，共发现 {len(all_findings)} 个漏洞")
    
    if all_findings:
        # 1. 锁定 reports 文件夹的绝对路径 (webscan/reports)
        output_dir = os.path.join(BASE_DIR, "reports")
        
        # 2. 如果不存在就创建
        if not os.path.exists(output_dir):
            try:
                os.makedirs(output_dir)
            except Exception as e:
                print(f"[-] 创建目录失败: {e}，尝试保存到当前目录")
                output_dir = "."

        # 3. 生成文件名
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"result_{timestamp}.json"
        
        # 4. 组合最终路径
        filepath = os.path.join(output_dir, filename)
        
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(all_findings, f, indent=4, ensure_ascii=False)
            print(f"[+] 漏洞报告已生成: {filepath}")
        except Exception as e:
            print(f"[-] 报告写入失败: {e}")
    else:
        print("[+] 未发现明显漏洞，未生成报告。")

if __name__ == "__main__":
    main()