import json
from flask import Flask, Response, stream_with_context
from flask_restful import Resource, Api
from gevent.pywsgi import WSGIServer


def encode_data(out):
    delay, data = out
    return bytes(str(delay), encoding="utf-8") + b',' + bytes(data, encoding="utf-8")

class Server():

    def __init__(self, path, offset=0):
        self._frames = []
        self.load_stream(path, offset)

    def load_stream(self, path, offset):
        stream_data = json.load(open(path))
        print(offset, type(offset))
        self._frames = stream_data['stdout'][offset:]

    @property
    def num_frames(self):
        return len(self._frames)

    def get_frame(self, num):
        delay, data = self._frames[num % self.num_frames]
        return delay, data


class StreamResource(Resource):

    def __init__(self, server: Server, num_frames: int):
        print("Initialised the Stream Resource")
        self.server = server
        self.num_frames = num_frames

    def get(self):
        def generate_frame():
            for i in range(self.num_frames):
                yield encode_data(self.server.get_frame(i))

        return Response(stream_with_context(generate_frame()), mimetype='text/plain')


class NonStreamResource(Resource):

    def __init__(self, server: Server, num_frames: int):
        print("Initialised the NonStream Resource")
        self.server = server
        self.num_frames = num_frames

    # Warning this does not work
    def get(self):
        for i in range(self.num_frames):
            return self.server.get_frame(i)


def main():
    parrot_json = 'asciicast-113643.json'
    s = Server(path=parrot_json, offset=19)
    num_frames=1000
    app = Flask(__name__)
    api = Api(app)
    cfg = {
        'server': s,
        'num_frames': num_frames
    }
    api.add_resource(StreamResource, '/stream', resource_class_kwargs=cfg)
    stream_server = WSGIServer(("localhost", 8000), app)
    stream_server.serve_forever()


if __name__ == '__main__':
    main()
