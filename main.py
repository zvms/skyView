# 每个用户id，生成一个token，存入db
# 用户上传图片时，需要携带token，验证token是否有效
# 验证token有效，接收图片
# 图片处理：
# 1. 保存图片
# 2. 鉴定是否为合法图片
# 3. 生成缩略图，压缩原图至一定大小
# 4. 生成md5
# 5. 使用ai生成描述关键词
# 6. 多端储存图片
# 7. 保存图片元信息到db
# 8. 删除本地图片
# 返回图片信息

import os
import sys
import time
import json
import hashlib

from flask import Flask, request, jsonify, send_from_directory, redirect, Response
from flask_cors import CORS
from werkzeug.utils import secure_filename

from db import *
from process import *
from storage import *
import config

import ssl
		
ssl._create_default_https_context = ssl._create_unverified_context()

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['UPLOAD_FOLDER'] = config.UPLOAD_FOLDER

# GET /user/:id/image 获取某个用户的所有图片列表
@app.route('/user/<userId>/image', methods=['GET'])
def getUserImageById(userId):
    # 检查用户token的权限是否为 1 - 管理员
    token = request.args.get('token')
    if token == None:
        return jsonify({
            "code": 400,
            "message": "未上传token"
        })
    thisUserId = getUserIdByToken(token)
    if thisUserId == None:
        return jsonify({
            "code": 401,
            "message": "token无效"
        })
    permission = getUserPermission(thisUserId)
    if permission != 1 and thisUserId != userId:
        return jsonify({
            "code": 403,
            "message": "权限不足"
        })
    pageSize = request.args.get('pageSize', default=config.PAGE_SIZE, type=int)
    pageNum = request.args.get('pageNum', default=config.PAGE_NUM, type=int)
    images = getUserImages(userId, pageSize, pageNum)
    return jsonify({
        "code": 200,
        "message": "获取图片列表成功",
        "data": {
            "images": images
        }
    })

# GET /user/image 获取当前用户的所有图片列表
@app.route('/user/image', methods=['GET'])
def getUserImage():
    token = request.args.get('token')
    if token == None:
        return jsonify({
            "code": 400,
            "message": "未上传token"
        })
    userId = getUserIdByToken(token)
    if userId == None:
        return jsonify({
            "code": 401,
            "message": "token无效"
        })
    pageSize = request.args.get('pageSize', default=config.PAGE_SIZE, type=int)
    pageNum = request.args.get('pageNum', default=config.PAGE_NUM, type=int)
    images = getUserImages(userId, pageSize, pageNum)
    return jsonify({
        "code": 200,
        "message": "获取图片列表成功",
        "data": {
            "images": images
        }
    })

# GET /image/:id 获取图片信息
@app.route('/image/<imageId>', methods=['GET'])
def getImageById(imageId):
    token = request.args.get('token')
    if token == None:
        return jsonify({
            "code": 400,
            "message": "未上传token"
        })
    userId = getUserIdByToken(token)
    if userId == None:
        return jsonify({
            "code": 401,
            "message": "token无效"
        })
    # 获取图片信息
    image = getImageInfo(imageId)
    print(imageId)
    if image == None:
        return jsonify({
            "code": 404,
            "message": "图片不存在"
        })
    return jsonify({
        "code": 200,
        "message": "获取图片信息成功",
        "data": {
            "image": image
        }
    })

# POST /user/image 上传图片
@app.route('/user/image', methods=['POST'])
def uploadImage():
    token = request.form['token']
    if token == None:
        return jsonify({
            "code": 400,
            "message": "未上传token"
        })
    userId = getUserIdByToken(token)
    if userId == None:
        return jsonify({
            "code": 401,
            "message": "token无效"
        })
    image = request.files['image']
    if image == None:
        return jsonify({
            "code": 400,
            "message": "未上传图片"
        })
    # 保存图片
    filename = randomString() + '.jpg'
    path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    image.save(path)
    # 鉴定是否为合法图片
    if config.CHECK_ENABLED and (not checkImg(path)):
        return jsonify({
            "code": 400,
            "message": "非法图片"
        })
    # 压缩图片
    compress(path, path, config.MAX_SIZE)
    # print("Started uploading.")
    # 上传图片
    fileId = upload(path)
    if fileId == None:
        return jsonify({
            "code": 500,
            "message": "上传图片失败"
        })
    # print("Uploaded.")
    # 新增图片信息
    md5 = generateMD5(path)
    keywords = ""
    if request.form.get('keywords') != None and config.KEYWORDS_GENERATE_ENABLED:
        keywords = generateKeywords(fileId)
    timestamp = int(time.time())
    addImage(fileId, userId, md5, keywords, timestamp)
    # 添加到用户图片列表
    addUserImage(userId, fileId)
    # 删除本地图片
    os.remove(path)
    # 返回图片信息
    return jsonify({
        "code": 200,
        "message": "上传图片成功",
        "data": {
            "url": config.SERVERURL + "/getimage/" + fileId,
            "author": userId,
            "md5": md5,
            "keywords": keywords,
            "timestamp": timestamp
        }
    })

# GET /image/:fileId 获取图片流
@app.route('/getimage/<fileId>')
def getImage(fileId):
    token = request.args.get('token')
    if token == None:
        return jsonify({
            "code": 400,
            "message": "未上传token"
        })
    userId = getUserIdByToken(token)
    if userId == None:
        return jsonify({
            "code": 401,
            "message": "token无效"
        })
    response = getBBImage(fileId)
    if response.status_code == 200:
        def generate():
            for chunk in response.iter_content(chunk_size=1024):
                yield chunk
        return Response(generate(), mimetype='application/octet-stream')
    else:
        return Response(response.text, status=response.status_code)

# GET /user/getToken 获取用户token
@app.route('/user/getToken', methods=['GET'])
def getToken():
    superAdminToken = request.args.get('superAdminToken')
    if(superAdminToken == None or superAdminToken != config.SUPERADMINTOKEN):
        return jsonify({
            "code": 403,
            "message": "超级管理员令牌错误"
        })
    userId = request.args.get('userId')
    if userId == None:
        return jsonify({
            "code": 400,
            "message": "未上传userId"
        })
    permission = request.args.get('permission')
    if permission == None:
        return jsonify({
            "code": 400,
            "message": "未上传permission"
        })
    token = getUserToken(userId, permission)
    return jsonify({
        "code": 200,
        "message": "获取token成功",
        "data": {
            "token": token
        }
    })

# root: redirect to https://www.amzcd.top/posts/zvmsapi/#zvms_skyview_api
@app.route('/', methods=['GET'])
def root():
    return redirect("https://www.amzcd.top/posts/zvmsapi/#zvms_skyview_api", code=302)

# DELETE /image/:id 删除图片
# since XH has plenty of storage, we don't need to delete images

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=6666, debug=True)

from gevent import pywsgi

if __name__ == '__main__':
    server = pywsgi.WSGIServer((config.host, config.port), app)
    server.serve_forever()