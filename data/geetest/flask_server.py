import sys, os
from flask import Flask, request
app = Flask(__name__)

sys.path.append(os.path.join(os.path.split(os.path.realpath(__file__))[0], '../util'))
import db

@app.route('/myapi/geetest', methods=['POST'])
def geetest():
    tracks = []
    data = request.data.decode("utf8")
    ps = data.split("|")
    for p in ps:
        p = p.replace("(","").replace(")","")
        ts = p.split(",")
        if len(ts) != 3:
            continue
        x = int(ts[0])
        y = int(ts[1])
        t = int(ts[2])
        tracks.append((x,y,t))

    track_list = []
    del tracks[0]

    index = 0
    x1,y1,t1 = (0,0,0)
    for p in tracks:
        x,y,t = p
        track_list.append((x-x1,y-y1,t-t1))
        x1,y1,t1 = p
        index += 1

    print(track_list)

    (x,y,t) = tracks[-1]
    loc = x
    mongo = db.connect_mongo()
    data = {
        "loc": loc,
        "track": track_list
    }
    mongo.raw.tyc_real_track.insert_one(data)
    mongo.close()
    return 'ok'

if __name__ == '__main__':
    app.run(port=8000)