# 数据库操作相关

import sqlite3
import os
import sys
import json
import config
import re

conn = sqlite3.connect(config.DB_PATH, check_same_thread=False)
c = conn.cursor()

# Random token generator
def generateToken():
    return os.urandom(24).hex()

# Picture model
# url: Picture url
# author: Uploader id
# md5: Image md5
# keywords: Keywords
# timestamp: Timestamp

# Create image table
c.execute('''CREATE TABLE IF NOT EXISTS images
    (id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    author TEXT NOT NULL,
    md5 TEXT NOT NULL,
    keywords TEXT NOT NULL,
    timestamp INTEGER NOT NULL)''')

# User model
# id: User id
# token: User token
# permission: User permission
# images: User images

# Create user table
c.execute('''CREATE TABLE IF NOT EXISTS users
    (id TEXT PRIMARY KEY,
    token TEXT NOT NULL,
    permission INTEGER NOT NULL,
    images TEXT NOT NULL)''')

# Create user
def createUser(userId, permission):
    token = generateToken()
    images = []
    c.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (userId, token, permission, json.dumps(images)))
    conn.commit()
    return token

# Get user token
def getUserToken(userId, permission):
    # If user not exists, create a new user
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

# Get user id by token
def getUserIdByToken(token):
    c.execute("SELECT * FROM users WHERE token=?", (token,))
    user = c.fetchone()
    if user == None:
        return None
    else:
        return user[0]

# Get user permission
def getUserPermission(userId):
    c.execute("SELECT * FROM users WHERE id=?", (userId,))
    user = c.fetchone()
    if user == None:
        return None
    else:
        return user[2]

# Add image
def addImage(url, author, md5, keywords, timestamp):
    c.execute("INSERT INTO images VALUES (?, ?, ?, ?, ?, ?)", (None, url, author, md5, keywords, timestamp))
    conn.commit()

# Add to user image list
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
    # Rule: xhfs<digest>_no suffix
    return re.sub(r'https://xhfs(\d).ztytech.com/CA107011/', r'xhfs\1_', url).replace('.jpg', '')

def id2url(pid):
    # xhfs0_f637d39729cd40648ce9e5a05a66f7ff
    # -> https://xhfs0.ztytech.com/CA107011/f637d39729cd40648ce9e5a05a66f7ff.jpg
    # Rule: xhfs<digest>_ -> https://xhfs<digest>.ztytech.com/CA107011/<digest>.jpg
    return re.sub(r'xhfs(\d)_', r'https://xhfs\1.ztytech.com/CA107011/', pid) + '.jpg'

# Get user images
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

# Get image info
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
