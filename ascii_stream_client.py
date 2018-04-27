import requests


with requests.get('http://localhost:8000/stream', stream=True) as r:
    for line in r.iter_lines(decode_unicode=True):
        if line:
            print(line)

