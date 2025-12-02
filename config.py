# config.py

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

REQUEST_TIMEOUT = 8         # 每次请求最大等待时间
MAX_DEPTH = 2               # 爬虫深度

# ---- SQL 注入检测 payload ----
SQLI_ERROR_PAYLOADS = [
    "'", "\"", "''", "`"
]

# 时间注入（盲注）
SQLI_TIME_PAYLOADS = [
    "' AND SLEEP(3)-- ",
    "\" AND SLEEP(3)-- ",
]

# 布尔注入
SQLI_BOOL_PAYLOADS = [
    "' AND '1'='1",
    "' AND '1'='2",
]

KEY_SQL_ERRORS = [
    "SQL syntax",
    "mysql_fetch",
    "ORA-01756",
    "You have an error in your SQL",
    "unterminated quoted string",
    "Warning: mysql_",
]
