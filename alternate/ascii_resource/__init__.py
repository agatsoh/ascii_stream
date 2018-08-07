import logging
import json
from flask import Flask, Response, stream_with_context
from flask import request
from microraiden.proxy.resources import Expensive

log = logging.getLogger(__name__)


def encode_data(out):
    delay, data = out
    return bytes(str(delay), encoding="utf-8") + b',' + bytes(data, encoding="utf-8")


class ProcessFrame:

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


class StreamResource(Expensive):

    def __init__(self):
        log.info("Initialised the Stream Resource")
        parrot_json = 'asciicast-113643.json'
        self.pf = ProcessFrame(parrot_json, offset=19)
        self.num_frames = 1000

    def get(self, url: str, param:str):
        log.info('Resource requested: {} with param "{}"'.format(request.url, param))

        def generate_frame():
            for i in range(self.num_frames):
                yield encode_data(self.pf.get_frame(i))

        return Response(stream_with_context(generate_frame()), mimetype='text/plain')


__all__ = (
    ProcessFrame,
    StreamResource
)