# 数据库操作相关

import sqlite3
import os
import sys
import json
import config
import re

conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
c = conn.cursor()

# 随机生成token
def generateToken():
    return os.urandom(24).hex()

# 图片模型
# url: 图片地址
# author: 上传者学号
# md5: 图片md5
# keywords: 图片关键词
# timestamp: 上传时间戳

# 创建图片表
c.execute('''CREATE TABLE IF NOT EXISTS images
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    author TEXT NOT NULL,
    md5 TEXT NOT NULL,
    keywords TEXT NOT NULL,
    timestamp INTEGER NOT NULL)''')

# 用户模型
# id: 用户id
# token: 用户token
# permission: 用户权限 [0, 1] [普通用户（只能看自己）, 管理员（看所有人）]
# images: 用户图片url列表

# 创建用户表
c.execute('''CREATE TABLE IF NOT EXISTS users
    (id TEXT PRIMARY KEY,
    token TEXT NOT NULL,
    permission INTEGER NOT NULL,
    images TEXT NOT NULL)''')

# 创建用户
def createUser(userId, permission):
    token = generateToken()
    images = []
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (userId, token, permission, json.dumps(images)))
    conn.commit()
    return token

# 获取用户token
def getUserToken(userId, permission):
    # 如果用户不存在，创建用户
    c.execute("SELECT * FROM users WHERE id=?", (userId,))
    user = c.fetchone()
    if user == None:
        return createUser(userId, permission)
    else:
        # generate a new token and update permission
        token = generateToken()
        c.execute("UPDATE users SET token=?, permission=? WHERE id=?", (token, permission, userId))
        conn.commit()
        return token

# 根据token获取用户id
def getUserIdByToken(token):
    c.execute("SELECT * FROM users WHERE token=?", (token,))
    user = c.fetchone()
    if user == None:
        return None
    else:
        return user[0]

# 获取用户权限
def getUserPermission(userId):
    c.execute("SELECT * FROM users WHERE id=?", (userId,))
    user = c.fetchone()
    if user == None:
        return None
    else:
        return user[2]

# 新增图片信息
def addImage(url, author, md5, keywords, timestamp):
    c.execute("INSERT INTO images VALUES (?, ?, ?, ?, ?, ?)", (None, url, author, md5, keywords, timestamp))
    conn.commit()

# 添加到用户图片列表
def addUserImage(userId, url):
    c.execute("SELECT * FROM users WHERE id=?", (userId,))
    user = c.fetchone()
    if user == None:
        return False
    else:
        images = json.loads(user[3])
        images.append(url)
        c.execute("UPDATE users SET images=? WHERE id=?", (json.dumps(images), userId))
        conn.commit()
        return True 

def url2id(url):
    # https://xhfs0.ztytech.com/CA107011/f637d39729cd40648ce9e5a05a66f7ff.jpg
    # -> xhfs0_f637d39729cd40648ce9e5a05a66f7ff
    # 规律：xhfs<数字>_文件名无后缀
    return re.sub(r'https://xhfs(\d).ztytech.com/CA107011/', r'xhfs\1_', url).replace('.jpg', '')

def id2url(pid):
    # xhfs0_f637d39729cd40648ce9e5a05a66f7ff
    # -> https://xhfs0.ztytech.com/CA107011/f637d39729cd40648ce9e5a05a66f7ff.jpg
    # 规律：xhfs<数字>_文件名无后缀
    return re.sub(r'xhfs(\d)_', r'https://xhfs\1.ztytech.com/CA107011/', pid) + '.jpg'

# 获取用户所有图片列表
def getUserImages(userId, pageSize, pageNum):
    c.execute("SELECT * FROM users WHERE id=?", (userId,))
    user = c.fetchone()
    if user == None:
        return None
    else:
        images = json.loads(user[3])
        images = images[(pageNum - 1) * pageSize:pageNum * pageSize]
        l = []
        for image in images:
            l.append({"id": url2id(image), "url": image})
        return l

# 获取图片信息
def getImageInfo(pid):
    url = id2url(pid)
    c.execute("SELECT * FROM images WHERE url=?", (url,))
    image = c.fetchone()
    if image == None:
        return None
    else:
        return {
            "id": pid,
            "index": image[0],
            "url": image[1],
            "author": image[2],
            "md5": image[3],
            "keywords": image[4],
            "timestamp": image[5]
        }