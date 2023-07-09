import os, gridfs, pika, json
from flask import Flask, request, send_file
from flask_pymongo import PyMongo
from auth import validate
from auth_svc import access
from storage import util
from auth import validate
from bson.ObjectId import ObjectId

MONGO_URI="mongodb://host.minikube.internal:27017/videos"

app = Flask(__name__)

mongo_video = PyMongo(app,
                      uri=MONGO_URI)

mongo_mp3 = PyMongo(app,
                      uri=MONGO_URI.replace('videos','mp3s'))

fs_video = gridfs.Gridfs(mongo_video.db)
fs_mp3 = gridfs.Gridfs(mongo_mp3.db)

connection = pika.BlockingConnection(pika.ConnectionParameters("rabbitmq"))
channel = connection.channel

@app.route('/login', methods=['POST'])
def login():
    token, err = access.login(request)
    if not err:
        return token
    else:
        return err

@app.route('/upload', methods=['POST'])
def upload():
    access, err = validate.token(request)

    if err:
        return err

    access = json.load(access)
    if access["admin"]:
        if len(request.files) > 1 or len(request.files) < 1:
            return "exactly 1 file required",400

        for _, f in request.files.items():
            err = util.upload(f, fs_video, channel, access)

            if err:
                return err

        return 'success',200

    else:
        return "not authorized",401

@app.route('/download', methods=['GET'])
def download():
    access, err = validate.token(request)

    if err:
        return err

    access = json.loads(access)

    if access['admin']:
        fid_string = request.args.get('fid')

        if not fid_string:
            return "fid is required",400

        try:
            out = fs_mp3.get(ObjectId(fid_string))
            return send_file(out, download_name=f"{fid_string}.mp3")
        except Exception as err:
            print(err)
            return "internal server error",500


    return "not authorized",401


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080)
