from hmac import new
from urllib.parse import urlencode, quote
from base64 import b64encode
from hashlib import sha1
from time import time

def sign_url(uri):
    sign_key = b"gUtPzJFZch4ZyAGviiyH94P99lQ3pFdRTwpJWDlSGFfwgpr6ses5ALOxWHOIT7R1"
    mac = new(sign_key, digestmod=sha1)
    stamp = str(int(time() * 1000))
    
    message = uri[:min(255, len(uri))] + stamp
    mac.update(message.encode('utf-8'))
    
    md = quote(b64encode(mac.digest()))
    separator = '&' if '?' in uri else '?'
    
    return f"{uri}{separator}msgpad={stamp}&md={md}"