import hashlib

def get_md5(url):
    if isinstance(url,str):
        url = url.encode("utf-8")
    m = hashlib.md5()
    m.update(url)
    return m.hexdigest()

if __name__ == '__main__':
    g = get_md5('https://www.baidu.com'.encode('utf-8'))
    print(g)