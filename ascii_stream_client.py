import requests

s = requests.Session()

with s.get('http://localhost:8000/stream', stream=True) as r:
    import pudb; pudb.set_trace()
    if r.status_code == requests.codes.OK:
        for line in r.iter_lines(decode_unicode=True):
            if line:
                print(line)

