# skyView

A high-performance picture bed for zvms.

## dependencies

```bash
pip install -r requirements.txt
```

PIL is also required.

International network environment is needed. (if you need to use huggingface)

## Run

```bash
python3 main.py
```

## Configure

You need to create a `config.py`. The content is as follows:

```python
# config.py
# The configuration file for skyView
# config.py - skyView Configuration File

# Storage Method
STORAGE = "..." # Storage Method (Backblaze, XueHai, Local)
XUEHAI_URL = "..." # XueHai API URL
KEYID = "..." # Backblaze KeyID
KEYNAME = "..." # Backblaze KeyName
APPKEY = "..." # Backblaze AppKey
BASEURL = "..." # Backblaze BaseURL
CFURL = "..." # Cloudflare Proxy URL

# Database Path
DB_PATH = "db.sqlite3" # Database Path

# 图片参数设定
UPLOAD_FOLDER = "..." # Cache Folder
PAGE_SIZE = 10 # Default Page Size
PAGE_NUM = 1 # Default Page Number
MAX_SIZE = 3 * 1024 * 1024 # Max Size of Image, otherwise it will be compressed

# Congiguration of content moderation
CHECK_ENABLED = False # Whether to enable content moderation
KEYWORDS_GENERATE_ENABLED = False # Whether to enable keywords generation
HF_ENABLED = False # Whether to enable huggingface
HF_URL = "..." # Whether to enable huggingface

# Server Configuration
SERVERURL = "..." # Server URL
SUPERADMINTOKEN = "..." # Super Admin Token
host = "0.0.0.0" # Server Host
port = 6666 # Server Port
```

## document

see [https://www.amzcd.top/posts/zvmsapi/#zvms_skyview_api](https://www.amzcd.top/posts/zvmsapi/#zvms_skyview_api).
