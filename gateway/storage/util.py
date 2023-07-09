import pika, json

def upload(f, fs, channel, access):
    try:
        fid = fs.put(f)

    except Exception as err:
        return "internal server error"


    message = {
        "video_fid":fid,
        "mp3_fid": None,
        "username":access["username"]
    }

    #put message on the queue
    try:
        channel.basic_publish(
            exchange="",
            routing_key="video",
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=pika.spec.PERSISTENT_DELIVER_MODE
            )
        )
    except:
        fs.delete(fid)
        return "internal server error",500

