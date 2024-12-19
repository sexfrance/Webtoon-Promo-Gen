from get_key import get_key
from create_encpw import encrypt
import requests

def get_neo(email, password):
        json    = get_key()
        url     = "https://global.apis.naver.com/lineWebtoon/webtoon/loginById.json"
        payload = {
            "serviceZone": "GLOBAL",
            "encpw": encrypt(json, email, password),
            "loginType": "EMAIL",
            "v": "3",
            "language": "en",
            "encnm": json["keyName"]
        }
        ses =  requests.post(url, data=payload).json()["message"]["result"]["ses"]
        return ses

print(get_neo("ikwqlvuwzkfgcftozhhnujzjiz@mailnesia.com", "9ljs5kc35qch"))